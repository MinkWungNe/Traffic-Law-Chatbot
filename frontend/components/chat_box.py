"""
Module: chat_box.py
Mục đích: Chứa các hàm render bong bóng chat và trích dẫn văn bản luật trên giao diện Streamlit.
Người phụ trách chính: Thành viên 3 (Frontend Web Lead)
"""

import streamlit as st
from typing import List, Dict, Any

def render_chat_message(role: str, content: str, sources: List[Dict[str, Any]] = None):
    """
    Hiển thị một tin nhắn trong luồng chat kèm hộp căn cứ pháp lý mở rộng.
    Args:
        role (str): 'user' hoặc 'assistant'.
        content (str): Nội dung văn bản câu hỏi / câu trả lời.
        sources (List[Dict[str, Any]]): Danh sách tài liệu tham khảo (nếu có).
    """
    with st.chat_message(role):
        st.markdown(content)
        if sources:
            with st.expander("📚 Căn cứ pháp lý trích dẫn"):
                for src in sources:
                    st.markdown(f"- **{src.get('title', 'Tài liệu')}**: {src.get('snippet', '')}")
