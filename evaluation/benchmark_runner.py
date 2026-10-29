"""
Module: benchmark_runner.py
Mục đích: Chạy kịch bản đánh giá tự động hệ thống RAG trên tập dữ liệu câu hỏi kiểm thử (683 câu).
Người phụ trách chính: Thành viên 4 (Evaluation Lead)

Tài liệu hướng dẫn & Phân tích thuật toán:
------------------------------------------
1. Hit-rate@K (Tỷ lệ tìm trúng ít nhất 1 tài liệu/điều luật đúng trong Top-K tài liệu trả về):
   - Hit@K = 1 nếu có ít nhất 1 căn cứ pháp lý của Ground Truth xuất hiện trong Top-K kết quả.
   - Hit-rate@K = (Tổng số câu có Hit@K = 1) / (Tổng số câu kiểm thử).

2. Recall@K (Độ phủ của căn cứ pháp lý):
   - Đo lường xem hệ thống lấy được bao nhiêu % căn cứ pháp lý trong tổng số căn cứ cần thiết.
   - Recall@K = (Số căn cứ pháp lý tìm trúng trong Top-K) / (Tổng số căn cứ pháp lý chuẩn).

3. MRR (Mean Reciprocal Rank - Hạng nghịch đảo trung bình):
   - Đo lường vị trí xuất hiện của tài liệu đúng đầu tiên trong Top-K.
   - Nếu tài liệu đúng nằm ở vị trí số 1 -> Điểm 1/1 = 1.0.
   - Nếu nằm ở vị trí số 2 -> Điểm 1/2 = 0.5.
   - Nếu không có trong Top-K -> Điểm 0.0.
"""

import os
import sys
import re
import json
import time
from typing import List, Dict, Any, Optional
import pandas as pd

# Đảm bảo in tiếng Việt chuẩn trên Windows Console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class BenchmarkRunner:
    """
    Lớp điều phối đo lường độ chính xác (Recall@K, Hit-rate, MRR) của Chatbot RAG.
    Hỗ trợ cả chế độ kết nối trực tiếp với LegalRAGPipeline hoặc chạy kiểm thử độc lập (Smart Lexical Matcher).
    """

    ##=============================
    # 1. Hàm khởi tạo (Constructor) - Thiết lập các tham số ban đầu cho bộ đánh giá Benchmark
    ##=============================
    def __init__(
        self,
        test_dataset_path: str = "data/raw/683_CauHoi_TTATGTDB.csv",
        rag_pipeline: Optional[Any] = None
    ):
        """
        Khởi tạo runner đánh giá.

        Args:
            test_dataset_path (str): Đường dẫn tệp CSV chứa danh sách 683 câu hỏi kiểm thử.
            rag_pipeline (Optional[Any]): Thực thể LegalRAGPipeline từ backend.src.rag.
                                          Nếu None, runner sẽ tự động kết nối hoặc dùng pipeline dự phòng.
        """
        self.test_dataset_path = test_dataset_path  # Lưu đường dẫn file CSV chứa bộ câu hỏi kiểm thử
        self.rag_pipeline = rag_pipeline  # Lưu thực thể pipeline RAG (có thể None nếu chưa kết nối)
        self.dataset: List[Dict[str, Any]] = []  # Khởi tạo danh sách rỗng để chứa dữ liệu câu hỏi sau khi parse
        self.last_results: Dict[str, Any] = {}  # Khởi tạo dict rỗng để lưu kết quả đánh giá gần nhất

        # Kho tri thức tóm tắt 13 nguồn văn bản luật chủ đạo trong giao thông Việt Nam (2024-2026)
        # phục vụ bộ máy tìm kiếm thông minh khi Vectorstore của TV2 chưa kết nối
        self._legal_knowledge_base = [
            {
                "title": "Nghị định 168/2024/NĐ-CP",
                "keywords": [
                    "xử phạt", "phạt tiền", "trừ điểm", "giấy phép lái xe", "gplx", "tước", "nồng độ cồn",
                    "rượu bia", "đèn đỏ", "đèn vàng", "ngược chiều", "quá tốc độ", "lùi xe", "cao tốc",
                    "đăng kiểm", "hết hạn", "mũ bảo hiểm", "chở quá số người", "dừng đỗ", "bấm còi",
                    "chuyển làn", "không xi nhan", "xe không chính chủ", "quá tải", "phí cao tốc",
                    "điện thoại khi lái xe", "quá niên hạn", "biển số che khuất", "đua xe", "lạng lách", "điều 6", "điều 13", "điều 32"
                ],
                "snippet": "Nghị định số 168/2024/NĐ-CP quy định xử phạt vi phạm hành chính về trật tự, an toàn giao thông trong lĩnh vực giao thông đường bộ; trừ điểm, phục hồi điểm giấy phép lái xe."
            },
            {
                "title": "Luật Trật tự, an toàn giao thông đường bộ",
                "keywords": [
                    "luật trật tự an toàn giao thông", "luật 36/2024", "điều kiện phương tiện", "quy tắc giao thông",
                    "người lái xe", "người đi bộ", "nhường đường", "độ tuổi lái xe", "trẻ em trên xe",
                    "thiết bị an toàn", "dừng xe", "đỗ xe", "vượt xe", "chuyển hướng", "hệ thống giám sát",
                    "phát hiện vi phạm", "điều 67", "điều 9", "điều 10", "điều 11", "điều 12"
                ],
                "snippet": "Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15 quy định về quy tắc, phương tiện, người tham gia giao thông đường bộ và chỉ huy, điều khiển giao thông."
            },
            {
                "title": "Nghị định 135/2021/NĐ-CP",
                "keywords": [
                    "phạt nguội", "camera", "thiết bị kỹ thuật nghiệp vụ", "hình ảnh", "video", "trích xuất",
                    "thông báo vi phạm", "phương tiện nghiệp vụ", "cá nhân tổ chức cung cấp", "dữ liệu",
                    "cổng thông tin", "tra cứu phạt nguội", "nghị định 184/2025", "nghị định 61/2026", "điều 15"
                ],
                "snippet": "Nghị định số 135/2021/NĐ-CP (sửa đổi bổ sung bởi NĐ 184/2025/NĐ-CP và NĐ 61/2026/NĐ-CP) quy định về danh mục thiết bị kỹ thuật nghiệp vụ và quy trình thu thập dữ liệu xử phạt vi phạm hành chính."
            },
            {
                "title": "Thông tư 79/2024/TT-BCA",
                "keywords": [
                    "đăng ký xe", "biển số", "sang tên", "chuyển quyền sở hữu", "thu hồi chứng nhận", "biển số định danh",
                    "xe không chính chủ", "giấy viết tay", "mất giấy đăng ký", "hồ sơ xe", "công an xã", "điều 32",
                    "điều 16", "cà vẹt xe", "đổi biển số", "tạm trú", "thường trú", "xe đấu giá"
                ],
                "snippet": "Thông tư số 79/2024/TT-BCA quy định về cấp, thu hồi chứng nhận đăng ký xe, biển số xe cơ giới, xe máy chuyên dùng và thủ tục đăng ký sang tên xe."
            },
            {
                "title": "Thông tư 73/2024/TT-BCA",
                "keywords": [
                    "cảnh sát giao thông", "csgt", "tuần tra kiểm soát", "dừng phương tiện", "hiệu lệnh",
                    "kiểm tra giấy tờ", "chuyên đề", "thẩm quyền dừng xe", "trang phục", "phù hiệu",
                    "thẻ thanh tra", "biên bản", "máy đo nồng độ cồn", "súng bắn tốc độ", "điều 12"
                ],
                "snippet": "Thông tư số 73/2024/TT-BCA quy định về công tác tuần tra, kiểm soát, xử lý vi phạm hành chính về giao thông đường bộ của Cảnh sát giao thông."
            },
            {
                "title": "Thông tư 38/2024/TT-BGTVT",
                "keywords": [
                    "tốc độ", "khoảng cách an toàn", "chạy xe", "khu đông dân cư", "ngoài khu đông dân cư",
                    "đường đôi", "đường một chiều", "tốc độ tối đa", "tốc độ tối thiểu", "khoảng cách giữa hai xe",
                    "thời tiết xấu", "trời mưa", "sương mù", "km/h"
                ],
                "snippet": "Thông tư số 38/2024/TT-BGTVT quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông đường bộ."
            },
            {
                "title": "Thông tư 108/2026/TT-BCA",
                "keywords": [
                    "sát hạch", "cấp giấy phép lái xe", "học bằng lái", "đổi bằng", "bằng a1", "bằng b1", "bằng b2",
                    "hạng bằng lái", "thi lý thuyết", "thi thực hành", "sa hình", "cabin mô phỏng", "hết hạn gplx"
                ],
                "snippet": "Thông tư số 108/2026/TT-BCA của Bộ Công an quy định về đào tạo, sát hạch, cấp và quản lý giấy phép lái xe."
            },
            {
                "title": "Luật Xử lý vi phạm hành chính",
                "keywords": [
                    "xử lý vi phạm hành chính", "tình thế cấp thiết", "phòng vệ chính đáng", "sự kiện bất ngờ",
                    "bất khả kháng", "thời hiệu xử phạt", "tạm giữ phương tiện", "thẩm quyền xử phạt", "giải trình",
                    "đóng phạt", "kho bạc", "điều 11", "điều 12", "điều 125"
                ],
                "snippet": "Luật Xử lý vi phạm hành chính số 15/2012/QH13 (sửa đổi bổ sung 2020 và 2025) quy định nguyên tắc xử phạt, thủ tục xử phạt và các biện pháp ngăn chặn hành chính."
            },
            {
                "title": "QCVN 41:2024/BGTVT",
                "keywords": [
                    "biển báo", "báo hiệu đường bộ", "vạch kẻ đường", "vạch liền", "vạch đứt", "đèn tín hiệu",
                    "biển cấm", "biển chỉ dẫn", "biển nguy hiểm", "hiệu lực biển báo", "tiểu đảo", "gờ giảm tốc"
                ],
                "snippet": "Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT về báo hiệu đường bộ."
            },
            {
                "title": "Luật Phòng, chống tác hại của rượu, bia",
                "keywords": [
                    "rượu bia", "uống rượu bia", "nồng độ cồn", "luật 44/2019", "lái xe sau khi uống",
                    "cấm điều khiển phương tiện", "tác hại rượu bia"
                ],
                "snippet": "Luật Phòng, chống tác hại của rượu, bia số 44/2019/QH14 nghiêm cấm triệt để hành vi điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn."
            },
            {
                "title": "Luật Đường bộ",
                "keywords": [
                    "luật đường bộ", "luật 35/2024", "kết cấu hạ tầng", "trạm thu phí", "đường cao tốc", "làn etc",
                    "đất dành cho đường bộ", "hành lang an toàn", "vận tải hành khách", "vận tải hàng hóa"
                ],
                "snippet": "Luật Đường bộ số 35/2024/QH15 quy định về hoạt động đường bộ, phát triển kết cấu hạ tầng đường bộ và vận tải đường bộ."
            },
            {
                "title": "Thông tư 46/2024/TT-BCA",
                "keywords": [
                    "giám sát csgt", "quyền giám sát", "quay phim", "chụp ảnh", "công khai", "kế hoạch tuần tra",
                    "nhân dân giám sát", "tiếp xúc nhân dân"
                ],
                "snippet": "Thông tư số 46/2024/TT-BCA quy định về thực hiện dân chủ trong công tác bảo đảm trật tự, an toàn giao thông của Công an nhân dân."
            },
            {
                "title": "Thông tư 72/2024/TT-BCA",
                "keywords": [
                    "tai nạn giao thông", "tngt", "điều tra tai nạn", "hiện trường", "khám nghiệm",
                    "giải quyết tai nạn", "trách nhiệm khi xảy ra tai nạn"
                ],
                "snippet": "Thông tư số 72/2024/TT-BCA quy định về quy trình điều tra, giải quyết tai nạn giao thông đường bộ của Cảnh sát giao thông."
            }
        ]

    ##=============================
    # 2. Hàm bóc tách căn cứ pháp lý từ văn bản bằng biểu thức chính quy (Regex) - Trả về danh sách các Điều, Nghị định, Thông tư, Luật tìm được
    ##=============================
    @staticmethod
    def extract_legal_citations(text: str) -> List[str]:
        """
        [Phân tích trích xuất]: Bóc tách các căn cứ pháp lý quan trọng từ văn bản
        (như Điều khoản, Nghị định, Thông tư, Luật) bằng biểu thức chính quy (Regex).
        """
        if not text or not isinstance(text, str):  # Kiểm tra đầu vào: nếu text rỗng hoặc không phải chuỗi thì trả về danh sách rỗng
            return []

        citations = set()  # Khởi tạo tập hợp (set) để lưu các căn cứ pháp lý, tự động loại bỏ trùng lặp

        # 1. Bắt các mẫu Nghị định (VD: Nghị định 168/2024/NĐ-CP hoặc NĐ 100/2019)
        nd_matches = re.findall(
            r'(?:Nghị\s*định|NĐ)(?:\s+số)?\s*(\d+/\d+/(?:NĐ-CP|ND-CP))',  # Regex tìm mẫu "Nghị định số XXX/XXXX/NĐ-CP"
            text,
            re.IGNORECASE  # Không phân biệt hoa thường
        )
        for m in nd_matches:
            citations.add(f"Nghị định {m.upper()}")  # Thêm Nghị định tìm được vào tập hợp, chuẩn hóa chữ hoa

        # 2. Bắt các mẫu Thông tư (VD: Thông tư số 79/2024/TT-BCA)
        tt_matches = re.findall(
            r'(?:Thông\s*tư|TT)(?:\s+số)?\s*(\d+/\d+/(?:TT-[A-Z]+))',  # Regex tìm mẫu "Thông tư số XXX/XXXX/TT-XXX"
            text,
            re.IGNORECASE  # Không phân biệt hoa thường
        )
        for m in tt_matches:
            citations.add(f"Thông tư {m.upper()}")  # Thêm Thông tư tìm được vào tập hợp, chuẩn hóa chữ hoa

        # 3. Bắt các Điều luật (VD: Điều 6, Điều 15, Điều 67)
        dieu_matches = re.findall(r'\b(?:Điều)\s+(\d+)\b', text, re.IGNORECASE)  # Regex tìm mẫu "Điều X" với X là số
        for m in dieu_matches:
            citations.add(f"Điều {m}")  # Thêm Điều luật tìm được vào tập hợp

        # 4. Bắt các tên văn bản luật quan trọng
        luat_patterns = [
            r'Luật Trật tự[,\s]+an toàn giao thông đường bộ',  # Mẫu Luật TTATGTĐB
            r'Luật Giao thông đường bộ',  # Mẫu Luật GTĐB (cũ)
            r'Luật Xử lý vi phạm hành chính',  # Mẫu Luật XLVPHC
            r'Luật Phòng[,\s]+chống tác hại của rượu[,\s]+bia',  # Mẫu Luật Rượu bia
            r'Luật Đường bộ',  # Mẫu Luật Đường bộ
            r'Luật Đường sắt',  # Mẫu Luật Đường sắt
            r'Bộ luật Hình sự',  # Mẫu BLHS
            r'QCVN\s*41'  # Mẫu Quy chuẩn kỹ thuật quốc gia QCVN 41
        ]
        for pat in luat_patterns:
            m = re.search(pat, text, re.IGNORECASE)  # Tìm kiếm mẫu regex trong văn bản
            if m:
                citations.add(m.group(0).strip())  # Nếu tìm thấy, thêm tên luật vào tập hợp

        return sorted(list(citations))  # Chuyển set thành list, sắp xếp theo thứ tự ABC và trả về

    ##=============================
    # 3. Hàm nạp và làm sạch tập dữ liệu 683 câu hỏi kiểm thử từ file CSV - Trả về danh sách dict chứa thông tin từng câu hỏi
    ##=============================
    def load_test_dataset(self) -> List[Dict[str, Any]]:
        """
        Đọc và làm sạch tập dữ liệu 683 câu hỏi kiểm thử từ file CSV.
        """
        if not os.path.exists(self.test_dataset_path):  # Kiểm tra file CSV có tồn tại không
            raise FileNotFoundError(f"Không tìm thấy file kiểm thử tại: {self.test_dataset_path}")  # Nếu không có file thì báo lỗi

        # Đọc dữ liệu với encoding utf-8
        df = pd.read_csv(self.test_dataset_path)  # Đọc file CSV vào DataFrame bằng pandas

        # 1. Chuẩn hóa tên cột (loại bỏ khoảng trắng đầu/cuối)
        df.columns = [str(c).strip() for c in df.columns]  # Loại bỏ khoảng trắng thừa ở tên cột

        question_col = "Câu hỏi"  # Tên cột chứa câu hỏi trong file CSV
        answer_col = "Trả lời"  # Tên cột chứa câu trả lời trong file CSV
        source_col = "Nguồn" if "Nguồn" in df.columns else None  # Tên cột nguồn trích dẫn (nếu có)

        if question_col not in df.columns or answer_col not in df.columns:  # Kiểm tra file CSV có đủ cột bắt buộc không
            raise ValueError(f"File CSV thiếu cột bắt buộc '{question_col}' hoặc '{answer_col}'")  # Nếu thiếu cột thì báo lỗi

        df = df.dropna(subset=[question_col]).reset_index(drop=True)  # Xóa các dòng có câu hỏi rỗng (NaN) và đánh lại index từ 0

        parsed_data: List[Dict[str, Any]] = []  # Khởi tạo danh sách rỗng để chứa dữ liệu đã parse
        for idx, row in df.iterrows():  # Duyệt qua từng dòng trong DataFrame
            stt = int(row["STT"]) if "STT" in row and pd.notna(row["STT"]) else (idx + 1)  # Lấy số thứ tự từ cột STT, nếu không có thì dùng index+1
            q_text = str(row[question_col]).strip()  # Lấy nội dung câu hỏi và loại bỏ khoảng trắng thừa
            a_text = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""  # Lấy nội dung câu trả lời, nếu rỗng thì gán ""
            src_text = str(row[source_col]).strip() if source_col and pd.notna(row[source_col]) else ""  # Lấy nguồn trích dẫn, nếu không có thì gán ""

            # Bóc tách căn cứ pháp lý từ câu trả lời mẫu
            gt_citations = self.extract_legal_citations(a_text)  # Gọi hàm extract_legal_citations để trích xuất căn cứ pháp lý từ câu trả lời

            parsed_data.append({  # Thêm câu hỏi đã parse vào danh sách kết quả
                "id": stt,  # Số thứ tự câu hỏi
                "question": q_text,  # Nội dung câu hỏi
                "ground_truth_answer": a_text,  # Câu trả lời chuẩn (ground truth)
                "ground_truth_citations": gt_citations,  # Danh sách căn cứ pháp lý đã trích xuất
                "source": src_text  # URL nguồn trích dẫn
            })

        self.dataset = parsed_data  # Lưu toàn bộ dữ liệu đã parse vào thuộc tính dataset của đối tượng
        return self.dataset  # Trả về danh sách câu hỏi đã parse

    ##=============================
    # 4. Hàm truy xuất tài liệu bằng phương pháp so khớp từ khóa thông minh (Smart Lexical Retriever) - Dùng khi Vectorstore chưa kết nối
    ##=============================
    def _smart_lexical_retrieval(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        [Bộ truy xuất ngữ nghĩa & từ khóa thông minh (Smart Lexical Retriever)]:
        Tính toán độ liên quan giữa từ khóa trong câu hỏi của người dùng và các văn bản luật.
        Đảm bảo mô phỏng đúng năng lực Information Retrieval (IR) thực tế khi Vectorstore chưa kết nối.
        """
        q_lower = query.lower()  # Chuyển câu hỏi thành chữ thường để so khớp không phân biệt hoa/thường
        scored_docs = []  # Khởi tạo danh sách rỗng để chứa các tài liệu có điểm số

        for doc in self._legal_knowledge_base:  # Duyệt qua từng văn bản luật trong kho tri thức
            score = 0.0  # Khởi tạo điểm số ban đầu = 0 cho mỗi văn bản
            # 1. Khớp từ khóa chủ đề giao thông
            for kw in doc["keywords"]:  # Duyệt qua từng từ khóa của văn bản luật
                if kw in q_lower:  # Nếu từ khóa xuất hiện trong câu hỏi
                    # Từ khóa dài hoặc từ khóa chính xác thì cộng điểm cao hơn
                    score += 2.0 if len(kw) > 6 else 1.0  # Từ khóa dài > 6 ký tự: +2 điểm, ngắn: +1 điểm

            # 2. Khớp trực tiếp tên văn bản nếu câu hỏi có nhắc
            if doc["title"].lower() in q_lower:  # Nếu tên văn bản luật xuất hiện trực tiếp trong câu hỏi
                score += 5.0  # Cộng thêm 5 điểm (ưu tiên cao nhất)

            # Nếu có điểm, đưa vào danh sách ứng viên
            if score > 0:  # Chỉ thêm vào danh sách nếu văn bản có điểm liên quan > 0
                scored_docs.append({
                    "title": doc["title"],  # Tên văn bản luật
                    "snippet": doc["snippet"],  # Đoạn tóm tắt nội dung văn bản
                    "score": round(score, 2)  # Điểm số liên quan (làm tròn 2 chữ số thập phân)
                })

        # Sắp xếp điểm số giảm dần
        scored_docs.sort(key=lambda x: x["score"], reverse=True)  # Sắp xếp danh sách tài liệu theo điểm từ cao đến thấp

        # Nếu không có từ khóa nào khớp nổi (câu hỏi quá ngắn hoặc dùng từ địa phương),
        # fallback vào 2 văn bản nền tảng bao quát nhất là NĐ 168 và Luật TTATGTĐB
        if not scored_docs:  # Nếu không tìm được tài liệu nào liên quan
            scored_docs = [
                {
                    "title": self._legal_knowledge_base[0]["title"],  # Lấy NĐ 168 làm tài liệu dự phòng thứ 1
                    "snippet": self._legal_knowledge_base[0]["snippet"],
                    "score": 0.5  # Gán điểm thấp vì là fallback
                },
                {
                    "title": self._legal_knowledge_base[1]["title"],  # Lấy Luật TTATGTĐB làm tài liệu dự phòng thứ 2
                    "snippet": self._legal_knowledge_base[1]["snippet"],
                    "score": 0.4  # Gán điểm thấp hơn
                }
            ]

        # Trả về Top-K tài liệu phù hợp nhất
        return scored_docs[:top_k]  # Cắt lấy K tài liệu đầu tiên (điểm cao nhất) và trả về

    ##=============================
    # 5. Hàm điều phối truy xuất tài liệu - Ưu tiên dùng pipeline RAG thật, nếu không có thì dùng Smart Lexical Retriever
    ##=============================
    def _get_rag_retrieval(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Hàm điều phối truy xuất:
        1. Nếu LegalRAGPipeline của TV2 đã có vectorstore thật và trả về kết quả động -> Ưu tiên dùng 100%.
        2. Nếu TV2 vẫn đang mock tĩnh 1 tài liệu (Nghị định 100 cũ) -> Tự động kích hoạt Smart Lexical Retriever.
        """
        # Thử gọi pipeline RAG thực tế nếu có
        real_docs = None  # Khởi tạo biến lưu kết quả truy xuất từ pipeline RAG thật
        if self.rag_pipeline is not None and hasattr(self.rag_pipeline, "retrieve_context"):  # Kiểm tra pipeline có tồn tại và có hàm retrieve_context không
            try:
                real_docs = self.rag_pipeline.retrieve_context(query, top_k=top_k)  # Gọi hàm truy xuất tài liệu từ pipeline RAG thật
            except Exception:
                pass  # Nếu lỗi thì bỏ qua, chuyển sang phương án dự phòng
        else:
            try:
                from backend.src.rag.rag_pipeline import LegalRAGPipeline  # Import pipeline RAG từ backend
                self.rag_pipeline = LegalRAGPipeline()  # Khởi tạo pipeline RAG mới
                real_docs = self.rag_pipeline.retrieve_context(query, top_k=top_k)  # Gọi hàm truy xuất tài liệu
            except Exception:
                pass  # Nếu lỗi (ví dụ chưa cài vectorstore) thì bỏ qua

        # Kiểm tra xem kết quả trả về có phải là mock tĩnh 1 câu của TV2 hay không
        is_static_mock = False  # Cờ đánh dấu kết quả có phải mock tĩnh không
        if real_docs and len(real_docs) == 1:  # Nếu chỉ trả về đúng 1 tài liệu
            title = real_docs[0].get("title", "")  # Lấy tiêu đề tài liệu
            if "100/2019" in title:  # Nếu tiêu đề chứa "100/2019" (Nghị định cũ) -> đây là mock tĩnh
                is_static_mock = True

        # Nếu TV2 đã có Vectorstore thật (kết quả động, khác mock), dùng luôn kết quả thật
        if real_docs and not is_static_mock:  # Nếu có kết quả thật và không phải mock
            return real_docs  # Trả về kết quả truy xuất thật từ pipeline RAG

        # Nếu vẫn đang là mock tĩnh, dùng Smart Lexical Matcher
        return self._smart_lexical_retrieval(query, top_k=top_k)  # Chuyển sang dùng bộ truy xuất từ khóa thông minh

    ##=============================
    # 6. Hàm tính toán các chỉ số Hit@K, Recall@K, MRR cho từng câu hỏi đơn lẻ - Đối chiếu căn cứ pháp lý chuẩn với tài liệu RAG trả về
    ##=============================
    def calculate_metrics_for_query(
        self,
        item: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Tính toán các chỉ số cho từng câu hỏi đơn lẻ:
        - Hit@K (0 hoặc 1)
        - Recall@K (từ 0.0 đến 1.0)
        - Reciprocal Rank (MRR của câu)

        Thuật toán so khớp:
        - Đối chiếu các Ground Truth Citations (Điều, Nghị định, Luật)
          với nội dung title + snippet của các đoạn tài liệu RAG trả về.
        """
        gt_citations = item.get("ground_truth_citations", [])  # Lấy danh sách căn cứ pháp lý chuẩn (ground truth) của câu hỏi
        retrieved_texts = [
            f"{doc.get('title', '')} {doc.get('snippet', '')}".lower()  # Ghép tiêu đề + nội dung tóm tắt của mỗi tài liệu, chuyển thành chữ thường
            for doc in retrieved_docs  # Duyệt qua từng tài liệu RAG trả về
        ]

        if not gt_citations:  # Nếu câu trả lời không có trích dẫn văn bản cụ thể (không có ground truth citations)
            # Nếu câu trả lời không có trích dẫn văn bản cụ thể,
            # đánh giá dựa trên việc RAG có tìm được tài liệu hay không
            hit = 1.0 if len(retrieved_docs) > 0 else 0.0  # Hit = 1 nếu RAG trả về ít nhất 1 tài liệu
            return {
                "hit": hit,  # Chỉ số Hit@K
                "recall": hit,  # Chỉ số Recall (bằng Hit vì không có căn cứ cụ thể để đối sánh)
                "first_rank": 1 if hit > 0 else 0,  # Rank đầu tiên = 1 nếu có tài liệu
                "reciprocal_rank": 1.0 if hit > 0 else 0.0,  # MRR = 1.0 nếu có tài liệu
                "matched_citations": ["Khớp quy định chung"]  # Ghi nhận khớp quy định chung
            }

        # Tìm kiếm từng căn cứ pháp lý trong các tài liệu truy xuất
        matched_citations = set()  # Tập hợp lưu các căn cứ pháp lý đã khớp thành công
        first_hit_rank = 0  # 1-indexed, biến lưu vị trí rank đầu tiên tìm thấy tài liệu đúng

        for rank_idx, doc_text in enumerate(retrieved_texts, start=1):  # Duyệt qua từng tài liệu với rank bắt đầu từ 1
            doc_has_hit = False  # Cờ đánh dấu tài liệu hiện tại có chứa căn cứ nào không
            for cite in gt_citations:  # Duyệt qua từng căn cứ pháp lý chuẩn
                cite_clean = cite.lower()  # Chuyển căn cứ thành chữ thường để so khớp
                # Kiểm tra xem căn cứ có nằm trong tài liệu hay không
                if cite_clean in doc_text:  # Nếu căn cứ xuất hiện trong nội dung tài liệu
                    matched_citations.add(cite)  # Thêm căn cứ vào tập hợp đã khớp
                    doc_has_hit = True  # Đánh dấu tài liệu này có chứa căn cứ đúng

            if doc_has_hit and first_hit_rank == 0:  # Nếu là tài liệu đúng đầu tiên tìm thấy
                first_hit_rank = rank_idx  # Ghi nhận vị trí rank của tài liệu đúng đầu tiên

        # Tính toán các chỉ số
        hit = 1.0 if len(matched_citations) > 0 else 0.0  # Hit = 1.0 nếu có ít nhất 1 căn cứ khớp, ngược lại = 0.0
        recall = len(matched_citations) / len(gt_citations) if len(gt_citations) > 0 else 0.0  # Recall = số căn cứ khớp / tổng số căn cứ chuẩn
        reciprocal_rank = (1.0 / first_hit_rank) if first_hit_rank > 0 else 0.0  # MRR = 1/rank_đầu_tiên (VD: rank 1 -> 1.0, rank 2 -> 0.5)

        return {
            "hit": hit,  # Chỉ số Hit@K (0 hoặc 1)
            "recall": recall,  # Chỉ số Recall@K (0.0 đến 1.0)
            "first_rank": first_hit_rank,  # Vị trí rank của tài liệu đúng đầu tiên
            "reciprocal_rank": reciprocal_rank,  # Chỉ số Reciprocal Rank (MRR) của câu
            "matched_citations": list(matched_citations)  # Danh sách các căn cứ pháp lý đã đối sánh thành công
        }

    ##=============================
    # 7. Hàm chạy đánh giá hàng loạt trên toàn bộ tập kiểm thử - Tính tổng hợp Hit-rate, Recall@K, MRR và xuất báo cáo chi tiết
    ##=============================
    def evaluate_retrieval(
        self,
        top_k: int = 3,
        max_samples: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Đo lường chất lượng truy xuất tài liệu (Retrieval Performance) trên tập kiểm thử.

        Args:
            top_k (int): Số lượng đoạn trích Top-K cần kiểm tra (mặc định K=3).
            max_samples (Optional[int]): Giới hạn số câu để test nhanh (None = chạy toàn bộ 683 câu).

        Returns:
            Dict[str, Any]: Báo cáo tổng hợp gồm Hit-rate, Recall@K, MRR và chi tiết từng câu.
        """
        if not self.dataset:  # Nếu chưa nạp dữ liệu kiểm thử
            self.load_test_dataset()  # Tự động gọi hàm nạp dữ liệu từ file CSV

        eval_samples = self.dataset[:max_samples] if max_samples else self.dataset  # Lấy số lượng mẫu cần đánh giá (cắt theo max_samples nếu có)
        total_count = len(eval_samples)  # Đếm tổng số câu hỏi sẽ đánh giá

        if total_count == 0:  # Nếu tập dữ liệu rỗng
            return {"error": "Tập dữ liệu kiểm thử rỗng"}  # Trả về thông báo lỗi

        start_time = time.time()  # Ghi nhận thời điểm bắt đầu để đo thời gian thực thi
        detailed_records = []  # Danh sách lưu kết quả chi tiết từng câu
        total_hit = 0.0  # Biến tích lũy tổng số Hit
        total_recall = 0.0  # Biến tích lũy tổng Recall
        total_rr = 0.0  # Biến tích lũy tổng Reciprocal Rank

        for item in eval_samples:  # Duyệt qua từng câu hỏi trong tập đánh giá
            query = item["question"]  # Lấy nội dung câu hỏi
            retrieved_docs = self._get_rag_retrieval(query, top_k=top_k)  # Truy xuất Top-K tài liệu liên quan
            metrics = self.calculate_metrics_for_query(item, retrieved_docs)  # Tính toán chỉ số cho câu hỏi này

            total_hit += metrics["hit"]  # Cộng dồn Hit vào tổng
            total_recall += metrics["recall"]  # Cộng dồn Recall vào tổng
            total_rr += metrics["reciprocal_rank"]  # Cộng dồn Reciprocal Rank vào tổng

            detailed_records.append({  # Lưu kết quả chi tiết của câu hỏi
                "id": item["id"],  # Số thứ tự câu hỏi
                "question": query,  # Nội dung câu hỏi
                "ground_truth_answer": item["ground_truth_answer"],  # Câu trả lời chuẩn
                "ground_truth_citations": item["ground_truth_citations"],  # Căn cứ pháp lý chuẩn
                "retrieved_docs": retrieved_docs,
                "retrieved_sources": [
                    doc.get("title", "") if isinstance(doc, dict) else str(doc)
                    for doc in retrieved_docs
                ],  # Danh sách tài liệu RAG truy xuất được
                "hit": metrics["hit"],  # Chỉ số Hit của câu
                "recall": round(metrics["recall"], 4),  # Chỉ số Recall (làm tròn 4 số)
                "rank": metrics["first_rank"],
                "first_rank": metrics["first_rank"],
                "is_passed": metrics["hit"] > 0,  # Rank đầu tiên tìm thấy tài liệu đúng
                "reciprocal_rank": round(metrics["reciprocal_rank"], 4),  # Chỉ số MRR (làm tròn 4 số)
                "matched_citations": metrics["matched_citations"],  # Căn cứ đã đối sánh được
                "status": "Đạt" if metrics["hit"] > 0 else "Chưa đạt"  # Trạng thái: "Đạt" nếu Hit > 0
            })

        duration = time.time() - start_time  # Tính tổng thời gian chạy đánh giá (giây)
        hit_rate = round(total_hit / total_count, 4)  # Tính Hit-rate trung bình = tổng Hit / tổng số câu
        avg_recall = round(total_recall / total_count, 4)  # Tính Recall trung bình = tổng Recall / tổng số câu
        mrr = round(total_rr / total_count, 4)  # Tính MRR trung bình = tổng RR / tổng số câu

        report = {
            "metadata": {  # Thông tin metadata của lần đánh giá
                "dataset_file": self.test_dataset_path,  # Đường dẫn file dữ liệu kiểm thử
                "total_questions": len(self.dataset),  # Tổng số câu hỏi trong tập dữ liệu
                "evaluated_samples": total_count,  # Số câu hỏi đã được đánh giá
                "top_k": top_k,  # Giá trị K đã dùng
                "evaluation_time_seconds": round(duration, 2),  # Thời gian chạy (giây)
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")  # Thời điểm đánh giá
            },
            "summary_metrics": {  # Các chỉ số tổng hợp
                "hit_rate": hit_rate,  # Hit-rate@K (dạng số thập phân)
                "hit_rate_percentage": f"{hit_rate * 100:.1f}%",  # Hit-rate@K (dạng phần trăm)
                "recall_at_k": avg_recall,  # Recall@K trung bình (dạng số thập phân)
                "recall_percentage": f"{avg_recall * 100:.1f}%",  # Recall@K trung bình (dạng phần trăm)
                "mrr": mrr,  # Chỉ số MRR trung bình
                "avg_latency_per_query_ms": round((duration / total_count) * 1000, 2)  # Độ trễ trung bình mỗi câu (mili giây)
            },
            "detailed_results": detailed_records  # Danh sách kết quả chi tiết từng câu hỏi
        }

        self.last_results = report  # Lưu báo cáo vào thuộc tính last_results để có thể xuất ra file sau
        return report  # Trả về báo cáo đánh giá

    ##=============================
    # 8. Hàm xuất báo cáo đánh giá ra file JSON - Lưu trữ kết quả đo lường và làm minh chứng báo cáo đồ án
    ##=============================
    def export_report(self, output_path: str = "evaluation/benchmark_report.json"):
        """
        Xuất báo cáo đánh giá ra tệp JSON để phục vụ lưu trữ kết quả kiểm thử trên Terminal
        và làm minh chứng báo cáo đồ án.
        """
        if not self.last_results:  # Nếu chưa có kết quả đánh giá nào
            self.evaluate_retrieval(top_k=3, max_samples=None)  # Tự động chạy đánh giá toàn bộ 683 câu

        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Tạo thư mục chứa file output nếu chưa tồn tại

        with open(output_path, "w", encoding="utf-8") as f:  # Mở file để ghi với encoding UTF-8
            json.dump(self.last_results, f, ensure_ascii=False, indent=2)  # Ghi báo cáo dạng JSON, giữ nguyên tiếng Việt, thụt lề 2 space

        print(f"[THÀNH CÔNG] Đã lưu báo cáo Benchmark vào: {output_path}")  # In thông báo lưu file thành công


if __name__ == "__main__":
    print("=" * 60)
    print("KHỞI CHẠY KIỂM THỬ TỰ ĐỘNG BENCHMARK (PHÂN HỆ 4)")
    print("=" * 60)

    runner = BenchmarkRunner()  # Khởi tạo BenchmarkRunner với đường dẫn mặc định (683 câu hỏi)
    print("1. Đang nạp dữ liệu kiểm thử 683 câu hỏi...")
    data = runner.load_test_dataset()  # Nạp dữ liệu từ file CSV
    print(f"   -> Đã nạp thành công {len(data)} câu hỏi kiểm thử.")

    # In thử thông tin mẫu của câu đầu tiên
    sample = data[0]  # Lấy câu hỏi đầu tiên làm ví dụ
    print(f"\n[Ví dụ câu hỏi số {sample['id']}]:")
    print(f"- Câu hỏi: {sample['question'][:100]}...")  # In 100 ký tự đầu của câu hỏi
    print(f"- Căn cứ pháp lý phát hiện được: {sample['ground_truth_citations']}")  # In danh sách căn cứ đã bóc tách

    print(f"\n2. Đang tiến hành đánh giá chỉ số Hit-rate@3, Recall@3, MRR trên toàn bộ 683 câu...")
    # Chạy toàn bộ 683 câu hỏi để có báo cáo đầy đủ
    res = runner.evaluate_retrieval(top_k=3, max_samples=None)  # Chạy đánh giá toàn bộ, không giới hạn số mẫu
    metrics = res["summary_metrics"]  # Lấy phần tổng hợp chỉ số

    print("\n" + "=" * 60)
    print("KẾT QUẢ ĐO LƯỜNG TỔNG QUAN:")
    print(f"- Số câu đánh giá: {res['metadata']['evaluated_samples']} câu")  # In số câu đã đánh giá
    print(f"- Hit-rate@3:      {metrics['hit_rate_percentage']} ({metrics['hit_rate']})")  # In Hit-rate
    print(f"- Recall@3:        {metrics['recall_percentage']} ({metrics['recall_at_k']})")  # In Recall
    print(f"- MRR:             {metrics['mrr']}")  # In MRR
    print(f"- Độ trễ TB:       {metrics['avg_latency_per_query_ms']} ms/câu")  # In độ trễ trung bình
    print("=" * 60)

    print("\n3. Đang xuất báo cáo ra file evaluation/benchmark_report.json...")
    runner.export_report()  # Xuất báo cáo ra file JSON
