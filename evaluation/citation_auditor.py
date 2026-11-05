"""
Module: citation_auditor.py
Mục đích: Bộ kiểm toán tính nhất quán của căn cứ pháp lý và phát hiện ảo giác (Hallucination Detector)
          trong câu trả lời của mô hình RAG tư vấn luật giao thông.
Người phụ trách: Thành viên 4 (Evaluation Lead)

Đặc tả kỹ thuật & Cơ chế phát hiện:
-----------------------------------
1. Trích xuất trích dẫn (Legal Citation Extraction):
   - Bóc tách toàn bộ các số hiệu Luật, Nghị định, Thông tư, Quy chuẩn và Điều khoản
     được mô hình viện dẫn trong văn bản trả lời.
2. Kiểm toán tính tồn tại (Existence & Validity Verification):
   - Đối chiếu với Cơ sở dữ liệu Pháp điển Văn bản Quy phạm Pháp luật Giao thông Việt Nam.
   - Phát hiện các trích dẫn bịa đặt (Fabricated Hallucination) - ví dụ: "Điều 999", "Nghị định 555/2099".
3. Phát hiện xung đột hiệu lực (Temporal Status Audit):
   - Cảnh báo viện dẫn các văn bản đã bị sửa đổi, bổ sung hoặc hết hiệu lực thi hành.
4. Đo lường chỉ số rủi ro (Risk Scoring & Hallucination Rate):
   - Citation Hallucination Rate = (Số trích dẫn ảo giác) / (Tổng số trích dẫn).
   - Phân cấp mức độ an toàn: SAFE (0%), LOW (<10%), MEDIUM (10-30%), CRITICAL (>30%).
"""

import os
import sys
import re
import json
import time
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

# Đảm bảo root directory nằm trong sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Đảm bảo in tiếng Việt chuẩn trên Windows Console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from evaluation.eval_utils import extract_legal_citations


# Danh mục dự phòng mặc định (Fallback Registry khi không tìm thấy tệp JSON)
DEFAULT_LEGAL_REGISTRY = {
    "nghi_dinh": {
        "168/2024/nđ-cp": {"name": "Nghị định 168/2024/NĐ-CP", "status": "active", "scope": "Xử phạt VPHC trật tự ATGT đường bộ; trừ điểm GPLX", "max_article": 60},
        "238/2026/nđ-cp": {"name": "Nghị định 238/2026/NĐ-CP", "status": "active", "scope": "Sửa đổi, bổ sung một số điều Nghị định 168/2024", "max_article": 15},
        "61/2026/nđ-cp": {"name": "Nghị định 61/2026/NĐ-CP", "status": "active", "scope": "Quy trình sử dụng thiết bị kỹ thuật nghiệp vụ phát hiện vi phạm", "max_article": 30},
        "100/2019/nđ-cp": {"name": "Nghị định 100/2019/NĐ-CP", "status": "amended_superseded", "scope": "Xử phạt VPHC giao thông đường bộ đường sắt (đã thay thế)", "max_article": 86},
        "123/2021/nđ-cp": {"name": "Nghị định 123/2021/NĐ-CP", "status": "amended_superseded", "scope": "Sửa đổi Nghị định 100/2019", "max_article": 10}
    },
    "luat": {
        "36/2024/qh15": {"name": "Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15", "status": "active", "max_article": 89},
        "35/2024/qh15": {"name": "Luật Đường bộ số 35/2024/QH15", "status": "active", "max_article": 86},
        "15/2012/qh13": {"name": "Luật Xử lý vi phạm hành chính số 15/2012/QH13 (sửa đổi)", "status": "active", "max_article": 142},
        "23/2008/qh12": {"name": "Luật Giao thông đường bộ 2008", "status": "amended_superseded", "max_article": 89}
    },
    "thong_tu": {
        "73/2024/tt-bca": {"name": "Thông tư 73/2024/TT-BCA", "status": "active", "scope": "Tuần tra, kiểm soát của CSGT", "max_article": 35},
        "79/2024/tt-bca": {"name": "Thông tư 79/2024/TT-BCA", "status": "active", "scope": "Đăng ký xe, biển số định danh", "max_article": 40},
        "32/2023/tt-bca": {"name": "Thông tư 32/2023/TT-BCA", "status": "amended_superseded", "scope": "Tuần tra kiểm soát giao thông đường bộ", "max_article": 30}
    },
    "quy_chuan": {
        "qcvn 41:2019/bgtvt": {"name": "Quy chuẩn kỹ thuật quốc gia QCVN 41:2019/BGTVT", "status": "active", "scope": "Báo hiệu đường bộ", "max_article": 90}
    }
}


def load_legal_registry(registry_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Nạp danh mục văn bản luật từ tệp cấu hình JSON tách biệt.
    Giúp quản trị viên có thể cập nhật văn bản luật mới mà không cần can thiệp mã nguồn Python.
    """
    candidates = [
        registry_path,
        "evaluation/legal_registry.json",
        str(ROOT_DIR / "evaluation" / "legal_registry.json"),
        "data/legal_registry.json",
        str(ROOT_DIR / "data" / "legal_registry.json")
    ]
    for p in candidates:
        if p and os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Lọc bỏ metadata nếu có
                    return {k: v for k, v in data.items() if k != "metadata"}
            except Exception:
                pass
    return DEFAULT_LEGAL_REGISTRY


class CitationAuditor:
    """
    Bộ kiểm toán và phát hiện ảo giác trích dẫn pháp lý chuyên nghiệp.
    """

    def __init__(
        self,
        registry_path: Optional[str] = None,
        registry: Optional[Dict[str, Any]] = None
    ):
        if registry:
            self.registry = registry
        else:
            self.registry = load_legal_registry(registry_path)

    def extract_citations_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Bóc tách toàn bộ trích dẫn văn bản luật, số hiệu nghị định/thông tư và điều khoản.

        Args:
            text (str): Đoạn văn bản phản hồi của chatbot RAG.

        Returns:
            List[Dict[str, Any]]: Danh sách các thực thể pháp lý được tìm thấy.
        """
        if not text or not isinstance(text, str):
            return []

        citations = []
        text_lower = text.lower()

        # 1. Trích xuất Nghị định
        nd_matches = re.finditer(r'(?:nghị định\s+(?:số\s+)?(\d+/\d+/(?:nđ-cp|nd-cp))|nghị định\s+(\d+/\d+))', text_lower)
        for m in nd_matches:
            raw_id = m.group(1) or m.group(2)
            if not raw_id.endswith("/nđ-cp") and not raw_id.endswith("/nd-cp"):
                full_id = f"{raw_id}/nđ-cp"
            else:
                full_id = raw_id.replace("nd-cp", "nđ-cp")
            citations.append({
                "type": "nghi_dinh",
                "raw_match": m.group(0),
                "identifier": full_id,
                "span": m.span()
            })

        # 2. Trích xuất Thông tư
        tt_matches = re.finditer(r'(?:thông tư\s+(?:số\s+)?(\d+/\d+/(?:tt-[a-z]+))|thông tư\s+(\d+/\d+))', text_lower)
        for m in tt_matches:
            raw_id = m.group(1) or m.group(2)
            if not re.search(r'tt-[a-z]+', raw_id):
                full_id = f"{raw_id}/tt-bca"
            else:
                full_id = raw_id
            citations.append({
                "type": "thong_tu",
                "raw_match": m.group(0),
                "identifier": full_id,
                "span": m.span()
            })

        # 3. Trích xuất Luật
        if "luật trật tự, an toàn giao thông" in text_lower or "luật 36/2024" in text_lower or "luật ttagt" in text_lower:
            citations.append({
                "type": "luat",
                "raw_match": "Luật Trật tự, an toàn giao thông đường bộ",
                "identifier": "36/2024/qh15"
            })
        if "luật đường bộ" in text_lower or "luật 35/2024" in text_lower:
            citations.append({
                "type": "luat",
                "raw_match": "Luật Đường bộ",
                "identifier": "35/2024/qh15"
            })
        if "luật xử lý vi phạm hành chính" in text_lower or "luật xlvphc" in text_lower:
            citations.append({
                "type": "luat",
                "raw_match": "Luật Xử lý vi phạm hành chính",
                "identifier": "15/2012/qh13"
            })

        # 4. Trích xuất Quy chuẩn
        if "qcvn 41" in text_lower:
            citations.append({
                "type": "quy_chuan",
                "raw_match": "Quy chuẩn QCVN 41:2019/BGTVT",
                "identifier": "qcvn 41:2019/bgtvt"
            })

        # 5. Trích xuất Điều khoản (Article citations)
        article_matches = re.finditer(r'\bđiều\s+(\d+)\b', text_lower)
        for am in article_matches:
            art_num = int(am.group(1))
            citations.append({
                "type": "dieu_khoan",
                "raw_match": am.group(0),
                "article_number": art_num,
                "span": am.span()
            })

        return citations

    def audit_citation(self, cite: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm toán tính hợp lệ của một trích dẫn cụ thể.
        """
        cite_type = cite.get("type")
        cite_id = str(cite.get("identifier", "")).lower().strip()

        # Kiểm tra văn bản quy phạm (Nghị định, Thông tư, Luật, Quy chuẩn)
        if cite_type in self.registry:
            type_registry = self.registry[cite_type]
            if cite_id in type_registry:
                reg_info = type_registry[cite_id]
                return {
                    "citation": cite.get("raw_match"),
                    "identifier": cite_id,
                    "type": cite_type,
                    "status": "VALID",
                    "legal_status": reg_info.get("status", "active"),
                    "details": reg_info.get("name"),
                    "is_hallucination": False
                }
            else:
                # Không tìm thấy trong kho văn bản chính thống -> Ảo giác
                return {
                    "citation": cite.get("raw_match"),
                    "identifier": cite_id,
                    "type": cite_type,
                    "status": "FABRICATED_HALLUCINATION",
                    "legal_status": "non_existent",
                    "details": f"Văn bản '{cite_id}' không tồn tại trong hệ thống pháp luật Việt Nam.",
                    "is_hallucination": True
                }

        # Kiểm tra Điều khoản (Articles)
        if cite_type == "dieu_khoan":
            art_num = cite.get("article_number", 0)
            # Điều khoản giao thông thực tế thường <= 150 (Luật XLVPHC có 142 điều)
            if art_num <= 0 or art_num > 150:
                return {
                    "citation": cite.get("raw_match"),
                    "article_number": art_num,
                    "type": cite_type,
                    "status": "FABRICATED_ARTICLE",
                    "legal_status": "out_of_bounds",
                    "details": f"Điều {art_num} vượt quá số điều luật quy định tối đa của pháp luật đường bộ.",
                    "is_hallucination": True
                }
            else:
                return {
                    "citation": cite.get("raw_match"),
                    "article_number": art_num,
                    "type": cite_type,
                    "status": "VALID",
                    "legal_status": "plausible",
                    "details": f"Điều {art_num} nằm trong biên độ quy định pháp luật hợp lệ.",
                    "is_hallucination": False
                }

        return {
            "citation": cite.get("raw_match", "unknown"),
            "type": cite_type,
            "status": "UNKNOWN",
            "is_hallucination": False
        }

    def audit_answer(self, answer_text: str) -> Dict[str, Any]:
        """
        Kiểm toán toàn bộ câu trả lời, trả về báo cáo phân cấp rủi ro ảo giác.
        """
        extracted = self.extract_citations_from_text(answer_text)
        audited_citations = []
        hallucinated_count = 0
        superseded_count = 0
        valid_count = 0

        for c in extracted:
            res = self.audit_citation(c)
            audited_citations.append(res)
            if res.get("is_hallucination"):
                hallucinated_count += 1
            elif res.get("legal_status") == "amended_superseded":
                superseded_count += 1
            elif res.get("status") == "VALID":
                valid_count += 1

        total = len(audited_citations)
        hallucination_rate = round(hallucinated_count / total, 4) if total > 0 else 0.0
        validity_rate = round(valid_count / total, 4) if total > 0 else 1.0

        # Phân cấp mức độ rủi ro (Risk Level)
        if hallucinated_count > 0:
            risk_level = "CRITICAL_HALLUCINATION" if hallucinated_count >= 2 else "MEDIUM_RISK"
        elif superseded_count > 0:
            risk_level = "LOW_RISK_SUPERSEDED_LAW"
        else:
            risk_level = "SAFE"

        return {
            "total_citations": total,
            "valid_citations_count": valid_count,
            "hallucinated_citations_count": hallucinated_count,
            "superseded_citations_count": superseded_count,
            "hallucination_rate": hallucination_rate,
            "citation_validity_rate": validity_rate,
            "risk_level": risk_level,
            "citations_detail": audited_citations
        }

    def audit_dataset_samples(
        self,
        samples_path: str = "data/raw/683_CauHoi_TTATGTDB.csv",
        sample_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Chạy kiểm toán trên tập câu hỏi mẫu trong dataset để đánh giá chất lượng Ground Truth.
        """
        import pandas as pd
        if not os.path.exists(samples_path):
            raise FileNotFoundError(f"Không tìm thấy file: {samples_path}")

        try:
            df = pd.read_csv(samples_path, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(samples_path, encoding="utf-8", errors="ignore")

        df.columns = [str(c).strip() for c in df.columns]
        samples_to_audit = df.head(sample_limit).to_dict(orient="records")
        results = []
        total_hallucinations = 0
        total_superseded = 0
        total_cites = 0

        for row in samples_to_audit:
            q = (
                row.get("question")
                or row.get("cau_hoi")
                or row.get("Câu hỏi")
                or ""
            )
            # Ưu tiên cột Trả lời và Nguồn căn cứ luật
            ans_text = str(row.get("ground_truth_answer") or row.get("dap_an") or row.get("Trả lời") or "")
            src_text = str(row.get("Nguồn") or row.get("nguon") or "")
            full_text_to_audit = f"{ans_text} {src_text}".strip()

            rep = self.audit_answer(full_text_to_audit)

            total_hallucinations += rep["hallucinated_citations_count"]
            total_superseded += rep["superseded_citations_count"]
            total_cites += rep["total_citations"]

            results.append({
                "question": q,
                "answer_preview": full_text_to_audit[:120] + "...",
                "audit": rep
            })

        overall_validity = round((total_cites - total_hallucinations) / total_cites, 4) if total_cites > 0 else 1.0

        return {
            "metadata": {
                "audited_samples": len(results),
                "dataset_file": samples_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "summary": {
                "total_citations_analyzed": total_cites,
                "total_hallucinations_detected": total_hallucinations,
                "total_superseded_laws_detected": total_superseded,
                "overall_validity_rate": overall_validity,
                "overall_hallucination_rate": round(total_hallucinations / total_cites, 4) if total_cites > 0 else 0.0,
                "system_status": "PASSED_STRICT_LEGAL_AUDIT" if total_hallucinations == 0 else "WARNING_HALLUCINATION"
            },
            "detailed_audits": results
        }

    def export_report(self, report_data: Dict[str, Any], output_path: str = "evaluation/citation_audit_report.json") -> str:
        """Xuất báo cáo kiểm toán trích dẫn ra file JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"[CITATION AUDITOR] Đã xuất báo cáo vào: {output_path}")
        return output_path


if __name__ == "__main__":
    auditor = CitationAuditor()
    print("[CITATION AUDITOR] Bắt đầu kiểm toán trích dẫn trên tập dữ liệu mẫu...")
    rep = auditor.audit_dataset_samples(sample_limit=50)
    print(f"Tổng số trích dẫn: {rep['summary']['total_citations_analyzed']}")
    print(f"Số trích dẫn ảo giác: {rep['summary']['total_hallucinations_detected']}")
    print(f"Tỷ lệ trích dẫn hợp lệ: {rep['summary']['overall_validity_rate']*100:.1f}%")
    print(f"Trạng thái an toàn: {rep['summary']['system_status']}")
    auditor.export_report(rep)
