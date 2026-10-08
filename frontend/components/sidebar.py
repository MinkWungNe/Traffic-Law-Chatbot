import streamlit as st

def render_sidebar():
    """
    Render sidebar cấu hình hệ thống và tùy chọn tham số RAG.
    """
    with st.sidebar:
        st.title("⚙️ Cấu hình hệ thống")
        
        # Cấu hình kết nối Backend
        st.subheader("1. Kết nối API")
        backend_url = st.text_input(
            "Backend URL", 
            value="http://localhost:8000",
            help="Địa chỉ FastAPI Backend đang chạy"
        )
        
        # Tham số RAG
        st.subheader("2. Tham số RAG")
        top_k = st.slider(
            "Số tài liệu truy xuất (Top-K)", 
            min_value=1, 
            max_value=10, 
            value=3,
            help="Số đoạn văn bản luật được lấy để làm ngữ cảnh"
        )
        temperature = st.slider(
            "Độ sáng tạo (Temperature)", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.2, 
            step=0.05,
            help="Giá trị càng thấp câu trả lời càng bám sát văn bản luật"
        )
        
        # Thao tác hội thoại
        st.subheader("3. Thao tác")
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Xin chào! Tôi là Trợ lý AI Tư vấn Pháp luật An toàn Giao thông. Bạn cần tra cứu quy định hoặc mức phạt nào?"
                }
            ]
            st.rerun()

        st.divider()
        st.caption("📌 **Đồ án:** Chatbot AI Tư vấn An toàn Giao thông")
        st.caption("🤖 **Mô hình:** VinaLlama + ChromaDB + LangChain")

    return {
        "backend_url": backend_url,
        "top_k": top_k,
        "temperature": temperature
    }
