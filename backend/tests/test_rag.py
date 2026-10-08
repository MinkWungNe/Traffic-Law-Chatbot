"""
Module: test_rag.py
Mục đích: Kiểm thử tự động (Unit Test) cho phân hệ RAG và API.
Người phụ trách chính: Thành viên 4 (Evaluation Lead) & Thành viên 2 (RAG Co-dev)
"""

def test_rag_dummy_response():
    """
    Kiểm tra luồng RAG cơ bản trả về cấu trúc câu trả lời hợp lệ.
    """
    from backend.src.rag.rag_pipeline import LegalRAGPipeline
    pipeline = LegalRAGPipeline()
    res = pipeline.answer_question("Vượt đèn đỏ phạt bao nhiêu?")
    assert "answer" in res
    assert "sources" in res
    assert isinstance(res["sources"], list)
    print("[PASSED] test_rag_dummy_response: SUCCESS")

if __name__ == "__main__":
    test_rag_dummy_response()
