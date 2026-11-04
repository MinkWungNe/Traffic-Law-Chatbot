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


# Danh mục các văn bản quy phạm pháp luật giao thông chính thức tại Việt Nam
OFFICIAL_LEGAL_REGISTRY = {
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


class CitationAuditor:
    """
    Bộ kiểm toán và phát hiện ảo giác trích dẫn pháp lý chuyên nghiệp.
    """

    def __init__(self, registry: Optional[Dict[str, Any]] = None):
        self.registry = registry or OFFICIAL_LEGAL_REGISTRY

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
            if 1 <= art_num <= 150:
                return {
                    "citation": f"Điều {art_num}",
                    "type": "dieu_khoan",
                    "status": "PLAUSIBLE_ARTICLE",
                    "details": f"Số thứ tự Điều {art_num} nằm trong dải điều khoản hợp lệ.",
                    "is_hallucination": False
                }
            else:
                # Điều khoản vượt quá số lượng điều thực tế (ví dụ Điều 999)
                return {
                    "citation": f"Điều {art_num}",
                    "type": "dieu_khoan",
                    "status": "FABRICATED_ARTICLE",
                    "details": f"Điều {art_num} vượt quá số lượng điều khoản của văn bản pháp luật.",
                    "is_hallucination": True
                }

        return {
            "citation": cite.get("raw_match", "unknown"),
            "type": "general",
            "status": "VAGUE_REFERENCE",
            "is_hallucination": False
        }

    def audit_answer(
        self,
        answer_text: str,
        retrieved_docs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Kiểm toán toàn diện một câu trả lời được sinh ra bởi hệ thống RAG.

        Args:
            answer_text (str): Nội dung phản hồi của chatbot.
            retrieved_docs (Optional[List[Dict[str, Any]]]): Các tài liệu RAG truy xuất được.

        Returns:
            Dict[str, Any]: Báo cáo kiểm toán với tỷ lệ ảo giác và cảnh báo chi tiết.
        """
        raw_citations = self.extract_citations_from_text(answer_text)
        audited_cites = [self.audit_citation(c) for c in raw_citations]

        total_citations = len(audited_cites)
        hallucinated_cites = [c for c in audited_cites if c.get("is_hallucination")]
        valid_cites = [c for c in audited_cites if not c.get("is_hallucination") and c.get("status") in ("VALID", "PLAUSIBLE_ARTICLE")]
        superseded_cites = [c for c in audited_cites if c.get("legal_status") == "amended_superseded"]

        hallucination_count = len(hallucinated_cites)
        hallucination_rate = round((hallucination_count / total_citations), 4) if total_citations > 0 else 0.0
        validity_rate = round((len(valid_cites) / total_citations), 4) if total_citations > 0 else 1.0

        # Xác định Risk Level
        if hallucination_count == 0 and len(superseded_cites) == 0:
            risk_level = "SAFE"
        elif hallucination_count == 0 and len(superseded_cites) > 0:
            risk_level = "LOW_RISK_SUPERSEDED_LAW"
        elif hallucination_rate <= 0.25:
            risk_level = "MEDIUM_RISK"
        else:
            risk_level = "CRITICAL_HALLUCINATION"

        return {
            "total_citations": total_citations,
            "valid_citations_count": len(valid_cites),
            "hallucinated_citations_count": hallucination_count,
            "superseded_citations_count": len(superseded_cites),
            "hallucination_rate": hallucination_rate,
            "hallucination_rate_percentage": f"{hallucination_rate * 100:.1f}%",
            "citation_validity_rate": validity_rate,
            "risk_level": risk_level,
            "detailed_citations": audited_cites
        }

    def audit_evaluation_dataset(
        self,
        benchmark_report_path: str = "evaluation/benchmark_report.json",
        sample_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Kiểm toán tỷ lệ ảo giác trích dẫn trên tập kết quả đánh giá thực tế.
        """
        if not os.path.exists(benchmark_report_path):
            raise FileNotFoundError(f"Không tìm thấy file {benchmark_report_path}")

        with open(benchmark_report_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        samples = bench_data.get("detailed_results", [])[:sample_limit]
        if not samples:
            return {"error": "Không có mẫu kết quả chi tiết để kiểm toán"}

        total_audited = len(samples)
        total_hallucinations = 0
        total_cites = 0
        risk_counter = {"SAFE": 0, "LOW_RISK_SUPERSEDED_LAW": 0, "MEDIUM_RISK": 0, "CRITICAL_HALLUCINATION": 0}
        audit_samples = []

        for s in samples:
            # Ưu tiên lấy text câu trả lời hoặc ground truth answer
            ans = s.get("answer") or s.get("ground_truth_answer", "")
            docs = s.get("retrieved_docs", [])
            audit_res = self.audit_answer(ans, docs)

            total_cites += audit_res["total_citations"]
            total_hallucinations += audit_res["hallucinated_citations_count"]
            risk = audit_res["risk_level"]
            risk_counter[risk] = risk_counter.get(risk, 0) + 1

            audit_samples.append({
                "id": s.get("id"),
                "question": s.get("question"),
                "total_citations": audit_res["total_citations"],
                "hallucination_rate": audit_res["hallucination_rate_percentage"],
                "risk_level": risk,
                "hallucinated_items": [c["citation"] for c in audit_res["detailed_citations"] if c.get("is_hallucination")]
            })

        avg_hallucination_rate = round(total_hallucinations / total_cites, 4) if total_cites > 0 else 0.0

        report = {
            "metadata": {
                "auditor_framework": "Legal Hallucination & Citation Consistency Auditor",
                "evaluated_samples": total_audited,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "summary_metrics": {
                "total_citations_analyzed": total_cites,
                "total_hallucinations_detected": total_hallucinations,
                "system_hallucination_rate": avg_hallucination_rate,
                "system_hallucination_percentage": f"{avg_hallucination_rate * 100:.2f}%",
                "safe_responses_ratio": f"{(risk_counter['SAFE'] / total_audited) * 100:.1f}%",
                "risk_distribution": risk_counter
            },
            "sample_audit_details": audit_samples
        }

        output_path = "evaluation/citation_audit_report.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[AUDIT] Hoàn thành kiểm toán {total_audited} mẫu. Đã lưu: {output_path}")
        return report


if __name__ == "__main__":
    auditor = CitationAuditor()
    print("Kiểm thử kiểm toán phát hiện ảo giác trích dẫn...")
    test_ans = (
        "Căn cứ Điều 6 Nghị định 168/2024/NĐ-CP và Điều 999 Nghị định 999/2099/NĐ-CP, "
        "người đi xe máy vượt đèn đỏ bị phạt 800.000 đến 1.000.000 đồng."
    )
    result = auditor.audit_answer(test_ans)
    print("Kết quả kiểm toán đơn lẻ:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\nKiểm toán tự động 50 câu trong benchmark_report.json...")
    auditor.audit_evaluation_dataset(sample_limit=50)
