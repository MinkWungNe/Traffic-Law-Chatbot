"""Khung nhập liệu Chat Dock nổi cho trợ lý AI."""

import streamlit as st
from streamlit.components.v2 import component

CHAT_DOCK_HTML = """
<div class="w-full max-w-3xl mx-auto px-4 pb-4 select-none">
  <form id="chatDockForm" class="bg-white border border-subtle rounded-2xl shadow-lg px-3.5 py-2.5 flex flex-col gap-1 focus-within:border-slate-300 transition-all">
    <div class="flex items-center gap-2">
      <!-- Nút đính kèm file -->
      <button id="btn-attach" type="button" class="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0" title="Đính kèm tệp">
        <span class="material-symbols-outlined text-[20px]">attach_file</span>
      </button>

      <!-- Nút tải ảnh hiện trường -->
      <button id="btn-photo" type="button" class="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0" title="Tải ảnh hiện trường">
        <span class="material-symbols-outlined text-[20px]">add_photo_alternate</span>
      </button>

      <!-- Ô nhập câu hỏi -->
      <input id="chatInputText" type="text" autocomplete="off" class="w-full bg-transparent border-0 text-[14px] text-slate-900 placeholder:text-slate-400 focus:ring-0 focus:outline-none px-2 py-1" placeholder="Hỏi VinaLaw về luật giao thông, mức phạt, biển báo..." />

      <!-- Nút gửi đỏ tròn -->
      <button id="btn-send-chat" type="submit" class="w-8 h-8 rounded-full bg-accent-red hover:bg-red-700 text-white flex items-center justify-center transition-transform hover:scale-105 shrink-0 shadow-xs" title="Gửi câu hỏi">
        <span class="material-symbols-outlined text-[17px]">arrow_upward</span>
      </button>
    </div>
  </form>
  <p class="text-center text-[11px] text-slate-400 mt-2">
    VinaLaw-Traffic có thể đưa ra kết quả tham khảo. Vui lòng đối chiếu với văn bản pháp luật hiện hành.
  </p>
</div>
"""

CHAT_DOCK_JS = """
export default function(component) {
  const { data, parentElement, setTriggerValue } = component;
  const form = parentElement.querySelector('#chatDockForm');
  const input = parentElement.querySelector('#chatInputText');
  const attachBtn = parentElement.querySelector('#btn-attach');
  const photoBtn = parentElement.querySelector('#btn-photo');

  // Điền prompt nếu có
  if (data && data.fill_text && input) {
    input.value = data.fill_text;
    input.focus();
  }

  if (form && input) {
    form.onsubmit = (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      setTriggerValue('submit_query', text);
      input.value = '';
    };
  }

  if (attachBtn) {
    attachBtn.onclick = (e) => {
      e.preventDefault();
      alert('Tính năng tải đính kèm hồ sơ, biên bản đang được phát triển.');
    };
  }

  if (photoBtn) {
    photoBtn.onclick = (e) => {
      e.preventDefault();
      alert('Tính năng phân tích hình ảnh hiện trường vi phạm đang được phát triển.');
    };
  }
}
"""

_CHAT_DOCK_COMPONENT = component(
    name="vinalaw_chat_dock",
    html=CHAT_DOCK_HTML,
    js=CHAT_DOCK_JS,
    isolate_styles=False
)

def render_chat_dock(fill_text: str = "", key: str = "chat_dock_comp"):
    """Mount component thanh nhập liệu chat dock và bắt sự kiện submit_query."""
    result = _CHAT_DOCK_COMPONENT(
        key=key,
        data={"fill_text": fill_text},
        on_submit_query_change=lambda: None
    )
    return result
