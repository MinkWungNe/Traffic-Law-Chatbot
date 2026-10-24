"""Màn hình Câu hỏi Thường gặp và bảng đối chiếu chế tài xử phạt giao thông."""

import streamlit as st
from streamlit.components.v2 import component

FAQ_HTML = """
<div class="flex-1 overflow-y-auto px-4 md:px-8 py-8 w-full h-full select-none">
  <div class="max-w-4xl mx-auto flex flex-col gap-6 pb-20">

    <!-- Header -->
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">Câu hỏi Thường gặp về Giao thông &amp; Xử phạt</h1>
      <p class="text-sm md:text-base text-slate-600 leading-relaxed">
        Tổng hợp các thắc mắc và tình huống pháp lý phổ biến được người dân hỏi nhiều nhất qua Trợ lý AI. Dữ liệu trích xuất trực tiếp từ các văn bản pháp luật hiện hành.
      </p>
    </div>

    <!-- Search Bar & Filters Card -->
    <div class="bg-white rounded-xl p-4 shadow-sm border border-subtle flex flex-col gap-4">
      <div class="relative flex items-center">
        <span class="material-symbols-outlined absolute left-4 text-slate-400 text-[22px] pointer-events-none">search</span>
        <input id="faqSearchInput" type="text" class="w-full bg-[#F8FAFD] text-slate-900 text-sm md:text-base pl-12 pr-12 py-3 rounded-lg border border-subtle focus:outline-none focus:bg-white focus:border-slate-300 transition-all placeholder:text-slate-400" placeholder="Tìm kiếm câu hỏi, tình huống xử phạt (VD: nồng độ cồn, vượt đèn đỏ, bằng lái)..." />
        <button id="faqClearBtn" type="button" class="absolute right-3 p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors flex items-center justify-center" title="Xóa từ khóa">
          <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>

      <!-- Category Filter Chips -->
      <div class="flex items-center gap-2 flex-wrap pt-1" id="faqFilterChips">
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs" data-category="all">
          Tất cả
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="oto">
          Ô tô
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="xemay">
          Xe máy
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="nongdocon">
          Nồng độ cồn
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="tocdo">
          Tốc độ
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="gplx">
          Giấy phép lái xe
        </button>
        <button class="faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all" data-category="phatnguoi">
          Phạt nguội
        </button>
      </div>
    </div>

    <!-- TODO: [FAQ Data] Hiện tại đang hardcode dữ liệu câu hỏi thường gặp mẫu -->
    <!-- DANH SÁCH CÂU HỎI: 100% CÁC CÂU HỎI ĐÓNG Ở DẠNG MẶC ĐỊNH THEO YÊU CẦU -->
    <div class="flex flex-col gap-3" id="faqAccordionList">

      <!-- Item 1: Nồng độ cồn -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="nongdocon" data-keywords="mức phạt nồng độ cồn xe máy ô tô tước bằng lái tạm giữ phương tiện">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              01
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-red-50 text-accent-red text-[11px] font-bold">Nồng độ cồn</span>
                <span class="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[11px] font-bold">Mức phạt kịch khung</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Mức phạt nồng độ cồn xe máy và ô tô mới nhất là bao nhiêu?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH (hidden) THEO TODO_NOTES -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <p class="text-[13.5px] text-slate-700 leading-relaxed mb-3">
            Căn cứ theo <strong>Nghị định 100/2019/NĐ-CP</strong> và sửa đổi bổ sung bởi <strong>Nghị định 123/2021/NĐ-CP</strong>, hành vi điều khiển phương tiện khi trong máu hoặc hơi thở có nồng độ cồn đều bị nghiêm cấm hoàn toàn.
          </p>
          
          <!-- Bảng so sánh trực quan -->
          <div class="overflow-x-auto rounded-lg border border-slate-200 mb-3">
            <table class="w-full text-left text-[12.5px]">
              <thead class="bg-primary-navy text-white text-[12px] font-semibold">
                <tr>
                  <th class="py-2.5 px-3">Khung vi phạm nồng độ</th>
                  <th class="py-2.5 px-3">Người lái Ô TÔ</th>
                  <th class="py-2.5 px-3">Người lái XE MÁY</th>
                  <th class="py-2.5 px-3">Tước GPLX</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 text-slate-700">
                <tr class="hover:bg-slate-50">
                  <td class="py-2.5 px-3 font-medium">Chưa vượt quá 50 mg/100 ml máu (hoặc 0.25 mg/l khí thở)</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">6 - 8 triệu đồng</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">2 - 3 triệu đồng</td>
                  <td class="py-2.5 px-3">Tước 10 - 12 tháng</td>
                </tr>
                <tr class="hover:bg-slate-50">
                  <td class="py-2.5 px-3 font-medium">Vượt quá 50 - 80 mg/100 ml máu (hoặc 0.25 - 0.4 mg/l khí thở)</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">16 - 18 triệu đồng</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">4 - 5 triệu đồng</td>
                  <td class="py-2.5 px-3">Tước 16 - 18 tháng</td>
                </tr>
                <tr class="hover:bg-slate-50">
                  <td class="py-2.5 px-3 font-medium">Vượt quá 80 mg/100 ml máu (hoặc 0.4 mg/l khí thở)</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">30 - 40 triệu đồng</td>
                  <td class="py-2.5 px-3 font-bold text-accent-red">6 - 8 triệu đồng</td>
                  <td class="py-2.5 px-3">Tước 22 - 24 tháng</td>
                </tr>
              </tbody>
            </table>
          </div>
          <button data-ask="Mức phạt nồng độ cồn xe máy và ô tô mới nhất" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI phân tích trường hợp cụ thể</span>
          </button>
        </div>
      </div>

      <!-- Item 2: Vượt đèn vàng đèn đỏ -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="xemay" data-keywords="vượt đèn vàng đèn đỏ xe máy ô tô mức phạt tín hiệu giao thông">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              02
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-blue-50 text-primary-navy text-[11px] font-bold">Tín hiệu giao thông</span>
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">QCVN 41:2019</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Vượt đèn vàng và vượt đèn đỏ có bị phạt như nhau không?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <p class="text-[13.5px] text-slate-700 leading-relaxed mb-3">
            <strong>Có, mức phạt là như nhau.</strong> Cả hai hành vi đều bị xác định là <em>"Không chấp hành hiệu lệnh của đèn tín hiệu giao thông"</em>:
          </p>
          <ul class="list-disc pl-5 text-[13px] text-slate-600 space-y-1 mb-3">
            <li><strong>Xe ô tô:</strong> Phạt tiền từ <strong>4.000.000đ – 6.000.000đ</strong>, tước GPLX từ 01 – 03 tháng.</li>
            <li><strong>Xe máy:</strong> Phạt tiền từ <strong>800.000đ – 1.000.000đ</strong>, tước GPLX từ 01 – 03 tháng.</li>
          </ul>
          <button data-ask="Vượt đèn vàng và vượt đèn đỏ có bị phạt như nhau không?" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI về tình huống này</span>
          </button>
        </div>
      </div>

      <!-- Item 3: Tốc độ -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="tocdo" data-keywords="chạy quá tốc độ tước bằng lái ô tô xe máy km/h bắn tốc độ">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              03
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[11px] font-bold">Chạy quá tốc độ</span>
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">Tước GPLX</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Chạy quá tốc độ bao nhiêu km/h thì bị tước giấy phép lái xe?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <div class="space-y-2 text-[13px] text-slate-700 mb-3">
            <div class="p-2.5 rounded bg-slate-50 border border-slate-200">
              <strong>Đối với ô tô:</strong> Bị tước GPLX khi chạy quá tốc độ từ <strong>20 km/h trở lên</strong> (Quá 20 - 35 km/h: Tước 02 - 04 tháng; Quá trên 35 km/h: Tước 02 - 04 tháng và phạt tiền 10 - 12 triệu).
            </div>
            <div class="p-2.5 rounded bg-slate-50 border border-slate-200">
              <strong>Đối với xe máy:</strong> Bị tước GPLX khi chạy quá tốc độ từ <strong>trên 20 km/h trở lên</strong> (Tước GPLX từ 02 – 04 tháng, phạt tiền từ 4 - 5 triệu).
            </div>
          </div>
          <button data-ask="Chạy quá tốc độ bao nhiêu km/h thì bị tước bằng lái xe?" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI về tình huống này</span>
          </button>
        </div>
      </div>

      <!-- Item 4: Giấy phép lái xe -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="gplx" data-keywords="quên mang bằng lái không có giấy phép lái xe gplx vneid mức phạt">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              04
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-[11px] font-bold">Giấy tờ xe</span>
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">VNeID</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Lỗi không mang Giấy phép lái xe khác gì lỗi không có Giấy phép lái xe?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <ul class="list-disc pl-5 text-[13px] text-slate-700 space-y-1 mb-3">
            <li><strong>Quên mang GPLX:</strong> Xe máy phạt 100.000đ – 200.000đ; Ô tô phạt 200.000đ – 400.000đ. (Xuất trình GPLX trên VNeID có giá trị tương đương).</li>
            <li><strong>Không có GPLX:</strong> Xe máy phạt từ 1 - 5 triệu đồng; Ô tô phạt 10 - 12 triệu đồng và tạm giữ phương tiện.</li>
          </ul>
          <button data-ask="Phân biệt lỗi không mang và không có giấy phép lái xe" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI về tình huống này</span>
          </button>
        </div>
      </div>

      <!-- Item 5: Phạt nguội -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="phatnguoi" data-keywords="thủ tục quy trình nộp phạt nguội toàn quốc cổng dịch vụ công csgt tra cứu">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              05
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[11px] font-bold">Phạt nguội</span>
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">Dịch vụ công</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Quy trình và thời hạn nộp phạt nguội toàn quốc qua Cổng Dịch vụ công?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <p class="text-[13.5px] text-slate-700 leading-relaxed mb-3">
            Người vi phạm có thể tra cứu thông tin phạt nguội tại website Cục CSGT. Sau khi nhận thông báo, công dân có thể nộp phạt trực tuyến 100% qua <strong>Cổng Dịch vụ công Quốc gia</strong> bằng mã quyết định xử phạt mà không cần đến trực tiếp cơ quan công an.
          </p>
          <button data-ask="Quy trình nộp phạt nguội trực tuyến trên Cổng dịch vụ công" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI về tình huống này</span>
          </button>
        </div>
      </div>

      <!-- Item 6: Xe máy không gương -->
      <div class="faq-card bg-white rounded-xl shadow-xs border border-subtle overflow-hidden transition-all" data-category="xemay" data-keywords="xe máy không gương chiếu hậu bên phải bên trái phạt bao nhiêu">
        <button class="faq-toggle-btn w-full px-5 py-4 flex items-start justify-between text-left gap-4 hover:bg-[#F8FAFD] transition-colors" type="button">
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-7 h-7 rounded-md bg-red-50 text-accent-red text-[12px] font-bold flex items-center justify-center border border-red-100">
              06
            </span>
            <div>
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="px-2 py-0.5 rounded bg-blue-50 text-primary-navy text-[11px] font-bold">Xe máy</span>
                <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">Gương chiếu hậu</span>
              </div>
              <h3 class="text-[15px] font-bold text-primary-navy leading-snug">
                Xe máy không có gương chiếu hậu bên phải có bị phạt tiền không?
              </h3>
            </div>
          </div>
          <div class="faq-icon-box shrink-0 w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 transition-transform duration-200">
            <span class="material-symbols-outlined text-[18px]">expand_more</span>
          </div>
        </button>
        <!-- ĐÓNG MẶC ĐỊNH -->
        <div class="faq-content hidden px-5 pb-5 pt-1 border-t border-slate-100">
          <p class="text-[13.5px] text-slate-700 leading-relaxed mb-3">
            <strong>Không bị phạt.</strong> Theo Điểm a Khoản 1 Điều 17 Nghị định 100/2019/NĐ-CP, pháp luật chỉ xử phạt hành vi điều khiển xe máy <em>"không có gương chiếu hậu bên trái người điều khiển hoặc có nhưng không có tác dụng"</em> với mức phạt từ <strong>100.000đ – 200.000đ</strong>.
          </p>
          <button data-ask="Xe máy không gương chiếu hậu bên phải có bị phạt không?" class="btn-ask-faq text-accent-red font-semibold text-[12.5px] hover:underline flex items-center gap-1">
            <span class="material-symbols-outlined text-[15px]">smart_toy</span>
            <span>Hỏi trợ lý AI về tình huống này</span>
          </button>
        </div>
      </div>

    </div>

    <!-- CauHoiThuongGap_2_NotFound Container (Icon tròn lớn help_outline ở đầu khung) -->
    <div id="faqNotFoundState" class="hidden bg-white rounded-xl p-8 md:p-12 shadow-sm border border-subtle flex flex-col items-center justify-center text-center">
      <!-- Icon tròn lớn help_outline ở đầu khung theo yêu cầu -->
      <div class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-4 shadow-xs">
        <span class="material-symbols-outlined text-[36px] text-slate-500">help_outline</span>
      </div>

      <div class="max-w-lg flex flex-col items-center text-center px-2">
        <h2 class="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Chưa có câu hỏi giải đáp cho tình huống này</h2>
        <p class="mt-2 text-sm text-slate-600 leading-relaxed">
          Chưa có câu trả lời mẫu có sẵn khớp với từ khóa của bạn. Trợ lý AI có thể giải đáp chi tiết theo từng điều khoản luật ngay lập tức.
        </p>
      </div>

      <div class="flex flex-col sm:flex-row items-center gap-3 mt-6 w-full sm:w-auto px-4">
        <button id="btn-reset-faq" type="button" class="w-full sm:w-auto px-4 py-2.5 rounded-lg border border-subtle hover:bg-[#F8FAFD] text-slate-700 font-semibold text-sm transition-colors flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-[18px] text-slate-500">close</span>
          <span>Xóa từ khóa</span>
        </button>
        <button id="btn-ask-ai-faq-search" type="button" class="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-accent-red hover:bg-red-700 text-white font-semibold text-sm transition-all shadow-xs flex items-center justify-center gap-2">
          <span class="material-symbols-outlined text-[18px] text-white icon-filled">smart_toy</span>
          <span>Hỏi Trợ lý AI giải đáp ngay</span>
          <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>

      <!-- Suggested Situations List -->
      <div class="w-full max-w-xl mt-8 pt-6 border-t border-slate-100 flex flex-col items-center">
        <div class="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold uppercase tracking-wider mb-3">
          <span class="material-symbols-outlined text-[15px] text-amber-500">lightbulb</span>
          <span>Hoặc xem các tình huống phổ biến liên quan</span>
        </div>
        <div class="w-full flex flex-col gap-2">
          <button data-faq-quick="Mức phạt vượt đèn đỏ đối với xe máy theo quy định mới nhất?" class="btn-quick-faq w-full flex items-center justify-between p-3 rounded-lg bg-[#F8FAFD] hover:bg-slate-100 border border-slate-200 transition-all text-left">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[20px] text-accent-red shrink-0">traffic</span>
              <span class="text-[13.5px] font-semibold text-slate-800">Mức phạt vượt đèn đỏ đối với xe máy theo quy định mới nhất?</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 shrink-0">chevron_right</span>
          </button>
          <button data-faq-quick="Bị phạt nguội kiểm tra ở đâu chính xác nhất trên Cục Cảnh sát giao thông?" class="btn-quick-faq w-full flex items-center justify-between p-3 rounded-lg bg-[#F8FAFD] hover:bg-slate-100 border border-slate-200 transition-all text-left">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[20px] text-primary-navy shrink-0">manage_search</span>
              <span class="text-[13.5px] font-semibold text-slate-800">Bị phạt nguội kiểm tra ở đâu chính xác nhất trên Cục CSGT?</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 shrink-0">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</div>
"""

FAQ_JS = """
export default function(component) {
  const { parentElement, setTriggerValue } = component;
  let activeCategory = 'all';

  const input = parentElement.querySelector('#faqSearchInput');
  const clearBtn = parentElement.querySelector('#faqClearBtn');
  const filterBtns = parentElement.querySelectorAll('.faq-filter-btn');
  const faqCards = parentElement.querySelectorAll('.faq-card');
  const notFound = parentElement.querySelector('#faqNotFoundState');
  const listContainer = parentElement.querySelector('#faqAccordionList');
  const resetBtn = parentElement.querySelector('#btn-reset-faq');
  const askAiBtn = parentElement.querySelector('#btn-ask-ai-faq-search');

  // Accordion Toggle: Mở / Đóng mượt mà
  faqCards.forEach(card => {
    const toggleBtn = card.querySelector('.faq-toggle-btn');
    const content = card.querySelector('.faq-content');
    const iconBox = card.querySelector('.faq-icon-box');

    if (toggleBtn && content && iconBox) {
      toggleBtn.onclick = (e) => {
        e.preventDefault();
        const isHidden = content.classList.contains('hidden');
        if (isHidden) {
          content.classList.remove('hidden');
          iconBox.classList.add('rotate-180');
        } else {
          content.classList.add('hidden');
          iconBox.classList.remove('rotate-180');
        }
      };
    }
  });

  function applyFilter() {
    const query = (input?.value || '').trim().toLowerCase();
    let visibleCount = 0;

    faqCards.forEach(card => {
      const cat = card.getAttribute('data-category');
      const keywords = (card.getAttribute('data-keywords') || '').toLowerCase();
      const text = card.textContent.toLowerCase();

      const matchCat = (activeCategory === 'all' || cat === activeCategory);
      const matchQuery = !query || keywords.includes(query) || text.includes(query);

      if (matchCat && matchQuery) {
        card.classList.remove('hidden');
        visibleCount++;
      } else {
        card.classList.add('hidden');
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

  // Filter category chips
  filterBtns.forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      activeCategory = btn.getAttribute('data-category');
      filterBtns.forEach(b => {
        b.className = "faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all";
      });
      btn.className = "faq-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs";
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
          b.className = "faq-filter-btn px-3 py-1 rounded-full bg-primary-navy text-white text-[12px] font-semibold transition-all shadow-xs";
        } else {
          b.className = "faq-filter-btn px-3 py-1 rounded-full bg-[#F8FAFD] hover:bg-slate-100 text-slate-600 border border-slate-200 text-[12px] font-semibold transition-all";
        }
      });
      applyFilter();
    };
  }

  // Ask AI buttons
  parentElement.querySelectorAll('.btn-ask-faq').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      const question = btn.getAttribute('data-ask');
      setTriggerValue('ask_faq_trigger', question);
    };
  });

  if (askAiBtn) {
    askAiBtn.onclick = (e) => {
      e.preventDefault();
      const query = input?.value || 'tình huống xử phạt giao thông';
      setTriggerValue('ask_faq_trigger', query);
    };
  }

  parentElement.querySelectorAll('.btn-quick-faq').forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      const q = btn.getAttribute('data-faq-quick');
      setTriggerValue('ask_faq_trigger', q);
    };
  });
}
"""

_FAQ_COMPONENT = component(
    name="vinalaw_faq",
    html=FAQ_HTML,
    js=FAQ_JS,
    isolate_styles=False
)

def render_faq(key: str = "faq_comp"):
    """Mount component Câu hỏi Thường gặp và bắt sự kiện ask_faq_trigger."""
    result = _FAQ_COMPONENT(
        key=key,
        on_ask_faq_trigger_change=lambda: None
    )
    return result
