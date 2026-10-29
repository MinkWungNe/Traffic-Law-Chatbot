"""
Module: test_evaluation.py
Mục đích: Bộ kiểm thử tự động (Unit Test & Integration Test) toàn diện cho Phân hệ 4
          (Evaluation, Benchmark Runner, RAGAS Metrics, Stress Testing Engine).
Người phụ trách: Thành viên 4 (Evaluation Lead)
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Đảm bảo root directory luôn nằm trong sys.path để import các module
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from evaluation.benchmark_runner import (
    BenchmarkRunner,
    get_latest_report,
    get_paginated_samples
)
from evaluation.ragas_eval import RagasEvaluator
from evaluation.stress_test import StressTester


# =====================================================================
# 1. KIỂM THỬ NẠP VÀ LÀM SẠCH BỘ DỮ LIỆU KIỂM THỬ
# =====================================================================

def test_benchmark_dataset_loading():
    """Kiểm tra đọc, làm sạch và parse đúng 683 câu hỏi kiểm thử từ file CSV."""
    runner = BenchmarkRunner(test_dataset_path="data/raw/683_CauHoi_TTATGTDB.csv")
    dataset = runner.load_test_dataset()

    assert len(dataset) == 683, f"Kỳ vọng 683 câu hỏi, nhưng đọc được {len(dataset)}"
    first_item = dataset[0]
    assert "id" in first_item, "Mỗi item phải có trường 'id'"
    assert "question" in first_item and len(first_item["question"]) > 0, "Câu hỏi không được rỗng"
    assert "ground_truth_answer" in first_item, "Phải có trường 'ground_truth_answer'"
    assert "ground_truth_citations" in first_item, "Phải có trường 'ground_truth_citations'"
    assert isinstance(first_item["ground_truth_citations"], list)


# =====================================================================
# 2. KIỂM THỬ BÓC TÁCH CĂN CỨ PHÁP LÝ BẰNG REGEX
# =====================================================================

def test_legal_citation_extraction():
    """Kiểm tra độ chính xác của bộ trích xuất biểu thức chính quy (Regex)."""
    sample_text = (
        "Căn cứ Điều 6 và Điều 67 Nghị định 168/2024/NĐ-CP, Thông tư 79/2024/TT-BCA "
        "và Luật Trật tự, an toàn giao thông đường bộ."
    )
    citations = BenchmarkRunner.extract_legal_citations(sample_text)

    assert "Điều 6" in citations
    assert "Điều 67" in citations
    assert "Nghị định 168/2024/NĐ-CP" in citations
    assert "Thông tư 79/2024/TT-BCA" in citations
    assert "Luật Trật tự, an toàn giao thông đường bộ" in citations


# =====================================================================
# 3. KIỂM THỬ CÔNG THỨC TOÁN HỌC RETRIEVAL METRICS (HIT, RECALL, MRR)
# =====================================================================

def test_retrieval_metrics_calculation_standard():
    """Kiểm tra tính toán Hit@K, Recall@K, MRR trong trường hợp chuẩn."""
    runner = BenchmarkRunner()

    item = {
        "ground_truth_citations": ["Điều 6", "Nghị định 168/2024/NĐ-CP"],
        "ground_truth_answer": "Căn cứ Điều 6 Nghị định 168..."
    }

    # Giả lập: trúng 1 căn cứ ở rank 1, không trúng ở rank 2, 3
    retrieved_docs = [
        {"title": "Trích lục Điều 6", "snippet": "Xử phạt vi phạm xe máy"},
        {"title": "Văn bản khác", "snippet": "Quy định chung"},
        {"title": "Quy chuẩn", "snippet": "Biển báo đường bộ"}
    ]

    metrics = runner.calculate_metrics_for_query(item, retrieved_docs)

    assert metrics["hit"] == 1.0, "Kỳ vọng Hit = 1.0"
    assert metrics["recall"] == 0.5, "Kỳ vọng Recall = 0.5 (1/2 căn cứ)"
    assert metrics["first_rank"] == 1, "Kỳ vọng rank đầu tiên = 1"
    assert metrics["reciprocal_rank"] == 1.0, "Kỳ vọng MRR = 1/1 = 1.0"


def test_retrieval_metrics_no_hit():
    """Kiểm tra trường hợp không tìm thấy bất kỳ căn cứ nào trong Top-K."""
    runner = BenchmarkRunner()
    item = {
        "ground_truth_citations": ["Điều 99", "Nghị định 999/2099/NĐ-CP"],
        "ground_truth_answer": "Quy định riêng"
    }
    retrieved_docs = [
        {"title": "Văn bản A", "snippet": "Không liên quan"},
        {"title": "Văn bản B", "snippet": "Nội dung khác"}
    ]
    metrics = runner.calculate_metrics_for_query(item, retrieved_docs)

    assert metrics["hit"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["first_rank"] == 0
    assert metrics["reciprocal_rank"] == 0.0


# =====================================================================
# 4. KIỂM THỬ KHỚP SCHEMA API CONTRACT CỦA BENCHMARK_REPORT.JSON
# =====================================================================

def test_benchmark_report_schema_compliance():
    """
    Kiểm tra cấu trúc file benchmark_report.json khớp 100% với đặc tả API Contract
    trong Mục 4.1 của PHAN_HE_4_AUDIT_VA_THIET_KE_TICH_HOP.md.
    """
    report_path = "evaluation/benchmark_report.json"
    assert os.path.exists(report_path), "File benchmark_report.json chưa được tạo"

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Kiểm tra Metadata
    assert "metadata" in data
    meta = data["metadata"]
    for field in ["framework", "dataset_file", "total_questions", "evaluated_samples", "top_k", "timestamp"]:
        assert field in meta, f"Metadata thiếu trường bắt buộc: {field}"

    # 2. Kiểm tra Summary Metrics
    assert "summary_metrics" in data
    summary = data["summary_metrics"]
    for field in ["hit_rate", "hit_rate_percentage", "recall_at_k", "recall_percentage", "mrr", "avg_latency_per_query_ms"]:
        assert field in summary, f"Summary metrics thiếu trường: {field}"

    # 3. Kiểm tra Quality Metrics (RAGAS)
    assert "quality_metrics" in data
    quality = data["quality_metrics"]
    assert "faithfulness_score" in quality
    assert "answer_relevance_score" in quality

    # 4. Kiểm tra Detailed Results
    assert "detailed_results" in data
    samples = data["detailed_results"]
    assert len(samples) > 0
    first_sample = samples[0]
    for field in ["id", "question", "ground_truth_citations", "retrieved_docs", "hit", "recall", "rank", "status"]:
        assert field in first_sample, f"Sample thiếu trường: {field}"


# =====================================================================
# 5. KIỂM THỬ HÀM HỖ TRỢ PHÂN TRANG VÀ TÌM KIẾM CHO ADMIN API
# =====================================================================

def test_get_paginated_samples_function():
    """Kiểm tra logic phân trang, lọc trạng thái và tìm kiếm từ khóa cho Admin API."""
    # 1. Phân trang mặc định
    res = get_paginated_samples(page=1, limit=10, status="all")
    assert res["page"] == 1
    assert res["limit"] == 10
    assert len(res["samples"]) <= 10
    assert res["total"] >= len(res["samples"])

    # 2. Lọc câu đạt
    res_passed = get_paginated_samples(page=1, limit=5, status="passed")
    for s in res_passed["samples"]:
        assert s["status"] == "Đạt" or s["hit"] > 0

    # 3. Tìm kiếm từ khóa
    res_search = get_paginated_samples(page=1, limit=5, status="all", search="đèn đỏ")
    for s in res_search["samples"]:
        assert "đèn đỏ" in s["question"].lower()


# =====================================================================
# 6. KIỂM THỬ BỘ ĐÁNH GIÁ CHẤT LƯỢNG RAGAS
# =====================================================================

def test_ragas_faithfulness_and_relevance():
    """Kiểm tra thuật toán đo lường Faithfulness và Answer Relevance của RagasEvaluator."""
    evaluator = RagasEvaluator()

    question = "Mức phạt người đi xe máy vượt đèn đỏ là bao nhiêu tiền?"
    answer = (
        "Căn cứ Điều 6 Nghị định 168/2024/NĐ-CP, người điều khiển xe mô tô, xe máy "
        "vượt đèn đỏ bị phạt tiền từ 800.000 đến 1.000.000 đồng và bị trừ điểm giấy phép lái xe."
    )
    docs = [
        {
            "title": "Nghị định 168/2024/NĐ-CP (Điều 6)",
            "snippet": "Xử phạt người điều khiển xe mô tô, xe gắn máy vi phạm tín hiệu đèn giao thông."
        }
    ]

    # Kiểm tra Faithfulness
    faith = evaluator.calculate_faithfulness(answer, docs, ground_truth_answer=answer)
    assert faith["score"] > 0.7, f"Kỳ vọng Faithfulness cao, nhận được {faith['score']}"
    assert faith["total_claims"] > 0

    # Kiểm tra Relevance
    rel = evaluator.calculate_answer_relevance(question, answer)
    assert rel["score"] >= 0.75, f"Kỳ vọng Answer Relevance cao, nhận được {rel['score']}"


# =====================================================================
# 7. KIỂM THỬ BỘ MÁY STRESS TEST (PHÂN VỊ & THỐNG KÊ ĐỘ TRỄ)
# =====================================================================

def test_stress_tester_report_generation():
    """Kiểm tra thuật toán tính toán thống kê phân vị (P50, P90, P95, P99) và RPS của StressTester."""
    tester = StressTester(concurrency=5, total_requests=10)

    # Giả lập 10 kết quả trả về
    mock_results = [
        {"request_id": 1, "success": True, "latency_ms": 10.0, "is_cached": False},
        {"request_id": 2, "success": True, "latency_ms": 20.0, "is_cached": True},
        {"request_id": 3, "success": True, "latency_ms": 30.0, "is_cached": True},
        {"request_id": 4, "success": True, "latency_ms": 40.0, "is_cached": False},
        {"request_id": 5, "success": True, "latency_ms": 50.0, "is_cached": False},
        {"request_id": 6, "success": True, "latency_ms": 60.0, "is_cached": True},
        {"request_id": 7, "success": True, "latency_ms": 70.0, "is_cached": False},
        {"request_id": 8, "success": True, "latency_ms": 80.0, "is_cached": False},
        {"request_id": 9, "success": True, "latency_ms": 90.0, "is_cached": True},
        {"request_id": 10, "success": True, "latency_ms": 100.0, "is_cached": False},
    ]
    tester.results = mock_results

    report = tester._generate_report(total_elapsed=2.0, mode="mock_test")
    summary = report["summary_metrics"]

    assert summary["successful_requests"] == 10
    assert summary["failed_requests"] == 0
    assert summary["throughput_rps"] == 5.0  # 10 reqs / 2.0s = 5.0 req/s
    assert summary["latency_min_ms"] == 10.0
    assert summary["latency_max_ms"] == 100.0
    assert summary["latency_median_p50_ms"] == 55.0

    cache = report["cache_performance"]
    assert cache["cached_requests"] == 4
    assert cache["uncached_requests"] == 6
    assert cache["cache_hit_rate_percentage"] == "40.0%"
