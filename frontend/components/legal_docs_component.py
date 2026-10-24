"""Màn hình Tra cứu Văn bản Quy phạm Pháp luật"""

import streamlit as st
from streamlit.components.v2 import component

LEGAL_DOCS_HTML = """
<div class="flex-1 overflow-y-auto px-4 md:px-8 py-8 w-full h-full select-none">
  <div class="max-w-4xl mx-auto flex flex-col gap-6 pb-20">

    <!-- Header -->
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Tra cứu Văn bản Quy phạm Pháp luật</h1>
      <p class="text-sm md:text-base text-slate-600 leading-relaxed">
        Các văn bản luật giao thông đường bộ cốt lõi được hệ thống AI trích xuất, đối soát và tham chiếu trả lời trực tiếp cho công dân.
      </p>
    </div>

    <!-- Search Bar & Category Chips Card -->
    <div class="bg-white rounded-xl p-4 shadow-sm border border-subtle flex flex-col gap-4">
      <div class="relative flex items-center">
        <span class="material-symbols-outlined absolute left-4 text-slate-400 text-[22px] pointer-events-none">search</span>
        <input id="docsSearchInput" type="text" class="w-full bg-[#F8FAFD] text-slate-900 text-sm md:text-base pl-12 pr-12 py-3 rounded-lg border border-subtle focus:outline-none focus:bg-white focus:border-slate-300 transition-all placeholder:text-slate-400" placeholder="Nhập số hiệu văn bản, từ khóa pháp lý (ví dụ: 100/2019, 36/2024, nồng độ cồn)..." />
        <button id="docsClearBtn" type="button" class="absolute right-3 p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors flex items-center justify-center" title="Xóa từ khóa">
          <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>

      <!-- Filter Chips -->
      <div class="flex items-center gap-2 flex-wrap pt-1" id="docsFilterChips">
        <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mr-1">Loại văn bản:</span>
        <button class="doc-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs" data-category="all">
          Tất cả (6)
        </button>
        <button class="doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="luat">
          Luật (2)
        </button>
        <button class="doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="nghi-dinh">
          Nghị định (2)
        </button>
        <button class="doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="thong-tu">
          Thông tư (1)
        </button>
        <button class="doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="quy-chuan">
          Quy chuẩn kỹ thuật (1)
        </button>
      </div>
    </div>

    <!-- TODO: [Legal Documents] Hiện tại đang hardcode dữ liệu danh mục văn bản mẫu -->
    <div class="flex flex-col gap-4" id="docsListContainer">

      <!-- Doc 1: Luật TTATGTĐB 2024 -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="luat" data-keywords="36/2024/qh15 trật tự an toàn giao thông đường bộ 2024 quốc hội">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-blue-50 flex flex-col items-center justify-center shrink-0 text-primary-navy border border-blue-100">
              <span class="material-symbols-outlined text-[24px]">gavel</span>
              <span class="text-[10px] uppercase font-bold text-primary-navy -mt-1">LUẬT</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">Số: 36/2024/QH15</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Hiệu lực từ 01/01/2025
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Quốc hội ban hành</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Luật Trật tự, an toàn giao thông đường bộ 2024</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Quy định quy tắc, phương tiện, người tham gia giao thông đường bộ; chỉ huy, điều khiển, tuần tra, kiểm soát, giải quyết tai nạn giao thông và quản lý trật tự giao thông đường bộ.
              </p>
            </div>
          </div>
          <button data-ask="Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

      <!-- Doc 2: Luật Đường bộ 2024 -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="luat" data-keywords="35/2024/qh15 luật đường bộ 2024 kết cấu hạ tầng quốc hội">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-blue-50 flex flex-col items-center justify-center shrink-0 text-primary-navy border border-blue-100">
              <span class="material-symbols-outlined text-[24px]">gavel</span>
              <span class="text-[10px] uppercase font-bold text-primary-navy -mt-1">LUẬT</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">Số: 35/2024/QH15</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Hiệu lực từ 01/01/2025
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Quốc hội ban hành</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Luật Đường bộ số 35/2024/QH15</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Quy định về hoạt động đường bộ, phát triển kết cấu hạ tầng, vận tải đường bộ và quản lý nhà nước về hoạt động giao thông đường bộ tại Việt Nam.
              </p>
            </div>
          </div>
          <button data-ask="Luật Đường bộ số 35/2024/QH15" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

      <!-- Doc 3: Nghị định 100 & 123 -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="nghi-dinh" data-keywords="100/2019/nđ-cp 123/2021/nđ-cp xử phạt vi phạm hành chính nồng độ cồn tốc độ vượt đèn đỏ">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-red-50 flex flex-col items-center justify-center shrink-0 text-accent-red border border-red-100">
              <span class="material-symbols-outlined text-[24px]">policy</span>
              <span class="text-[9px] uppercase font-bold text-accent-red -mt-1">NGHỊ ĐỊNH</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">Số: 100/2019/NĐ-CP &amp; 123/2021/NĐ-CP</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Đang áp dụng xử phạt
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Chính phủ ban hành</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Nghị định 100/2019/NĐ-CP (sửa đổi, bổ sung bởi NĐ 123/2021/NĐ-CP)</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Quy định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường bộ và đường sắt; khung tiền phạt, tước giấy phép lái xe và tạm giữ phương tiện.
              </p>
            </div>
          </div>
          <button data-ask="Nghị định 100/2019/NĐ-CP và Nghị định 123/2021/NĐ-CP" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

      <!-- Doc 4: Nghị định xử phạt TTATGT 2024 -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="nghi-dinh" data-keywords="168/2024/nđ-cp văn bản hợp nhất xử phạt vi phạm hành chính ttatgt chính phủ">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-red-50 flex flex-col items-center justify-center shrink-0 text-accent-red border border-red-100">
              <span class="material-symbols-outlined text-[24px]">policy</span>
              <span class="text-[9px] uppercase font-bold text-accent-red -mt-1">NGHỊ ĐỊNH</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">Số: 168/2024/NĐ-CP</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Văn bản hợp nhất
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Chính phủ</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Nghị định quy định xử phạt vi phạm hành chính về TTATGT đường bộ</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Văn bản hướng dẫn thi hành các chế tài xử phạt hành chính mới nhất đồng bộ với Luật Trật tự, an toàn giao thông đường bộ 2024.
              </p>
            </div>
          </div>
          <button data-ask="Nghị định 168/2024/NĐ-CP" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

      <!-- Doc 5: Thông tư 73/2024/TT-BCA -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="thong-tu" data-keywords="73/2024/tt-bca tuần tra kiểm soát csgt csgt dừng xe bộ công an">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-amber-50 flex flex-col items-center justify-center shrink-0 text-amber-700 border border-amber-100">
              <span class="material-symbols-outlined text-[24px]">description</span>
              <span class="text-[9px] uppercase font-bold text-amber-700 -mt-1">THÔNG TƯ</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">Số: 73/2024/TT-BCA</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Có hiệu lực
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Bộ Công an</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Thông tư quy định nhiệm vụ, quyền hạn, tuần tra kiểm soát của CSGT</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Quy định quy trình tuần tra kiểm soát, dừng phương tiện giao thông, xử lý vi phạm hành chính và sử dụng phương tiện, thiết bị nghiệp vụ của CSGT.
              </p>
            </div>
          </div>
          <button data-ask="Thông tư 73/2024/TT-BCA của Bộ Công an" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

      <!-- Doc 6: Quy chuẩn QCVN 41 -->
      <article class="doc-item bg-white rounded-xl p-5 md:p-6 shadow-xs hover:shadow-md border border-subtle transition-all" data-category="quy-chuan" data-keywords="qcvn 41:2019/bgtvt quy chuẩn báo hiệu đường bộ biển báo vạch kẻ đường đèn tín hiệu bộ giao thông vận tải">
        <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1">
            <div class="w-12 h-12 rounded-lg bg-indigo-50 flex flex-col items-center justify-center shrink-0 text-indigo-700 border border-indigo-100">
              <span class="material-symbols-outlined text-[24px]">traffic</span>
              <span class="text-[8px] uppercase font-bold text-indigo-700 -mt-1">QUY CHUẨN</span>
            </div>
            <div class="flex flex-col min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <span class="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-bold text-primary-navy">QCVN 41:2019/BGTVT</span>
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold inline-flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>Quy chuẩn quốc gia
                </span>
                <span class="px-2 py-0.5 rounded bg-[#F8FAFD] text-[11px] text-slate-500 border border-slate-200">Bộ Giao thông Vận tải</span>
              </div>
              <h3 class="text-[16px] font-bold text-primary-navy tracking-tight">Quy chuẩn kỹ thuật quốc gia về Báo hiệu đường bộ</h3>
              <p class="text-[13.5px] text-slate-600 mt-1 leading-relaxed">
                Quy định chi tiết về ý nghĩa, phân loại và quy cách hệ thống biển báo hiệu, vạch kẻ đường, đèn tín hiệu giao thông trên toàn mạng lưới đường bộ Việt Nam.
              </p>
            </div>
          </div>
          <button data-ask="Quy chuẩn kỹ thuật quốc gia QCVN 41:2019/BGTVT" class="btn-ask-doc px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-accent-red text-slate-700 text-[12.5px] font-semibold transition-colors flex items-center gap-1.5 shrink-0 self-start">
            <span class="material-symbols-outlined text-[16px]">smart_toy</span>
            <span>Hỏi AI về luật này</span>
          </button>
        </div>
      </article>

    </div>

    <!-- TraCuuVB_2_NotFound Container (Icon tròn lớn search_off ở đầu khung theo TODO_NOTES) -->
    <div id="docsNotFoundState" class="hidden bg-white rounded-xl p-8 md:p-12 shadow-sm border border-subtle flex flex-col items-center justify-center text-center">
      <!-- Icon tròn lớn search_off ở đầu khung theo yêu cầu -->
      <div class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-4 shadow-xs">
        <span class="material-symbols-outlined text-[36px] text-slate-500">search_off</span>
      </div>

      <div class="max-w-lg flex flex-col items-center text-center px-2">
        <h2 class="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Không tìm thấy văn bản pháp luật phù hợp</h2>
        <p class="mt-2 text-sm text-slate-600 leading-relaxed">
          Không có văn bản quy phạm pháp luật nào khớp với từ khóa tìm kiếm của bạn. Hãy thử tra cứu bằng số hiệu chính xác (ví dụ: <span class="font-semibold text-slate-800">100/2019/NĐ-CP</span>, <span class="font-semibold text-slate-800">36/2024/QH15</span>) hoặc tham vấn trực tiếp Trợ lý AI.
        </p>
      </div>

      <div class="flex flex-col sm:flex-row items-center gap-3 mt-6 w-full sm:w-auto px-4">
        <button id="btn-reset-docs" type="button" class="w-full sm:w-auto px-4 py-2.5 rounded-lg border border-subtle hover:bg-[#F8FAFD] text-slate-700 font-semibold text-sm transition-colors flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-[18px] text-slate-500">close</span>
          <span>Xóa bộ lọc &amp; từ khóa</span>
        </button>
        <button id="btn-ask-ai-search" type="button" class="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-accent-red hover:bg-red-700 text-white font-semibold text-sm transition-all shadow-xs flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-[18px] text-white icon-filled">smart_toy</span>
          <span>Hỏi Trợ lý AI về văn bản này</span>
          <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>

      <!-- Shortcuts list -->
      <div class="w-full max-w-xl mt-8 pt-6 border-t border-slate-100 flex flex-col items-center">
        <div class="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-3">
          <span class="material-symbols-outlined text-[15px] text-amber-500">lightbulb</span>
          <span>Hoặc xem các văn bản pháp luật phổ biến nhất</span>
        </div>
        <div class="w-full flex flex-col gap-2">
          <button data-shortcut="36/2024/QH15" class="btn-shortcut-doc w-full flex items-center justify-between p-3 rounded-lg bg-[#F8FAFD] hover:bg-slate-100 border border-slate-200 transition-all text-left">
            <div class="flex items-center gap-3 min-w-0">
              <span class="material-symbols-outlined text-[22px] text-primary-navy shrink-0">menu_book</span>
              <div class="flex flex-col min-w-0">
                <span class="text-[13.5px] font-semibold text-slate-800 truncate">Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15</span>
                <span class="text-[11.5px] text-slate-500 truncate mt-0.5">Quy tắc giao thông, tín hiệu đèn, giấy phép lái xe 2025</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 shrink-0 ml-2">chevron_right</span>
          </button>

          <button data-shortcut="100/2019/NĐ-CP" class="btn-shortcut-doc w-full flex items-center justify-between p-3 rounded-lg bg-[#F8FAFD] hover:bg-slate-100 border border-slate-200 transition-all text-left">
            <div class="flex items-center gap-3 min-w-0">
              <span class="material-symbols-outlined text-[22px] text-accent-red shrink-0">gavel</span>
              <div class="flex flex-col min-w-0">
                <span class="text-[13.5px] font-semibold text-slate-800 truncate">Nghị định số 100/2019/NĐ-CP &amp; 123/2021/NĐ-CP</span>
                <span class="text-[11.5px] text-slate-500 truncate mt-0.5">Khung tiền phạt nồng độ cồn, chạy quá tốc độ, vượt đèn đỏ</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 shrink-0 ml-2">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</div>
"""

LEGAL_DOCS_JS = """
export default function(component) {
  const { parentElement, setTriggerValue } = component;
  let activeCategory = 'all';

  const input = parentElement.querySelector('#docsSearchInput');
  const clearBtn = parentElement.querySelector('#docsClearBtn');
  const filterBtns = parentElement.querySelectorAll('.doc-filter-btn');
  const docItems = parentElement.querySelectorAll('.doc-item');
  const notFound = parentElement.querySelector('#docsNotFoundState');
  const listContainer = parentElement.querySelector('#docsListContainer');
  const resetBtn = parentElement.querySelector('#btn-reset-docs');
  const askAiBtn = parentElement.querySelector('#btn-ask-ai-search');

  function applyFilter() {
    const query = (input?.value || '').trim().toLowerCase();
    let visibleCount = 0;

    docItems.forEach(item => {
      const cat = item.getAttribute('data-category');
      const keywords = (item.getAttribute('data-keywords') || '').toLowerCase();
      const text = item.textContent.toLowerCase();

      const matchCat = (activeCategory === 'all' || cat === activeCategory);
      const matchQuery = !query || keywords.includes(query) || text.includes(query);

      if (matchCat && matchQuery) {
        item.classList.remove('hidden');
        visibleCount++;
      } else {
        item.classList.add('hidden');
      }
    });

    if (visibleCount === 0) {
      if (notFound) notFound.classList.remove('hidden');
      if (listContainer) listContainer.classList.add('hidden');
    } else {
      if (notFound) notFound.classList.add('hidden');
      if (listContainer) listContainer.classList.remove('hidden');
    }
  }

  // Filter Buttons
  filterBtns.forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      activeCategory = btn.getAttribute('data-category');
      filterBtns.forEach(b => {
        b.className = "doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all";
      });
      btn.className = "doc-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs";
      applyFilter();
    };
  });

  // Search input & clear
  if (input) {
    input.oninput = applyFilter;
  }

  if (clearBtn) {
    clearBtn.onclick = (e) => {
      e.preventDefault();
      if (input) input.value = '';
      applyFilter();
    };
  }

  if (resetBtn) {
    resetBtn.onclick = (e) => {
      e.preventDefault();
      if (input) input.value = '';
      activeCategory = 'all';
      filterBtns.forEach(b => {
        if (b.getAttribute('data-category') === 'all') {
          b.className = "doc-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs";
        } else {
          b.className = "doc-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all";
        }
      });
      applyFilter();
    };
  }

  // Ask AI about doc
  parentElement.querySelectorAll('.btn-ask-doc').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      const docName = btn.getAttribute('data-ask');
      setTriggerValue('ask_doc_trigger', docName);
    };
  });

  if (askAiBtn) {
    askAiBtn.onclick = (e) => {
      e.preventDefault();
      const query = input?.value || 'văn bản pháp luật giao thông';
      setTriggerValue('ask_doc_trigger', query);
    };
  }

  // Shortcuts
  parentElement.querySelectorAll('.btn-shortcut-doc').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      const code = btn.getAttribute('data-shortcut');
      if (input) {
        input.value = code;
        applyFilter();
      }
    };
  });
}
"""

_LEGAL_DOCS_COMPONENT = component(
    name="vinalaw_legal_docs",
    html=LEGAL_DOCS_HTML,
    js=LEGAL_DOCS_JS,
    isolate_styles=False
)

def render_legal_docs(key: str = "legal_docs_comp"):
    """Mount component Tra cứu Văn bản Pháp luật và bắt sự kiện ask_doc_trigger."""
    result = _LEGAL_DOCS_COMPONENT(
        key=key,
        on_ask_doc_trigger_change=lambda: None
    )
    return result
