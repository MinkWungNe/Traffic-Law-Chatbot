"""
Module: test_api.py
Mục đích: Kiểm thử tự động (Unit Test & Integration Test) toàn diện cho phân hệ API FastAPI.
Người phụ trách: Thành viên 3 (Backend API Lead)
"""

from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)

def test_root_endpoint():
    """Kiểm tra Endpoint gốc trả về thông tin hệ thống và danh mục endpoints."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "endpoints" in data
    print("[PASSED] test_root_endpoint: SUCCESS")

def test_health_check_endpoint():
    """Kiểm tra Endpoint kiểm tra sức khỏe hệ thống /api/health."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data
    print("[PASSED] test_health_check_endpoint: SUCCESS")

def test_chat_query_and_cache():
    """Kiểm tra xử lý câu hỏi RAG và cơ chế Cache phản hồi tức thì."""
    payload = {
        "query": "Quy định mức phạt vượt đèn đỏ đối với xe máy?",
        "top_k": 3,
        "temperature": 0.2
    }
    # Lần 1: Xử lý RAG (Chưa lưu cache)
    res1 = client.post("/api/chat", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["cached"] is False
    assert len(data1["sources"]) > 0

    # Lần 2: Truy vấn lại cùng câu hỏi (Phải trả về từ Cache < 0.1s)
    res2 = client.post("/api/chat", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["cached"] is True
    assert data2["query"] == payload["query"]
    print(f"[PASSED] test_chat_query_and_cache: SUCCESS (Cache Hit latency: {data2.get('execution_time_ms')}ms)")

def test_chat_validation_min_length():
    """Kiểm tra xử lý lỗi khi câu hỏi dưới 2 ký tự (HTTP 422)."""
    res = client.post("/api/chat", json={"query": "?"})
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data
    print("[PASSED] test_chat_validation_min_length: SUCCESS")

def test_search_sources_endpoint():
    """Kiểm tra tính năng trích xuất nhanh căn cứ pháp lý /api/search."""
    res = client.post("/api/search", json={"query": "nồng độ cồn", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["sources"]) > 0
    print("[PASSED] test_search_sources_endpoint: SUCCESS")

def test_legal_documents_endpoint():
    """Kiểm tra Endpoint danh mục văn bản luật /api/documents."""
    res = client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 6
    assert len(data["documents"]) >= 6
    print("[PASSED] test_legal_documents_endpoint: SUCCESS")

if __name__ == "__main__":
    print("=== BẮT ĐẦU CHẠY KIỂM THỬ API FASTAPI ===")
    test_root_endpoint()
    test_health_check_endpoint()
    test_chat_query_and_cache()
    test_chat_validation_min_length()
    test_search_sources_endpoint()
    test_legal_documents_endpoint()
    print("=== TẤT CẢ CÁC BÀI TEST API ĐÃ VƯỢT QUA 100% ===")
