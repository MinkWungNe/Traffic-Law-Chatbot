"""Màn hình lỗi 404 (404Page)"""

import streamlit as st
from streamlit.components.v2 import component
from frontend.utils import load_svg

CARCRASH_SVG = load_svg("CarCrash.svg", color="#1C3D6E", class_name="w-full h-full object-contain")

NOT_FOUND_HTML = f"""
<div class="flex-1 flex flex-col items-center justify-center p-6 w-full h-full relative overflow-hidden select-none">
  <!-- Hiệu ứng Ambient Glow -->
  <div class="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center">
    <div class="w-[600px] h-[400px] bg-gradient-to-tr from-blue-100/40 via-red-50/30 to-amber-50/20 rounded-full blur-3xl opacity-75 transform -translate-y-6"></div>
  </div>

  <div class="relative z-10 w-full max-w-2xl flex flex-col items-center text-center">
    <!-- 4 [CarCrash SVG #1C3D6E] 4 -->
    <div class="relative flex items-center justify-center select-none my-2">
      <div class="flex items-center text-[100px] sm:text-[128px] font-bold tracking-tighter text-primary-navy leading-none">
        <span>4</span>
        <div class="carcrash-box mx-3 sm:mx-5 flex items-center justify-center w-24 h-24 sm:w-28 sm:h-28">
          {CARCRASH_SVG}
        </div>
        <span>4</span>
      </div>
    </div>

    <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mb-2">Không tìm thấy trang yêu cầu</h1>
    <p class="text-sm sm:text-base text-slate-500 max-w-md mb-8">Đường dẫn bạn đang tìm kiếm không tồn tại hoặc đã bị thay đổi vị trí.</p>

    <!-- 3 Action CTAs -->
    <div class="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
      <button data-nav="chat" class="btn-nav-404 w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-accent-red text-white font-semibold text-sm shadow-xs hover:bg-red-700 transition-all">
        <span class="material-symbols-outlined text-[18px] text-white icon-filled">smart_toy</span>
        <span>Về Trợ lý AI</span>
      </button>
      <button data-nav="docs" class="btn-nav-404 w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:text-primary-navy hover:border-slate-300 font-semibold text-sm shadow-xs hover:bg-slate-50 transition-all">
        <span class="material-symbols-outlined text-[18px] text-slate-500">menu_book</span>
        <span>Tra cứu Văn bản Pháp luật</span>
      </button>
      <button data-nav="faq" class="btn-nav-404 w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:text-primary-navy hover:border-slate-300 font-semibold text-sm shadow-xs hover:bg-slate-50 transition-all">
        <span class="material-symbols-outlined text-[18px] text-slate-500">help_center</span>
        <span>Tra cứu câu hỏi thường gặp</span>
      </button>
    </div>
  </div>
</div>
"""

NOT_FOUND_JS = """
export default function(component) {
  const { parentElement, setTriggerValue } = component;
  parentElement.querySelectorAll('.btn-nav-404').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      const tab = btn.getAttribute('data-nav');
      setTriggerValue('nav_to_tab', tab);
    };
  });
}
"""

_NOT_FOUND_COMPONENT = component(
    name="vinalaw_404",
    html=NOT_FOUND_HTML,
    js=NOT_FOUND_JS,
    isolate_styles=False
)

def render_not_found(key: str = "not_found_comp"):
    """Mount component Màn hình 404 và bắt sự kiện nav_to_tab."""
    result = _NOT_FOUND_COMPONENT(
        key=key,
        on_nav_to_tab_change=lambda: None
    )
    return result
