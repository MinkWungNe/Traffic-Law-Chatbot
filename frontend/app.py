import os
import requests
import streamlit as st
from components.sidebar import render_sidebar

# 1. Cấu hình trang
st.set_page_config(
    page_title="AI Tư Vấn Luật Giao Thông",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tải CSS tùy biến (nếu có)
css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Render Sidebar và lấy tham số cấu hình
config = render_sidebar()

# 4. Tiêu đề ứng dụng
st.title("🚦 Trợ Lý Tư Vấn Luật Giao Thông Đường Bộ")
st.markdown("Hệ thống hỏi đáp pháp luật giao thông ứng dụng **RAG (Retrieval-Augmented Generation)**.")

# 5. Khởi tạo lịch sử chat trong Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Xin chào! Tôi có thể giúp bạn tra cứu quy định pháp luật giao thông đường bộ, mức phạt vi phạm, hoặc thủ tục giấy tờ. Bạn có câu hỏi gì cần hỗ trợ?",
            "sources": []
        }
    ]

# 6. Hiển thị lịch sử hội thoại
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Căn cứ pháp lý trích dẫn"):
                for src in msg["sources"]:
                    st.markdown(f"- **{src.get('title', 'Tài liệu')}**: {src.get('snippet', '')}")

# 7. Xử lý câu hỏi người dùng
user_query = st.chat_input("Nhập câu hỏi của bạn (ví dụ: Vượt đèn đỏ xe máy phạt bao nhiêu tiền?)...")

if user_query:
    # Lưu và hiển thị câu hỏi của người dùng
    st.session_state["messages"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Phản hồi từ trợ lý AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Đang tra cứu cơ sở dữ liệu luật và phân tích...*")
        
        bot_response = ""
        sources = []

        try:
            # Gửi yêu cầu tới FastAPI Backend
            endpoint = f"{config['backend_url']}/api/chat"
            payload = {
                "query": user_query,
                "top_k": config["top_k"],
                "temperature": config["temperature"]
            }
            res = requests.post(endpoint, json=payload, timeout=30)
            
            if res.status_code == 200:
                data = res.json()
                bot_response = data.get("answer", "Không tìm thấy câu trả lời phù hợp.")
                sources = data.get("sources", [])
            else:
                bot_response = f"⚠️ Lỗi từ máy chủ Backend (Mã lỗi: {res.status_code})."
        except requests.exceptions.ConnectionError:
            # Chế độ Mock / Fallback khi Backend chưa khởi chạy
            bot_response = (
                "⚠️ **Chưa kết nối được với FastAPI Backend** (mặc định tại `http://localhost:8000`).\n\n"
                "*(Khung giao diện đang chạy ở chế độ kiểm thử cục bộ. Vui lòng bật backend bằng lệnh: "
                "`uvicorn app.main:app --reload` trong thư mục `backend/` để kích hoạt RAG hoàn chỉnh.)*\n\n"
                f"**Câu hỏi đã ghi nhận:** \"{user_query}\""
            )
        except Exception as e:
            bot_response = f"⚠️ Đã xảy ra lỗi: {str(e)}"

        message_placeholder.markdown(bot_response)
        
        if sources:
            with st.expander("📚 Căn cứ pháp lý trích dẫn"):
                for src in sources:
                    st.markdown(f"- **{src.get('title', 'Tài liệu')}**: {src.get('snippet', '')}")

        # Lưu câu trả lời của trợ lý vào lịch sử
        st.session_state["messages"].append({
            "role": "assistant",
            "content": bot_response,
            "sources": sources
        })
