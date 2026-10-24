"""Điểm khởi chạy chính của ứng dụng Frontend Streamlit (VinaLaw-Traffic)."""

import sys
from pathlib import Path

# Đảm bảo thư mục gốc dự án luôn nằm trong sys.path để import 'frontend....' chuẩn xác
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from frontend.components.sidebar_component import render_sidebar
from frontend.components.chat_dock_component import render_chat_dock
from frontend.components.chat_message_component import render_chat_messages
from frontend.components.legal_docs_component import render_legal_docs
from frontend.components.faq_component import render_faq
from frontend.components.not_found_component import render_not_found
from frontend.components.login_component import render_login
from frontend.services import query_chat_api

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="VinaLaw-Traffic - Trợ lý AI Luật Giao thông",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Nạp Thư viện Giao diện (Google Fonts, Material Symbols, Tailwind CSS CDN & Cấu hình Theme)
CDN_HEAD_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        colors: {
          "canvas": "#F8FAFD",
          "surface": "#FFFFFF",
          "sidebar": "#F0F4F9",
          "subtle": "#E2E8F0",
          "border-subtle": "#E2E8F0",
          "primary-navy": "#1C3D6E",
          "accent-red": "#B91C1C",
          "accent-gold": "#D97706",
          "text-main": "#0F172A",
          "text-muted": "#64748B"
        },
        fontFamily: {
          sans: ["Be Vietnam Pro", "sans-serif"]
        }
      }
    }
  };
</script>
"""
st.html(CDN_HEAD_HTML, unsafe_allow_javascript=True)

# Nạp CSS tập trung chuẩn Streamlit 1.65.0 qua st.html(pathlib.Path)
CSS_PATH = Path(__file__).resolve().parent / "styles" / "style.css"
if CSS_PATH.exists():
    st.html(CSS_PATH)

# 3. Khởi tạo State trong st.session_state
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "login"

if "session_title" not in st.session_state:
    st.session_state["session_title"] = "Rẽ phải khi đèn đỏ"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "fill_text" not in st.session_state:
    st.session_state["fill_text"] = ""

def process_query(user_query: str):
    """Xử lý câu hỏi người dùng, gọi FastAPI Backend và cập nhật lịch sử chat."""
    if not user_query or not user_query.strip():
        return
    query = user_query.strip()
    st.session_state["messages"].append({"role": "user", "content": query})

    # Gọi Backend API tập trung qua api_client (hỗ trợ cả live API lẫn fallback)
    api_res = query_chat_api(query)
    bot_content = api_res.get("answer", "")
    sources = api_res.get("sources", [])

    st.session_state["messages"].append({
        "role": "assistant",
        "content": bot_content,
        "sources": sources,
        "render_mode": "markdown"  # Mặc định render markdown chuẩn, có thể chuyển sang "structured" khi cần
    })

# 4. Hiển thị Giao diện theo Tab hiện tại
current_tab = st.session_state["current_tab"]

if current_tab == "login":
    # 4.A. Màn hình Đăng nhập (Full Screen 4 Layers)
    login_res = render_login(key="vinalaw_login_key")
    if login_res and login_res.login_success:
        st.session_state["current_tab"] = "chat"
        st.session_state["user_profile"] = login_res.login_success
        st.rerun()

else:
    # 4.B. Bố cục 2 cột ngang: Sidebar cố định 270px bên trái, Main Content bên phải
    with st.container(horizontal=True, wrap=False):
        # Cột Trái: Sidebar Component
        sidebar_res = render_sidebar(
            active_tab=st.session_state["current_tab"],
            session_title=st.session_state["session_title"],
            key="vinalaw_sidebar_key"
        )

        # Cột Phải: Main View
        with st.container():
            if current_tab == "chat":
                chat_msg_res = render_chat_messages(
                    messages=st.session_state["messages"],
                    key="vinalaw_chat_messages_key"
                )
                chat_dock_res = render_chat_dock(
                    fill_text=st.session_state["fill_text"],
                    key="vinalaw_chat_dock_key"
                )

                # Xử lý khi bấm thẻ gợi ý ban đầu hoặc follow-up chip
                if chat_msg_res and chat_msg_res.starter_prompt:
                    prompt_to_send = chat_msg_res.starter_prompt
                    st.session_state["fill_text"] = ""
                    process_query(prompt_to_send)
                    st.rerun()

                # Xử lý khi gửi câu hỏi từ thanh chat dock
                if chat_dock_res and chat_dock_res.submit_query:
                    query_to_send = chat_dock_res.submit_query
                    st.session_state["fill_text"] = ""
                    process_query(query_to_send)
                    st.rerun()

            elif current_tab == "docs":
                docs_res = render_legal_docs(key="vinalaw_legal_docs_key")
                if docs_res and docs_res.ask_doc_trigger:
                    doc_query = docs_res.ask_doc_trigger
                    st.session_state["current_tab"] = "chat"
                    process_query(f"Quy định chi tiết và các điểm cần lưu ý về: {doc_query}")
                    st.rerun()

            elif current_tab == "faq":
                faq_res = render_faq(key="vinalaw_faq_key")
                if faq_res and faq_res.ask_faq_trigger:
                    faq_query = faq_res.ask_faq_trigger
                    st.session_state["current_tab"] = "chat"
                    process_query(faq_query)
                    st.rerun()

            elif current_tab == "404":
                not_found_res = render_not_found(key="vinalaw_404_key")
                if not_found_res and not_found_res.nav_to_tab:
                    st.session_state["current_tab"] = not_found_res.nav_to_tab
                    st.rerun()

    # 5. Xử lý sự kiện từ Sidebar
    if sidebar_res:
        # Sự kiện đổi tab
        if sidebar_res.tab_change and sidebar_res.tab_change != st.session_state["current_tab"]:
            st.session_state["current_tab"] = sidebar_res.tab_change
            st.rerun()

        # Sự kiện thao tác phiên (new_chat / pin / rename / delete)
        if sidebar_res.session_action:
            act = sidebar_res.session_action
            action_type = act.get("action") if isinstance(act, dict) else act
            if action_type == "new_chat":
                st.session_state["messages"] = []
                st.session_state["current_tab"] = "chat"
                st.session_state["fill_text"] = ""
                st.rerun()
            elif action_type == "rename":
                new_title = act.get("title") if isinstance(act, dict) else ""
                if new_title:
                    st.session_state["session_title"] = new_title
                    st.rerun()
            elif action_type == "delete":
                st.session_state["messages"] = []
                st.session_state["current_tab"] = "chat"
                st.rerun()
