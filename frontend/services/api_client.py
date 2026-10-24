"""
Module: api_client.py
Mục đích: Tầng kết nối tập trung giữa Streamlit Frontend và máy chủ FastAPI Backend.
"""

import logging
from typing import Any, Dict, List, Tuple
import requests

logger = logging.getLogger(__name__)

BACKEND_BASE_URL = "http://localhost:8000"

def check_backend_health(base_url: str = BACKEND_BASE_URL) -> bool:
    """Kiểm tra máy chủ FastAPI Backend có đang hoạt động hay không."""
    try:
        res = requests.get(f"{base_url}/api/health", timeout=2)
        return res.status_code == 200
    except Exception:
        return False

def query_chat_api(
    query: str,
    top_k: int = 3,
    temperature: float = 0.2,
    base_url: str = BACKEND_BASE_URL,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Gửi câu hỏi người dùng đến FastAPI endpoint /api/chat.
    Trả về dict dạng:
      {
        "answer": str (văn bản markdown),
        "sources": list (danh sách trích dẫn),
        "is_fallback": bool
      }
    """
    url = f"{base_url}/api/chat"
    payload = {
        "query": query,
        "top_k": top_k,
        "temperature": temperature
    }
    try:
        res = requests.post(url, json=payload, timeout=timeout)
        if res.status_code == 200:
            data = res.json()
            return {
                "answer": data.get("answer", ""),
                "sources": data.get("sources", []),
                "is_fallback": False
            }
        logger.warning(f"Backend trả về mã lỗi: {res.status_code}")
    except Exception as e:
        logger.info(f"Không thể kết nối FastAPI backend ({e}), chuyển sang fallback offline.")

    # Fallback Markdown chuẩn khi Backend chưa khởi động
    fallback_answer, fallback_sources = _get_offline_fallback(query)
    return {
        "answer": fallback_answer,
        "sources": fallback_sources,
        "is_fallback": True
    }

def _get_offline_fallback(query: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Tạo câu trả lời Markdown mẫu chuẩn luật khi Backend đang offline."""
    q_lower = query.lower()
    if "rẽ phải" in q_lower or "đèn đỏ" in q_lower:
        answer = (
            "### Kết luận: Không được phép rẽ phải khi đèn đỏ\n\n"
            "Khi ngã tư có tín hiệu đèn đỏ mà **không có biển báo phụ** (như biển *\"Đèn đỏ được phép rẽ phải\"*), "
            "không có đèn mũi tên xanh và không có hiệu lệnh của CSGT, người điều khiển xe máy **bắt buộc phải dừng trước vạch dừng xe**.\n\n"
            "#### Khung hình phạt áp dụng:\n"
            "- **Phạt tiền trực tiếp:** **800.000đ – 1.000.000đ** (Mức phổ biến áp dụng: **900.000 VNĐ**).\n"
            "- **Hình thức phạt bổ sung:** Tước quyền sử dụng Giấy phép lái xe từ **01 đến 03 tháng** (Nếu gây TNGT: Tước **02 – 04 tháng**).\n"
            "- **Tạm giữ phương tiện:** Không tạm giữ nếu người điều khiển xuất trình đủ giấy tờ xe hợp lệ.\n\n"
            "> **Căn cứ pháp lý:** Điểm e Khoản 4 và Điểm b Khoản 10 Điều 6 Nghị định 100/2019/NĐ-CP (sửa đổi, bổ sung bởi Nghị định 123/2021/NĐ-CP)."
        )
        sources = [
            {
                "title": "Điểm e Khoản 4 Điều 6 Nghị định 100/2019/NĐ-CP",
                "snippet": "Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy không chấp hành hiệu lệnh của đèn tín hiệu giao thông.",
                "score": 0.94
            },
            {
                "title": "Nghị định 123/2021/NĐ-CP",
                "snippet": "Bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng; gây tai nạn giao thông tước từ 02 đến 04 tháng.",
                "score": 0.88
            }
        ]
    elif "nồng độ cồn" in q_lower or "rượu" in q_lower:
        answer = (
            "### Kết luận: Nghiêm cấm tuyệt đối nồng độ cồn khi điều khiển phương tiện\n\n"
            "Luật Trật tự, an toàn giao thông đường bộ 2024 nghiêm cấm triệt để hành vi điều khiển phương tiện tham gia giao thông "
            "mà trong máu hoặc hơi thở có nồng độ cồn.\n\n"
            "#### Mức xử phạt kịch khung đối với xe máy:\n"
            "- **Phạt tiền:** **6.000.000đ – 8.000.000đ** (khi nồng độ cồn vượt quá 80mg/100ml máu hoặc vượt quá 0.4mg/l khí thở).\n"
            "- **Hình phạt bổ sung:** Tước quyền sử dụng GPLX từ **22 đến 24 tháng**.\n"
            "- **Biện pháp ngăn chặn:** Tạm giữ phương tiện đến **07 ngày làm việc**.\n\n"
            "> **Căn cứ pháp lý:** Điểm e Khoản 8 Điều 6 Nghị định 100/2019/NĐ-CP."
        )
        sources = [
            {
                "title": "Điểm e Khoản 8 Điều 6 Nghị định 100/2019/NĐ-CP",
                "snippet": "Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở.",
                "score": 0.96
            }
        ]
    else:
        answer = (
            f"### Giải đáp quy định pháp luật về: \"{query}\"\n\n"
            "Căn cứ Luật Trật tự, an toàn giao thông đường bộ 2024 và các Nghị định hướng dẫn xử phạt vi phạm hành chính:\n\n"
            "- Mọi hành vi vi phạm trật tự an toàn giao thông đường bộ đều được xử lý theo nguyên tắc đúng người, đúng hành vi, đúng tính chất và mức độ vi phạm.\n"
            "- Người tham gia giao thông có nghĩa vụ chấp hành nghiêm chỉnh hệ thống báo hiệu đường bộ và hiệu lệnh của người điều khiển giao thông.\n\n"
            "> *(Lưu ý: Bạn có thể khởi động máy chủ FastAPI tại cổng 8000 để nhận phân tích chi tiết từ mô hình AI RAG đầy đủ).* "
        )
        sources = [
            {
                "title": "Luật Trật tự, an toàn giao thông đường bộ 2024 (Luật số 36/2024/QH15)",
                "snippet": "Quy tắc chung và quy định chấp hành an toàn giao thông đường bộ.",
                "score": 0.82
            }
        ]
    return answer, sources
