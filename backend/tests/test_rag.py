"""
Module: test_rag.py
Mục đích: Kiểm thử tự động (Unit Test) cho phân hệ RAG và hệ thống Đánh giá Benchmark.
Người phụ trách chính: Thành viên 4 (Evaluation Lead) & Thành viên 2 (RAG Co-dev)

Các kịch bản kiểm thử:
1. test_rag_dummy_response: Kiểm tra pipeline RAG trả về đúng cấu trúc chuẩn.
2. test_benchmark_dataset_loading: Kiểm tra việc nạp dữ liệu 683 câu hỏi kiểm thử.
3. test_legal_citation_extraction: Kiểm tra bóc tách căn cứ pháp lý từ Ground Truth bằng Regex.
4. test_retrieval_metrics_calculation: Kiểm tra tính toán các chỉ số toán học Hit-rate, Recall@K, MRR.
"""

import os
import sys
from pathlib import Path

# Đảm bảo root directory luôn nằm trong sys.path để import các module
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # Lấy đường dẫn thư mục gốc của dự án (lùi 3 cấp từ file test)
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))  # Chèn đường dẫn gốc vào đầu sys.path để Python có thể import được các module trong dự án

import pytest
from evaluation.benchmark_runner import BenchmarkRunner  # Import lớp BenchmarkRunner từ phân hệ đánh giá


##=============================
# 1. Hàm kiểm tra pipeline RAG trả về đúng cấu trúc dữ liệu chuẩn (gồm answer, sources)
##=============================
def test_rag_dummy_response():
    """
    Kịch bản 1: Kiểm tra luồng RAG cơ bản trả về cấu trúc câu trả lời hợp lệ
    (gồm answer, sources và query).
    """
    from backend.src.rag.rag_pipeline import LegalRAGPipeline  # Import pipeline RAG từ backend
    pipeline = LegalRAGPipeline()  # Khởi tạo đối tượng pipeline RAG
    res = pipeline.answer_question("Vượt đèn đỏ phạt bao nhiêu?")  # Gọi hàm trả lời câu hỏi và lưu kết quả vào biến res
    
    assert "answer" in res, "Kết quả thiếu trường 'answer'"  # Kiểm tra kết quả phải chứa trường 'answer' (câu trả lời)
    assert "sources" in res, "Kết quả thiếu trường 'sources'"  # Kiểm tra kết quả phải chứa trường 'sources' (nguồn trích dẫn)
    assert isinstance(res["sources"], list), "Trường 'sources' phải là một danh sách"  # Kiểm tra 'sources' phải là kiểu danh sách (list)
    print("[PASSED] test_rag_dummy_response: Pipeline trả về đúng cấu trúc.")  # In thông báo test đạt


##=============================
# 2. Hàm kiểm tra việc nạp và tiền xử lý tập 683 câu hỏi kiểm thử từ file CSV
##=============================
def test_benchmark_dataset_loading():
    """
    Kịch bản 2: Kiểm tra nạp và tiền xử lý tập 683 câu hỏi kiểm thử.
    """
    runner = BenchmarkRunner(test_dataset_path="data/raw/683_CauHoi_TTATGTDB.csv")  # Khởi tạo BenchmarkRunner với đường dẫn file CSV chứa 683 câu hỏi
    dataset = runner.load_test_dataset()  # Gọi hàm nạp dữ liệu từ file CSV, trả về danh sách các câu hỏi đã được parse

    assert len(dataset) == 683, f"Kỳ vọng 683 câu hỏi, nhưng đọc được {len(dataset)}"  # Kiểm tra số lượng câu hỏi nạp được phải đúng bằng 683
    
    first_item = dataset[0]  # Lấy câu hỏi đầu tiên trong tập dữ liệu để kiểm tra cấu trúc
    assert "id" in first_item, "Mỗi item phải có trường 'id'"  # Kiểm tra mỗi câu hỏi phải có trường 'id' (số thứ tự)
    assert "question" in first_item and len(first_item["question"]) > 0, "Câu hỏi không được rỗng"  # Kiểm tra trường 'question' tồn tại và không rỗng
    assert "ground_truth_answer" in first_item, "Phải có trường 'ground_truth_answer'"  # Kiểm tra phải có trường đáp án chuẩn (ground truth)
    assert "ground_truth_citations" in first_item, "Phải có trường 'ground_truth_citations'"  # Kiểm tra phải có trường danh sách căn cứ pháp lý chuẩn
    print(f"[PASSED] test_benchmark_dataset_loading: Đọc đủ {len(dataset)} câu hỏi.")  # In thông báo test đạt kèm số lượng câu hỏi


##=============================
# 3. Hàm kiểm tra bộ bóc tách căn cứ pháp lý bằng biểu thức chính quy (Regex) có hoạt động chính xác không
##=============================
def test_legal_citation_extraction():
    """
    Kịch bản 3: Kiểm tra bộ bóc tách căn cứ pháp lý (Regex Extraction).
    """
    # Tạo đoạn văn bản mẫu chứa nhiều loại căn cứ pháp lý khác nhau để test
    sample_text = (
        "Căn cứ Điều 6 Nghị định số 168/2024/NĐ-CP và Thông tư số 79/2024/TT-BCA "
        "quy định xử phạt theo Luật Trật tự, an toàn giao thông đường bộ."
    )
    citations = BenchmarkRunner.extract_legal_citations(sample_text)  # Gọi hàm tĩnh bóc tách căn cứ pháp lý từ văn bản mẫu

    assert "Điều 6" in citations, "Chưa bóc tách được 'Điều 6'"  # Kiểm tra đã trích xuất được Điều luật
    assert "Nghị định 168/2024/NĐ-CP" in citations, "Chưa bóc tách được 'Nghị định 168/2024/NĐ-CP'"  # Kiểm tra đã trích xuất được Nghị định
    assert "Thông tư 79/2024/TT-BCA" in citations, "Chưa bóc tách được 'Thông tư 79/2024/TT-BCA'"  # Kiểm tra đã trích xuất được Thông tư
    assert "Luật Trật tự, an toàn giao thông đường bộ" in citations, "Chưa bóc tách được tên Luật"  # Kiểm tra đã trích xuất được tên Luật
    print(f"[PASSED] test_legal_citation_extraction: Trích xuất chính xác {len(citations)} căn cứ.")  # In thông báo test đạt kèm số căn cứ


##=============================
# 4. Hàm kiểm tra tính toán các chỉ số đo lường Hit-rate, Recall@K, MRR theo công thức toán học chuẩn
##=============================
def test_retrieval_metrics_calculation():
    """
    Kịch bản 4: Kiểm tra tính toán chỉ số Hit-rate, Recall@K, MRR theo công thức chuẩn.
    """
    runner = BenchmarkRunner()  # Khởi tạo BenchmarkRunner với cấu hình mặc định

    # Dữ liệu chuẩn có 2 căn cứ: 'Điều 6' và 'Nghị định 168/2024/NĐ-CP'
    item = {
        "ground_truth_citations": ["Điều 6", "Nghị định 168/2024/NĐ-CP"],  # Danh sách căn cứ pháp lý chuẩn (ground truth) cần đối sánh
        "ground_truth_answer": "Quy định tại Điều 6 Nghị định 168..."  # Câu trả lời mẫu chuẩn
    }

    # Giả lập tài liệu truy xuất được:
    # Tài liệu 1: Chứa 'Điều 6' (Trúng 1 căn cứ tại rank 1)
    # Tài liệu 2: Không liên quan
    # Tài liệu 3: Không liên quan
    retrieved_docs = [
        {"title": "Trích lục Điều 6", "snippet": "Xử phạt người điều khiển xe mô tô."},  # Tài liệu giả lập rank 1 - chứa "Điều 6"
        {"title": "Văn bản khác", "snippet": "Nội dung quy định chung."},  # Tài liệu giả lập rank 2 - không liên quan
        {"title": "Quy chuẩn", "snippet": "Biển báo hiệu đường bộ."}  # Tài liệu giả lập rank 3 - không liên quan
    ]

    metrics = runner.calculate_metrics_for_query(item, retrieved_docs)  # Gọi hàm tính toán các chỉ số cho 1 câu hỏi

    assert metrics["hit"] == 1.0, "Kỳ vọng Hit = 1.0"  # Kiểm tra Hit = 1.0 (vì có ít nhất 1 căn cứ trúng trong Top-3)
    assert metrics["recall"] == 0.5, f"Kỳ vọng Recall = 0.5 (1/2), nhận được {metrics['recall']}"  # Kiểm tra Recall = 0.5 (tìm trúng 1 trong tổng 2 căn cứ = 1/2)
    assert metrics["first_rank"] == 1, "Kỳ vọng rank đầu tiên = 1"  # Kiểm tra tài liệu đúng đầu tiên xuất hiện ở vị trí rank 1
    assert metrics["reciprocal_rank"] == 1.0, "Kỳ vọng MRR = 1.0 (1/1)"  # Kiểm tra MRR = 1/1 = 1.0 (vì rank đầu tiên = 1)
    print("[PASSED] test_retrieval_metrics_calculation: Các công thức toán học chính xác 100%.")  # In thông báo test đạt


if __name__ == "__main__":
    print("=" * 60)
    print("CHẠY BỘ UNIT TEST TỰ ĐỘNG CHO PHÂN HỆ EVALUATION & RAG")
    print("=" * 60)
    test_rag_dummy_response()  # Chạy kịch bản kiểm thử 1
    test_benchmark_dataset_loading()  # Chạy kịch bản kiểm thử 2
    test_legal_citation_extraction()  # Chạy kịch bản kiểm thử 3
    test_retrieval_metrics_calculation()  # Chạy kịch bản kiểm thử 4
    print("=" * 60)
    print("TẤT CẢ UNIT TESTS ĐÃ VƯỢT QUA XUẤT SẮC! [ALL PASSED]")
    print("=" * 60)
