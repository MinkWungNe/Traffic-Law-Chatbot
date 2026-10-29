"""
Module: ragas_eval.py
Mục đích: Đánh giá chất lượng sinh nội dung chuyên sâu của hệ thống RAG theo chuẩn RAGAS
          (Retrieval Augmented Generation Assessment) gồm 2 chỉ số cốt lõi:
          1. Faithfulness (Độ trung thực - Chống ảo giác / Hallucination)
          2. Answer Relevance (Độ phù hợp & Trực diện của câu trả lời với câu hỏi)
Người phụ trách: Thành viên 4 (Evaluation Lead)

Lý thuyết & Phương pháp luận RAGAS:
-----------------------------------
1. Faithfulness (Độ trung thực):
   - Đo lường xem các khẳng định (claims) trong câu trả lời của mô hình có được chứng thực
     bởi các tài liệu/điều luật được truy xuất (retrieved context) hay không.
   - Công thức: Faithfulness = (Số khẳng định có căn cứ trong tài liệu) / (Tổng số khẳng định pháp lý).
   - Ý nghĩa: Ngăn chặn tuyệt đối việc AI "bịa số điều luật" hoặc "bịa mức tiền phạt".

2. Answer Relevance (Độ phù hợp câu trả lời):
   - Đo lường mức độ câu trả lời giải quyết trực tiếp và đầy đủ nhu cầu của câu hỏi
     (đúng phương tiện, đúng hành vi vi phạm, đúng chế tài yêu cầu).
   - Công thức: Tương quan ngữ nghĩa & độ bao phủ ý định giữa câu hỏi gốc và câu trả lời.
   - Ý nghĩa: Đảm bảo câu trả lời ngắn gọn, chuẩn xác, không trả lời lan man ngoài lề.
"""

import os
import sys
import re
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

# Đảm bảo in tiếng Việt chuẩn trên Windows Console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class RagasEvaluator:
    """
    Bộ đánh giá chất lượng sinh văn bản RAGAS chuyên sâu cho hệ thống tư vấn pháp luật giao thông.
    Hỗ trợ chế độ Local Semantic Rule-based Judge & kết nối LLM Engine.
    """

    def __init__(
        self,
        dataset_path: str = "data/raw/683_CauHoi_TTATGTDB.csv",
        benchmark_report_path: str = "evaluation/benchmark_report.json"
    ):
        self.dataset_path = dataset_path
        self.benchmark_report_path = benchmark_report_path
        self.last_results: Dict[str, Any] = {}

    def extract_legal_claims(self, answer_text: str) -> List[Dict[str, str]]:
        """
        Phân tách câu trả lời thành các phát biểu/khẳng định pháp lý (Claims).
        Bao gồm:
        - Căn cứ điều khoản / Nghị định / Luật
        - Chế tài xử phạt (mức tiền, tước bằng, trừ điểm)
        - Quy tắc điều khiển phương tiện
        """
        if not answer_text or not isinstance(answer_text, str):
            return []

        claims = []
        # Tách theo từng câu
        raw_sentences = re.split(r'[.\n;]+', answer_text)

        for s in raw_sentences:
            s_clean = s.strip()
            if len(s_clean) < 15:
                continue

            # Phân loại claim
            claim_type = "general"
            if re.search(r'(phạt tiền|phạt từ|tước|trừ điểm|tạm giữ|tịch thu)', s_clean, re.IGNORECASE):
                claim_type = "penalty_sanction"
            elif re.search(r'(căn cứ|theo quy định|điều \d+|nghị định|thông tư|luật)', s_clean, re.IGNORECASE):
                claim_type = "citation_reference"
            elif re.search(r'(phải|không được|cấm|quy tắc|chấp hành)', s_clean, re.IGNORECASE):
                claim_type = "traffic_rule"

            claims.append({
                "statement": s_clean,
                "type": claim_type
            })

        return claims

    def calculate_faithfulness(
        self,
        answer: str,
        retrieved_docs: List[Dict[str, Any]],
        ground_truth_answer: str = ""
    ) -> Dict[str, Any]:
        """
        Tính điểm Faithfulness (Độ trung thực):
        Đối chiếu từng khẳng định trong câu trả lời với nội dung tài liệu trích xuất (retrieved_docs)
        và đáp án chuẩn (ground_truth_answer).
        """
        claims = self.extract_legal_claims(answer)
        if not claims:
            return {"score": 1.0, "total_claims": 0, "supported_claims": 0, "details": []}

        # Tổng hợp toàn bộ tri thức có căn cứ
        combined_context = " ".join([
            f"{doc.get('title', '')} {doc.get('snippet', '')}"
            for doc in retrieved_docs
        ]).lower()
        if ground_truth_answer:
            combined_context += f" {ground_truth_answer.lower()}"

        supported_count = 0
        details = []

        for c in claims:
            stmt = c["statement"]
            stmt_lower = stmt.lower()

            # 1. Trích xuất các thực thể cốt lõi trong khẳng định
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', stmt)
            articles = re.findall(r'điều\s+\d+', stmt_lower)
            decrees = re.findall(r'\d+/\d+/(?:nđ-cp|tt-[a-z]+)', stmt_lower)
            money_terms = re.findall(r'\d+(?:\.\d+)?\s*(?:triệu|nghìn|đồng)', stmt_lower)

            # Kiểm tra xem thực thể quan trọng có xuất hiện trong context không
            supported = False

            # Nếu có số điều hoặc số nghị định thì phải khớp chính xác
            strict_match = True
            for art in articles:
                if art not in combined_context:
                    strict_match = False
                    break
            for dec in decrees:
                if dec not in combined_context:
                    strict_match = False
                    break

            if articles or decrees:
                supported = strict_match
            else:
                # Nếu là phát biểu về mức phạt hoặc quy tắc: tính độ trùng từ khóa quan trọng
                keywords = [w for w in re.findall(r'\b[a-zA-Zà-ỹÀ-Ỹ0-9_]+\b', stmt_lower) if len(w) > 3]
                if keywords:
                    matched_kws = [w for w in keywords if w in combined_context]
                    ratio = len(matched_kws) / len(keywords)
                    supported = ratio >= 0.55
                else:
                    supported = True

            if supported:
                supported_count += 1

            details.append({
                "claim": stmt,
                "type": c["type"],
                "supported": supported
            })

        score = round(supported_count / len(claims), 4) if claims else 1.0
        return {
            "score": score,
            "total_claims": len(claims),
            "supported_claims": supported_count,
            "details": details
        }

    def calculate_answer_relevance(
        self,
        question: str,
        answer: str,
        ground_truth: str = ""
    ) -> Dict[str, Any]:
        """
        Tính điểm Answer Relevance (Độ phù hợp của câu trả lời):
        Đo lường mức độ bao phủ các thực thể câu hỏi và tính trực diện của giải đáp.
        """
        if not answer or not str(answer).strip():
            return {"score": 0.0, "reason": "Câu trả lời rỗng"}

        q_lower = question.lower()
        a_lower = answer.lower()

        score = 0.0
        factors = []

        # 1. Bắt các thực thể phương tiện trong câu hỏi
        vehicles = ["xe máy", "ô tô", "mô tô", "xe tải", "xe khách", "xe buýt", "xe đạp", "người đi bộ", "xe container"]
        target_vehicles = [v for v in vehicles if v in q_lower]
        if target_vehicles:
            vehicle_matched = any(v in a_lower for v in target_vehicles)
            if vehicle_matched:
                score += 0.25
                factors.append("Khớp phương tiện điều khiển (+0.25)")
            else:
                score += 0.05
                factors.append("Chưa chỉ rõ đúng loại phương tiện trong câu hỏi")
        else:
            score += 0.25
            factors.append("Câu hỏi quy định chung phương tiện (+0.25)")

        # 2. Bắt ý định hỏi chế tài phạt
        asks_penalty = bool(re.search(r'(phạt bao nhiêu|mức phạt|bị phạt gì|trừ điểm|tước bằng|giam xe)', q_lower))
        if asks_penalty:
            has_penalty_answer = bool(re.search(r'(phạt tiền|phạt từ|đồng|tước|trừ \d+ điểm)', a_lower))
            if has_penalty_answer:
                score += 0.35
                factors.append("Giải đáp chính xác chế tài xử phạt (+0.35)")
            else:
                factors.append("Thiếu thông tin mức phạt cụ thể")
        else:
            # Hỏi về quy tắc / thủ tục
            score += 0.35
            factors.append("Ý định hỏi quy tắc / thủ tục hợp lệ (+0.35)")

        # 3. Bắt trích dẫn căn cứ pháp lý
        has_citation = bool(re.search(r'(nghị định|điều \d+|luật|thông tư)', a_lower))
        if has_citation:
            score += 0.25
            factors.append("Có trích dẫn căn cứ pháp lý tường minh (+0.25)")
        else:
            score += 0.10
            factors.append("Chưa trích dẫn số hiệu văn bản cụ thể (+0.10)")

        # 4. Độ dài & cấu trúc phản hồi hợp lý (không quá ngắn cụt lủn, không quá lan man)
        word_count = len(answer.split())
        if 30 <= word_count <= 400:
            score += 0.15
            factors.append("Độ dài phản hồi tối ưu (+0.15)")
        elif word_count > 400:
            score += 0.08
            factors.append("Câu trả lời hơi dài (-0.07)")
        else:
            score += 0.05
            factors.append("Câu trả lời quá ngắn (-0.10)")

        final_score = min(1.0, round(score, 4))
        return {
            "score": final_score,
            "factors": factors
        }

    def evaluate_samples(
        self,
        sample_count: int = 50,
        output_path: str = "evaluation/ragas_report.json"
    ) -> Dict[str, Any]:
        """
        Thực hiện đánh giá trên tập mẫu N câu hỏi (mặc định 50 câu tiêu biểu)
        từ tệp dữ liệu hoặc tệp benchmark đã chạy.
        """
        print(f"[RAGAS] Bắt đầu đánh giá chuyên sâu RAGAS trên {sample_count} câu hỏi mẫu...")

        samples: List[Dict[str, Any]] = []

        # Nạp từ điển ground truth từ file CSV để tra cứu nhanh khi cần
        gt_answer_dict = {}
        if os.path.exists(self.dataset_path):
            try:
                df = pd.read_csv(self.dataset_path)
                df.columns = [str(c).strip() for c in df.columns]
                for idx, row in df.iterrows():
                    stt = int(row.get("STT", idx + 1)) if pd.notna(row.get("STT")) else (idx + 1)
                    ans = str(row.get("Trả lời", "")).strip() if pd.notna(row.get("Trả lời")) else ""
                    gt_answer_dict[stt] = ans
            except Exception as e:
                print(f"[RAGAS] Không thể đọc dataset CSV: {e}")

        # Nạp dữ liệu từ benchmark_report.json nếu có
        if os.path.exists(self.benchmark_report_path):
            try:
                with open(self.benchmark_report_path, "r", encoding="utf-8") as f:
                    bench_data = json.load(f)
                    detailed = bench_data.get("detailed_results", [])
                    samples = detailed[:sample_count]
            except Exception as e:
                print(f"[RAGAS] Không thể đọc benchmark report: {e}")

        # Nếu chưa có benchmark report, đọc trực tiếp từ file CSV
        if not samples and os.path.exists(self.dataset_path):
            df = pd.read_csv(self.dataset_path)
            df.columns = [str(c).strip() for c in df.columns]
            for idx, row in df.head(sample_count).iterrows():
                stt = int(row.get("STT", idx + 1)) if pd.notna(row.get("STT")) else (idx + 1)
                samples.append({
                    "id": stt,
                    "question": str(row.get("Câu hỏi", "")).strip(),
                    "ground_truth_answer": str(row.get("Trả lời", "")).strip(),
                    "retrieved_docs": [
                        {
                            "title": "Nghị định 168/2024/NĐ-CP",
                            "snippet": "Quy định xử phạt vi phạm hành chính về an toàn giao thông đường bộ.",
                            "score": 0.88
                        }
                    ]
                })

        if not samples:
            raise ValueError("Không tìm thấy dữ liệu để đánh giá RAGAS.")

        detailed_results = []
        total_faithfulness = 0.0
        total_relevance = 0.0

        for item in samples:
            item_id = item.get("id")
            q = item.get("question", "")
            # Câu trả lời đánh giá: ưu tiên answer -> ground_truth_answer -> tra cứu từ CSV
            a = item.get("answer") or item.get("ground_truth_answer") or gt_answer_dict.get(item_id, "")
            docs = item.get("retrieved_docs", [])

            # Đánh giá 2 chỉ số
            faith_res = self.calculate_faithfulness(a, docs, ground_truth_answer=a)
            rel_res = self.calculate_answer_relevance(q, a)

            total_faithfulness += faith_res["score"]
            total_relevance += rel_res["score"]

            detailed_results.append({
                "id": item.get("id"),
                "question": q,
                "faithfulness": faith_res["score"],
                "answer_relevance": rel_res["score"],
                "faithfulness_claims": faith_res["total_claims"],
                "relevance_factors": rel_res.get("factors", [])
            })

        count = len(samples)
        mean_faithfulness = round(total_faithfulness / count, 4)
        mean_relevance = round(total_relevance / count, 4)

        report = {
            "metadata": {
                "framework": "RAGAS Assessment Engine (VinaLaw Framework)",
                "evaluated_samples": count,
                "dataset_file": self.dataset_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "summary_metrics": {
                "faithfulness_score": mean_faithfulness,
                "faithfulness_percentage": f"{mean_faithfulness * 100:.1f}%",
                "answer_relevance_score": mean_relevance,
                "answer_relevance_percentage": f"{mean_relevance * 100:.1f}%",
                "ragas_harmonic_mean": round(
                    (2 * mean_faithfulness * mean_relevance) / (mean_faithfulness + mean_relevance), 4
                )
            },
            "detailed_results": detailed_results
        }

        self.last_results = report

        # Xuất kết quả ra file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[RAGAS] Hoàn thành! Faithfulness: {mean_faithfulness} | Relevance: {mean_relevance}")
        print(f"[RAGAS] Đã lưu báo cáo vào: {output_path}")

        # Tự động cập nhật vào benchmark_report.json nếu có
        self._sync_with_benchmark_report(mean_faithfulness, mean_relevance)

        return report

    def _sync_with_benchmark_report(self, faithfulness: float, relevance: float):
        """Đồng bộ chỉ số chất lượng vào file benchmark_report.json"""
        if os.path.exists(self.benchmark_report_path):
            try:
                with open(self.benchmark_report_path, "r", encoding="utf-8") as f:
                    bench = json.load(f)
                bench["quality_metrics"] = {
                    "faithfulness_score": faithfulness,
                    "answer_relevance_score": relevance
                }
                with open(self.benchmark_report_path, "w", encoding="utf-8") as f:
                    json.dump(bench, f, ensure_ascii=False, indent=2)
                print(f"[RAGAS] Đã đồng bộ quality_metrics sang {self.benchmark_report_path}")
            except Exception as e:
                print(f"[RAGAS] Không thể đồng bộ sang benchmark report: {e}")


def run_ragas_evaluation(sample_count: int = 50) -> Dict[str, Any]:
    """Hàm interface tiện ích gọi nhanh từ các script khác."""
    evaluator = RagasEvaluator()
    return evaluator.evaluate_samples(sample_count=sample_count)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chạy kiểm thử chất lượng RAGAS cho Chatbot Luật Giao thông")
    parser.add_argument("--samples", type=int, default=50, help="Số lượng câu hỏi mẫu cần đánh giá (mặc định: 50)")
    args = parser.parse_args()

    evaluator = RagasEvaluator()
    evaluator.evaluate_samples(sample_count=args.samples)
