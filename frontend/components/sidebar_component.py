"""Thanh điều hướng Sidebar (270px)"""

import streamlit as st
from streamlit.components.v2 import component
from frontend.utils import load_svg

LOGO_SVG = load_svg("Chatbot_Logo.svg", color="#FFFFFF")

SIDEBAR_HTML = f"""
<aside class="w-[270px] shrink-0 bg-sidebar border-r border-subtle flex flex-col justify-between h-full select-none z-20">
  <div class="flex flex-col p-3 overflow-y-auto">
    <!-- Logo & Brand Header -->
    <div class="flex items-center gap-2.5 px-2 py-2 mb-2">
      <div class="brand-logo-box w-9 h-9 rounded-xl bg-accent-red flex items-center justify-center shrink-0 shadow-sm overflow-hidden" title="VinaLaw-Traffic">
        {LOGO_SVG}
      </div>
      <div class="flex flex-col">
        <span class="font-bold text-[15px] tracking-tight text-primary-navy leading-none">VinaLaw-Traffic</span>
        <span class="text-[11px] text-text-muted font-medium mt-1">Trợ lý AI Luật Giao thông</span>
      </div>
    </div>

    <!-- New Chat Button -->
    <button id="btn-new-chat" class="flex items-center gap-3 w-full px-4 py-2.5 rounded-full bg-white border border-transparent hover:border-accent-red shadow-xs hover:shadow-sm text-text-main transition-colors duration-200 mb-4 text-left group">
      <span class="material-symbols-outlined text-[20px] text-accent-red">add</span>
      <span class="text-[13px] font-semibold text-slate-800">Cuộc trò chuyện mới</span>
    </button>

    <!-- Main Navigation Tabs -->
    <nav class="flex flex-col gap-1 mb-5" id="sidebarNav">
      <button data-tab="chat" class="tab-item flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all">
        <span class="nav-icon material-symbols-outlined text-[18px]">smart_toy</span>
        <span class="nav-label">Trợ lý AI</span>
      </button>

      <button data-tab="docs" class="tab-item flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all">
        <span class="nav-icon material-symbols-outlined text-[18px]">menu_book</span>
        <span class="nav-label">Tra cứu Văn bản Pháp luật</span>
      </button>

      <button data-tab="faq" class="tab-item flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all">
        <span class="nav-icon material-symbols-outlined text-[18px]">help_center</span>
        <span class="nav-label">Câu hỏi thường gặp</span>
      </button>
    </nav>

    <!-- History Section: Single Session with 3-dot dropdown menu on the LEFT on hover -->
    <div class="flex flex-col">
      <div class="flex items-center justify-between px-2.5 py-1 mb-1.5 text-slate-500">
        <span class="text-[11px] font-bold tracking-wider uppercase">Lịch sử trò chuyện</span>
        <span class="material-symbols-outlined text-[16px] cursor-pointer hover:text-text-main">expand_more</span>
      </div>

      <!-- TODO: [Single Session] Hiện tại đang hardcode 1 phiên cho bước single session -->
      <div class="relative flex flex-col gap-0.5" id="historySessions">
        <div class="group relative flex items-center w-full px-2 py-1.5 rounded-lg hover:bg-white/70 transition-all text-[12.5px] text-slate-700">
          <!-- Icon 3 chấm dọc ở bên TRÁI khi hover -->
          <button id="btn-session-menu" class="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-slate-200/80 text-slate-500 hover:text-slate-800 transition-opacity shrink-0 mr-1.5 flex items-center justify-center" title="Tùy chọn phiên">
            <span class="material-symbols-outlined text-[16px]">more_vert</span>
          </button>
          <span class="truncate cursor-pointer flex-1" id="session-title">Rẽ phải khi đèn đỏ</span>
        </div>

        <!-- Vertical Dropdown Menu -->
        <div id="sessionDropdownMenu" class="hidden absolute left-2 top-8 z-50 w-36 bg-white rounded-lg shadow-lg border border-slate-200 py-1 flex flex-col text-[12px] text-slate-700">
          <button data-action="pin" class="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors">
            <span class="material-symbols-outlined text-[16px] text-slate-500">push_pin</span>
            <span>Ghim</span>
          </button>
          <button data-action="rename" class="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors">
            <span class="material-symbols-outlined text-[16px] text-slate-500">edit</span>
            <span>Đổi tên</span>
          </button>
          <button data-action="delete" class="flex items-center gap-2 px-3 py-1.5 hover:bg-red-50 text-red-600 text-left transition-colors border-t border-slate-100">
            <span class="material-symbols-outlined text-[16px] text-red-500">delete</span>
            <span>Xóa</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Sidebar Footer: Account / Login Navigation -->
  <div class="p-3 border-t border-subtle">
    <button data-tab="login" class="tab-item flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all group">
      <span class="nav-icon material-symbols-outlined text-[18px]">account_circle</span>
      <span class="nav-label">Đăng nhập tài khoản</span>
    </button>
  </div>
</aside>
"""

SIDEBAR_JS = """
export default function(component) {
  const { data, parentElement, setTriggerValue } = component;
  const activeTab = (data && data.active_tab) || 'chat';
  const sessionTitle = (data && data.session_title) || 'Rẽ phải khi đèn đỏ';

  // Cập nhật tiêu đề phiên
  const titleEl = parentElement.querySelector('#session-title');
  if (titleEl) titleEl.textContent = sessionTitle;

  // Cập nhật trạng thái Tab Active / Inactive
  const tabs = parentElement.querySelectorAll('.tab-item');
  tabs.forEach(btn => {
    const tabName = btn.getAttribute('data-tab');
    const icon = btn.querySelector('.nav-icon');
    if (tabName === activeTab) {
      btn.className = "tab-item tab-active flex items-center gap-2.5 px-3 py-2 rounded-xl bg-white text-primary-navy font-bold shadow-xs border border-slate-200/60 text-[13px] w-full text-left transition-all";
      icon.className = "nav-icon material-symbols-outlined text-[18px] text-accent-red icon-filled";
    } else {
      btn.className = "tab-item flex items-center gap-2.5 px-3 py-2 rounded-xl text-text-muted hover:text-text-main hover:bg-white/60 text-[13px] w-full text-left transition-all group";
      icon.className = "nav-icon material-symbols-outlined text-[18px] group-hover:text-accent-red transition-colors";
    }

    btn.onclick = (e) => {
      e.preventDefault();
      setTriggerValue('tab_change', tabName);
    };
  });

  // Nút Cuộc trò chuyện mới
  const newChatBtn = parentElement.querySelector('#btn-new-chat');
  if (newChatBtn) {
    newChatBtn.onclick = (e) => {
      e.preventDefault();
      setTriggerValue('session_action', { action: 'new_chat' });
    };
  }

  // Menu 3 chấm phiên chat
  const menuBtn = parentElement.querySelector('#btn-session-menu');
  const dropdown = parentElement.querySelector('#sessionDropdownMenu');
  if (menuBtn && dropdown) {
    menuBtn.onclick = (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('hidden');
    };
  }

  // Các nút trong dropdown menu
  if (dropdown) {
    dropdown.querySelectorAll('button[data-action]').forEach(actionBtn => {
      actionBtn.onclick = (e) => {
        e.stopPropagation();
        const action = actionBtn.getAttribute('data-action');
        dropdown.classList.add('hidden');
        if (action === 'rename') {
          const newName = prompt('Đổi tên cuộc trò chuyện:', sessionTitle);
          if (newName && newName.trim()) {
            setTriggerValue('session_action', { action: 'rename', title: newName.trim() });
          }
        } else {
          setTriggerValue('session_action', { action: action });
        }
      };
    });
  }

  // Click ngoài đóng dropdown
  document.addEventListener('click', () => {
    if (dropdown && !dropdown.classList.contains('hidden')) {
      dropdown.classList.add('hidden');
    }
  });
}
"""

_SIDEBAR_COMPONENT = component(
    name="vinalaw_sidebar",
    html=SIDEBAR_HTML,
    js=SIDEBAR_JS,
    isolate_styles=False
)

def render_sidebar(active_tab: str = "chat", session_title: str = "Rẽ phải khi đèn đỏ", key: str = "sidebar_comp"):
    """Mount component sidebar và lắng nghe sự kiện đổi tab / thao tác phiên."""
    result = _SIDEBAR_COMPONENT(
        key=key,
        data={
            "active_tab": active_tab,
            "session_title": session_title
        },
        on_tab_change_change=lambda: None,
        on_session_action_change=lambda: None
    )
    return result
