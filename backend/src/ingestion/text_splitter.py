"""
Module: text_splitter.py
Mục đích: Phân chia văn bản pháp luật thành các đoạn nhỏ (chunks) theo cấu trúc Điều/Khoản.
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead)
"""

from typing import List, Dict, Any, Optional
import re
import json
import logging
from pathlib import Path

try:
    from backend.src.utils.text_cleaner import TextCleaner
except ModuleNotFoundError:
    import sys
    # Tự động thêm thư mục gốc dự án vào sys.path khi chạy script độc lập
    project_root = str(Path(__file__).resolve().parents[3])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from backend.src.utils.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

# Bảng ánh xạ tên file thô sang tên văn bản pháp luật chính thức đầy đủ bằng tiếng Việt
LAW_NAME_MAPPING: Dict[str, str] = {
    "1.1_VBHN_LuatTTATGTDB_36.2024.QH15.docx": "Luật Trật tự, an toàn giao thông đường bộ 2024 (Luật số 36/2024/QH15)",
    "1.2_VBHN_LuatHinhSu_100.2015.QH13.docx": "Bộ luật Hình sự 2015 (sửa đổi, bổ sung 2017)",
    "1.3_LuatDanSu_91.2015.QH13.docx": "Bộ luật Dân sự 2015 (Luật số 91/2015/QH13)",
    "1.4_VBHN_LuatXuLyVPHC_15.2012.QH13.docx": "Luật Xử lý vi phạm hành chính (Văn bản hợp nhất số 20/VBHN-VPQH)",
    "1.5_RuouBia_44.2019.QH14.docx": "Luật Phòng, chống tác hại của rượu, bia 2019 (Luật số 44/2019/QH14)",
    "1.6_LuatDuongBo_35.2024.QH15.docx": "Luật Đường bộ 2024 (Luật số 35/2024/QH15)",
    "1.7_LuatDuongSat_95.2025.QH15.docx": "Luật Đường sắt 2025 (Luật số 95/2025/QH15)",
    "1.8_LuatDoLuong_04.2011.QH13.docx": "Luật Đo lường 2011 (Luật số 04/2011/QH13)",
    "1.9_VBHN_LuatCanhVe_13.2017.QH14.docx": "Luật Cảnh vệ (Văn bản hợp nhất)",
    "2.1_VBHN_VPHC-ATGT_168.2024.ND.CP.docx": "Nghị định 168/2024/NĐ-CP (Xử phạt VPHC về trật tự, ATGT đường bộ; trừ điểm GPLX)",
    "2.2_PhatNguoi_61.2026.NĐ.CP.docx": "Nghị định 61/2026/NĐ-CP (Thiết bị kỹ thuật nghiệp vụ và xử phạt nguội)",
    "2.3_AnNinhTratTu_282.2025.ND.CP.docx": "Nghị định 282/2025/NĐ-CP (Xử phạt VPHC an ninh, trật tự, an toàn xã hội)",
    "2.4_VPHC_HoatDongDuongBo_336.2025.ND.CP.docx": "Nghị định 336/2025/NĐ-CP (Xử phạt VPHC trong hoạt động đường bộ)",
    "2.5_VPHC_DuongSat_81.2026.ND.CP.docx": "Nghị định 81/2026/NĐ-CP (Xử phạt VPHC trong lĩnh vực giao thông đường sắt)",
    "2.6_VBHN_KDVTDNDuongBo_58.2026.VBHN.BXD.docx": "Nghị định 158/2024/NĐ-CP (Quy định về hoạt động vận tải đường bộ)",
    "3.1_VBHN_CSGT_73.2024.TT.BCA.docx": "Thông tư 73/2024/TT-BCA (Quy định tuần tra, kiểm soát, xử lý vi phạm của CSGT)",
    "3.2_VBHN_DangKyXe_79.2024.TT.BCA.docx": "Thông tư 79/2024/TT-BCA (Quy định cấp, thu hồi đăng ký, biển số xe cơ giới)",
    "3.3_SatHachCapGPLX_108.2026.TT.BCA.docx": "Thông tư 108/2026/TT-BCA (Quy định sát hạch, cấp giấy phép lái xe)",
    "3.4_TocDoVaKhoangCach_38.2024.TT.BGTVT.docx": "Thông tư 38/2024/TT-BGTVT (Quy định tốc độ và khoảng cách an toàn xe cơ giới)",
    "3.5_QCVN41_51.2024.TT.BGTVT.docx": "Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT (Báo hiệu đường bộ)",
    "3.6_VBHN_DieuTraTNGT_72.2024.TT.BCA.docx": "Thông tư 72/2024/TT-BCA (Quy trình điều tra, giải quyết tai nạn giao thông của CSGT)",
    "3.7_VBHN_Thong_Tu_67.2019.TT.BCA.docx": "Thông tư 67/2019/TT-BCA (Thực hiện dân chủ trong bảo đảm trật tự, ATGT)",
}


class LegalTextSplitter:
    """
    Lớp chia nhỏ văn bản pháp luật thành các đoạn thông tin phục vụ vector hóa.
    Đặc thù văn bản luật: Nên ưu tiên cắt theo 'Điều ...' hoặc 'Khoản ...' để giữ trọn vẹn ngữ nghĩa.
    """

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 150):
        """
        Khởi tạo bộ chia văn bản.
        Args:
            chunk_size (int): Độ dài ký tự tối đa cho mỗi đoạn văn bản (mặc định 1200).
            chunk_overlap (int): Độ dài ký tự gối đầu giữa các đoạn liền kề (mặc định 150).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @staticmethod
    def _extract_law_name(doc_metadata: Dict[str, Any]) -> str:
        """
        Trích xuất tên luật chính thức bằng tiếng Việt từ bảng ánh xạ LAW_NAME_MAPPING.
        Nếu không có trong bảng ánh xạ, tự động fallback chuẩn hóa từ tên file.
        """
        if "law_name" in doc_metadata and doc_metadata["law_name"]:
            return str(doc_metadata["law_name"])

        file_name = doc_metadata.get("file_name", "")
        if not file_name and "file_path" in doc_metadata:
            file_name = Path(doc_metadata["file_path"]).name

        # 1. Tra cứu trực tiếp từ bảng ánh xạ tên luật chính thức
        if file_name in LAW_NAME_MAPPING:
            return LAW_NAME_MAPPING[file_name]

        # 2. Fallback làm sạch nếu file mới chưa có trong bảng ánh xạ
        clean = re.sub(r"\.[^.]+$", "", file_name)
        clean = re.sub(r"^\d+[\.\d]*_*(?:VBHN_)?", "", clean)
        return clean or file_name or "Văn bản quy phạm pháp luật"

    @staticmethod
    def _slice_at_word_boundary(text: str, start: int, max_length: int) -> tuple:
        """
        Cắt chuỗi tại ranh giới từ (khoảng trắng hoặc xuống dòng) gần nhất,
        tránh chém ngang từ tiếng Việt. Có guard clause phòng vệ chống vòng lặp vô tận.
        Returns:
            tuple: (đoạn text đã cắt, vị trí start tiếp theo)
        """
        if start + max_length >= len(text):
            return text[start:].strip(), len(text)

        target_end = start + max_length
        sp = text.rfind(" ", start, target_end)
        nl = text.rfind("\n", start, target_end)
        split_pos = max(sp, nl)

        # Chỉ ngắt tại khoảng trắng/xuống dòng nếu tiến về phía trước ít nhất 50% max_length
        # để đảm bảo các đoạn không bị quá vụn
        if split_pos > start + (max_length // 2):
            return text[start:split_pos].strip(), split_pos + 1

        # Fallback an toàn: nếu không có khoảng trắng hợp lệ, ngắt cứng tại target_end
        return text[start:target_end].strip(), target_end

    def _split_long_article(self, article_text: str, header: str) -> List[str]:
        """
        Chia nhỏ một Điều luật dài thành các đoạn nhỏ hơn theo Khoản hoặc đoạn văn.
        - Gắn tiêu đề Điều vào Khoản 1, không bao giờ bỏ rơi tiêu đề thành chunk rác riêng.
        - Luôn chèn tiền tố header cho mọi đoạn con từ đoạn thứ 2 trở đi.
        - Ngắt từ tròn trịa tại khoảng trắng, không cắt đôi từ tiếng Việt.
        """
        if len(article_text) <= self.chunk_size:
            return [article_text]

        prefix = f"[{header} (tiếp theo)]\n" if header else ""
        chunks: List[str] = []

        # Tách theo ranh giới từng Khoản (ví dụ: "1. ", "2. ")
        clauses = re.split(r"(?m)(?=^\s*\d+\.\s+)", article_text)

        if len(clauses) > 1:
            # Gắn tiêu đề Điều (clauses[0]) vào Khoản 1 (clauses[1]) để tiêu đề không bị xé lẻ
            first_clause = (clauses[0].strip() + "\n" + clauses[1].strip()).strip()
            items = [first_clause] + [c.strip() for c in clauses[2:] if c.strip()]
        else:
            items = [p.strip() for p in article_text.split("\n") if p.strip()]

        cur_chunk = ""
        for item in items:
            # Tính toán không gian khả dụng trong chunk hiện tại
            pfx = prefix if (chunks or cur_chunk) else ""
            available_size = self.chunk_size - len(pfx)

            # Trường hợp 1: Bản thân một Khoản/đoạn vượt quá kích thước chunk
            if len(item) > available_size:
                if cur_chunk:
                    chunks.append(cur_chunk)
                    cur_chunk = ""

                start = 0
                while start < len(item):
                    current_pfx = prefix if chunks else ""
                    max_len = max(1, self.chunk_size - len(current_pfx))
                    seg, next_start = self._slice_at_word_boundary(item, start, max_len)

                    if seg:
                        # Nếu đoạn cuối quá ngắn (<100 ký tự) và đã có chunk trước đó, gộp vào chunk trước
                        if len(seg) < 100 and chunks and (len(chunks[-1]) + len(seg) + 1 <= self.chunk_size + 150):
                            chunks[-1] = chunks[-1] + " " + seg
                        else:
                            final_seg = current_pfx + seg if current_pfx and not seg.startswith(current_pfx) else seg
                            chunks.append(final_seg)

                    # Guard clause chống vòng lặp vô tận
                    if next_start <= start:
                        break
                    start = next_start
                continue

            # Trường hợp 2: Khoản có thể gộp vào chunk hiện tại
            current_pfx = prefix if (chunks and not cur_chunk) else ""
            needed_len = len(cur_chunk) + (1 if cur_chunk else 0) + len(current_pfx) + len(item)

            if needed_len <= self.chunk_size:
                if cur_chunk:
                    cur_chunk = cur_chunk + "\n" + item
                else:
                    cur_chunk = (current_pfx + item).strip()
            else:
                if cur_chunk:
                    chunks.append(cur_chunk)
                current_pfx = prefix if chunks else ""
                cur_chunk = (current_pfx + item).strip()

        if cur_chunk:
            chunks.append(cur_chunk)

        return chunks

    def split_by_article(self, text: str, doc_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Cắt văn bản theo ranh giới từng 'Điều' (Ví dụ: Điều 1, Điều 2...).
        Args:
            text (str): Toàn bộ nội dung văn bản luật.
            doc_metadata (Dict[str, Any]): Thông tin về văn bản (tên luật, số hiệu).
        Returns:
            List[Dict[str, Any]]: Danh sách các chunks kèm metadata điều khoản.
        """
        chunks: List[Dict[str, Any]] = []
        if not text or not text.strip():
            return chunks

        law_name = self._extract_law_name(doc_metadata)

        # Nhận diện ranh giới từng Điều bằng Positive Lookahead Multiline Regex
        pattern = r"(?m)(?=^\s*Điều\s+\d+[\.:\s])"
        parts = re.split(pattern, text)

        for idx, part in enumerate(parts):
            part_str = part.strip()
            if not part_str:
                continue

            # Phần 0 (trước Điều 1) là Lời nói đầu / Căn cứ pháp lý
            if idx == 0 and not re.match(r"^\s*Điều\s+\d+[\.:\s]", part_str):
                preamble_subparts = self._split_long_article(
                    part_str, header="Lời nói đầu & Căn cứ ban hành"
                )
                for sub in preamble_subparts:
                    chunk_item = {
                        "chunk_text": sub,
                        "law_name": law_name,
                        "article_number": None,
                        "article_title": "Lời nói đầu & Căn cứ ban hành",
                    }
                    for k, v in doc_metadata.items():
                        if k not in chunk_item:
                            chunk_item[k] = v
                    chunks.append(chunk_item)
                continue

            # Các Điều luật chính thức
            first_line = part_str.split("\n", 1)[0].strip()
            art_num = TextCleaner.extract_article_number(first_line)

            match = re.search(r"Điều\s+\d+[\.:\s]\s*(.*)", first_line)
            art_title = match.group(1).strip() if match else first_line

            sub_chunks = self._split_long_article(part_str, header=first_line)

            for sub_text in sub_chunks:
                chunk_item = {
                    "chunk_text": sub_text,
                    "law_name": law_name,
                    "article_number": art_num,
                    "article_title": art_title,
                }
                for k, v in doc_metadata.items():
                    if k not in chunk_item:
                        chunk_item[k] = v
                chunks.append(chunk_item)

        return chunks

    def split_into_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Nhận danh sách tài liệu từ document_loader và phân mảnh toàn bộ.
        Args:
            documents (List[Dict[str, Any]]): Danh sách tài liệu thô.
        Returns:
            List[Dict[str, Any]]: Toàn bộ danh sách chunks đã chuẩn hóa.
        """
        all_chunks: List[Dict[str, Any]] = []

        for doc in documents:
            text = doc.get("content", "")
            doc_meta = doc.get("metadata", {})
            if not text.strip():
                continue

            doc_chunks = self.split_by_article(text, doc_meta)
            all_chunks.extend(doc_chunks)

        logger.info(
            f"Đã phân mảnh {len(documents)} tài liệu thành {len(all_chunks)} chunks chuẩn hóa."
        )
        return all_chunks

    @staticmethod
    def export_chunks_to_json(
        chunks: List[Dict[str, Any]],
        output_path: str = "data/processed/legal_chunks.json"
    ) -> str:
        """
        Xuất danh sách các chunk chuẩn hóa ra một tệp JSON riêng biệt.
        Args:
            chunks (List[Dict[str, Any]]): Danh sách các chunks chuẩn hóa.
            output_path (str): Đường dẫn file lưu trữ (mặc định trong data/processed/).
        Returns:
            str: Đường dẫn file đã lưu.
        """
        out_file = Path(output_path)
        if not out_file.is_absolute():
            project_root = Path(__file__).resolve().parents[3]
            out_file = project_root / output_path

        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        print(f"✔ Đã xuất thành công {len(chunks)} chunks ra file: {out_file}")
        return str(out_file)


if __name__ == "__main__":
    import sys

    # Cấu hình encoding UTF-8 để hiển thị tiếng Việt trên Terminal Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    from backend.src.ingestion.document_loader import DocumentLoader

    print("=== ĐANG NẠP VÀ PHÂN MẢNH TOÀN BỘ VĂN BẢN TỪ data/raw/ ===")
    loader = DocumentLoader("data/raw")
    documents = loader.load_all_raw_documents()

    splitter = LegalTextSplitter(chunk_size=1200, chunk_overlap=150)
    all_chunks = splitter.split_into_chunks(documents)

    output_path = "data/processed/legal_chunks.json"
    saved_path = LegalTextSplitter.export_chunks_to_json(all_chunks, output_path)

    print(f"✔ Hoàn thành: {len(all_chunks)} chunks chuẩn hóa đã được lưu tại:")
    print(f"  -> {saved_path}")

