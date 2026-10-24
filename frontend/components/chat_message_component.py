"""Luồng tin nhắn hội thoại và màn hình chào mừng (Welcome Hero)"""

import streamlit as st
from streamlit.components.v2 import component
from frontend.utils import load_svg

AI_AVATAR_SVG = load_svg("Chatbot_Logo.svg", color="#FFFFFF")

CHAT_MESSAGE_HTML = f"""
<div id="chatScrollArea" class="flex-1 overflow-y-auto px-4 md:px-8 py-6 w-full h-full">
  <div class="max-w-3xl mx-auto flex flex-col gap-6 pb-24">

    <!-- Trạng thái trống (Welcome Hero) -->
    <div id="chatEmptyHero" class="flex flex-col items-center justify-center pt-10 md:pt-14 pb-4 text-center max-w-2xl mx-auto">
      <h1 class="text-[24px] md:text-[28px] font-bold text-slate-900 tracking-tight leading-snug mb-3">
        Xin chào! Tôi có thể giúp gì cho bạn về Luật Giao thông hôm nay?
      </h1>
      <p class="text-[14px] md:text-[15px] text-slate-600 leading-relaxed max-w-xl">
        Hỏi đáp tình huống vi phạm, tra cứu mức phạt theo <strong>luật hiện hành</strong>, quy chuẩn biển báo đường bộ.
      </p>

      <!-- 4 Starter Suggestion Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 max-w-2xl mx-auto w-full mt-8">
        <button data-starter="Xe máy rẽ phải ở ngã tư khi đèn đỏ không có biển phụ thì bị phạt bao nhiêu tiền và có bị giữ bằng lái không?" class="starter-card p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all text-left flex flex-col justify-between group shadow-xs hover:shadow cursor-pointer">
          <div class="flex items-center justify-between w-full mb-1.5">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[20px] text-accent-red">traffic</span>
              <span class="text-[13.5px] font-bold text-slate-900 group-hover:text-primary-navy transition-colors">Rẽ phải khi đèn đỏ</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 group-hover:text-primary-navy group-hover:translate-x-0.5 transition-all">arrow_forward</span>
          </div>
          <p class="text-[12.5px] text-slate-600 leading-normal line-clamp-2">
            Xe máy rẽ phải ngã tư đèn đỏ không có biển phụ bị phạt bao nhiêu?
          </p>
        </button>

        <button data-starter="Khung hình phạt nồng độ cồn mới nhất đối với ô tô và xe máy, thời hạn tước bằng lái xe?" class="starter-card p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all text-left flex flex-col justify-between group shadow-xs hover:shadow cursor-pointer">
          <div class="flex items-center justify-between w-full mb-1.5">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[20px] text-amber-700">no_drinks</span>
              <span class="text-[13.5px] font-bold text-slate-900 group-hover:text-primary-navy transition-colors">Nồng độ cồn ô tô &amp; xe máy</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 group-hover:text-primary-navy group-hover:translate-x-0.5 transition-all">arrow_forward</span>
          </div>
          <p class="text-[12.5px] text-slate-600 leading-normal line-clamp-2">
            Mức phạt kịch khung nồng độ cồn và thời hạn tước bằng lái xe.
          </p>
        </button>

        <button data-starter="Quy định tốc độ tối đa cho phép của xe máy và ô tô trong khu vực đông dân cư?" class="starter-card p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all text-left flex flex-col justify-between group shadow-xs hover:shadow cursor-pointer">
          <div class="flex items-center justify-between w-full mb-1.5">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[20px] text-primary-navy">speed</span>
              <span class="text-[13.5px] font-bold text-slate-900 group-hover:text-primary-navy transition-colors">Tốc độ khu dân cư</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 group-hover:text-primary-navy group-hover:translate-x-0.5 transition-all">arrow_forward</span>
          </div>
          <p class="text-[12.5px] text-slate-600 leading-normal line-clamp-2">
            Tốc độ tối đa trên đường đôi có dải phân cách và đường hai chiều.
          </p>
        </button>

        <button data-starter="Thời hạn và thủ tục nộp phạt nguội toàn quốc qua Cổng Dịch vụ công Quốc gia?" class="starter-card p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all text-left flex flex-col justify-between group shadow-xs hover:shadow cursor-pointer">
          <div class="flex items-center justify-between w-full mb-1.5">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[20px] text-emerald-600">schedule</span>
              <span class="text-[13.5px] font-bold text-slate-900 group-hover:text-primary-navy transition-colors">Thời hạn phạt nguội</span>
            </div>
            <span class="material-symbols-outlined text-[18px] text-slate-400 group-hover:text-primary-navy group-hover:translate-x-0.5 transition-all">arrow_forward</span>
          </div>
          <p class="text-[12.5px] text-slate-600 leading-normal line-clamp-2">
            Quy trình nhận thông báo phạt nguội và cách nộp phạt trực tuyến.
          </p>
        </button>
      </div>
    </div>

    <!-- Danh sách tin nhắn động -->
    <div id="dynamicMessages" class="flex flex-col gap-6"></div>

  </div>
</div>
"""

CHAT_MESSAGE_JS = f"""
export default function(component) {{
  const {{ data, parentElement, setTriggerValue }} = component;
  const messages = (data && data.messages) || [];
  const hero = parentElement.querySelector('#chatEmptyHero');
  const container = parentElement.querySelector('#dynamicMessages');
  const scrollArea = parentElement.querySelector('#chatScrollArea');

  // Gắn sự kiện cho các Starter Cards
  parentElement.querySelectorAll('.starter-card').forEach(btn => {{
    btn.onclick = (e) => {{
      e.preventDefault();
      const prompt = btn.getAttribute('data-starter');
      setTriggerValue('starter_prompt', prompt);
    }};
  }});

  // Nếu có tin nhắn, ẩn Hero và hiển thị tin nhắn
  if (messages.length > 0) {{
    if (hero) hero.classList.add('hidden');
    if (container) {{
      container.innerHTML = '';
      messages.forEach(msg => {{
        if (msg.role === 'user') {{
          const isLong = (msg.content || '').length > 180;
          const userHtml = `
            <div class="flex items-start justify-end gap-3 self-end max-w-2xl mt-4">
              <div class="bg-sidebar border border-slate-200/80 rounded-2xl rounded-tr-sm px-4 py-3 text-[14.5px] leading-relaxed text-slate-900 shadow-xs flex flex-col">
                <div class="user-bubble-content ${{isLong ? 'line-clamp-4' : ''}}">
                  ${{escapeHtml(msg.content)}}
                </div>
                ${{isLong ? `
                  <button type="button" class="expand-btn text-[12px] text-accent-red font-semibold flex items-center gap-0.5 mt-1.5 hover:underline cursor-pointer self-start">
                    <span class="material-symbols-outlined text-[15px]">expand_more</span>
                    <span>Xem thêm</span>
                  </button>
                ` : ''}}
              </div>
              <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0 text-slate-600 text-[14px] font-bold">
                <span class="material-symbols-outlined text-[18px]">person</span>
              </div>
            </div>
          `;
          container.insertAdjacentHTML('beforeend', userHtml);
        }} else if (msg.role === 'assistant') {{
          const botHtml = renderBotMessage(msg);
          container.insertAdjacentHTML('beforeend', botHtml);
        }}
      }});

      // Gắn sự kiện nút Xem thêm / Thu gọn cho tin nhắn user
      container.querySelectorAll('.expand-btn').forEach(btn => {{
        btn.onclick = (e) => {{
          e.preventDefault();
          const bubble = btn.previousElementSibling;
          const label = btn.querySelector('span:last-child');
          const icon = btn.querySelector('.material-symbols-outlined');
          if (bubble.classList.contains('line-clamp-4')) {{
            bubble.classList.remove('line-clamp-4');
            label.textContent = 'Thu gọn';
            icon.textContent = 'expand_less';
          }} else {{
            bubble.classList.add('line-clamp-4');
            label.textContent = 'Xem thêm';
            icon.textContent = 'expand_more';
          }}
        }};
      }});

      // Gắn sự kiện nút Copy
      container.querySelectorAll('.btn-copy-resp').forEach(btn => {{
        btn.onclick = (e) => {{
          e.preventDefault();
          const text = btn.getAttribute('data-copy') || '';
          navigator.clipboard.writeText(text);
          const icon = btn.querySelector('.material-symbols-outlined');
          if (icon) {{
            icon.textContent = 'check';
            setTimeout(() => {{ icon.textContent = 'content_copy'; }}, 1500);
          }}
        }};
      }});

      // Gắn sự kiện cho các Follow-up Chips
      container.querySelectorAll('.follow-up-chip').forEach(chip => {{
        chip.onclick = (e) => {{
          e.preventDefault();
          const query = chip.getAttribute('data-query');
          setTriggerValue('starter_prompt', query);
        }};
      }});

      // Tự động cuộn xuống dưới
      if (scrollArea) {{
        scrollArea.scrollTo({{ top: scrollArea.scrollHeight, behavior: 'smooth' }});
      }}
    }}
  }} else {{
    if (hero) hero.classList.remove('hidden');
    if (container) container.innerHTML = '';
  }}

  function parseMarkdown(text) {{
    if (!text) return '';
    if (window.marked && typeof window.marked.parse === 'function') {{
      try {{
        return window.marked.parse(text);
      }} catch (e) {{
        console.warn('Marked parse error', e);
      }}
    }}
    let html = escapeHtml(text);
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-[15px] font-bold text-primary-navy mt-3 mb-1.5">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-[16px] font-bold text-primary-navy mt-3 mb-1.5">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-[18px] font-bold text-primary-navy mt-3 mb-1.5">$1</h1>');
    html = html.replace(/^\\> (.*$)/gim, '<blockquote class="border-l-3 border-accent-red bg-red-50/70 p-2.5 rounded-r my-2 italic text-slate-700">$1</blockquote>');
    html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="font-semibold text-slate-900">$1</strong>');
    html = html.replace(/\\*(.*?)\\*/g, '<em class="italic">$1</em>');
    html = html.replace(/^\\- (.*$)/gim, '<li class="ml-4 list-disc my-0.5">$1</li>');
    html = html.replace(/\\n\\n/g, '<p class="mb-2"></p>').replace(/\\n/g, '<br/>');
    return html;
  }}

  function renderMarkdownBotMessage(msg) {{
    const rawContent = msg.content || '';
    const parsedHtml = parseMarkdown(rawContent);
    const sources = msg.sources || [];
    const followUps = msg.follow_ups || [
      'Quy trình nộp phạt nguội online như thế nào?',
      'Biển phụ nào thì xe máy được rẽ phải khi đèn đỏ?',
      'Thủ tục nộp phạt và nhận lại bằng lái xe bị tạm giữ?'
    ];

    let sourcesHtml = '';
    if (sources && sources.length > 0) {{
      const items = sources.map((s, idx) => `
        <div class="border-l-2 border-accent-red pl-3 py-1 bg-slate-50/70 rounded-r-md">
          <div class="text-[12px] font-semibold text-slate-800 flex items-center justify-between">
            <span>${{idx + 1}}. ${{escapeHtml(s.title || 'Văn bản quy phạm')}}</span>
            ${{s.score ? `<span class="text-[10px] text-slate-400 font-normal">Độ phù hợp: ${{Math.round(s.score * 100)}}%</span>` : ''}}
          </div>
          ${{s.snippet ? `<p class="italic text-[12px] text-slate-600 mt-0.5">${{escapeHtml(s.snippet)}}</p>` : ''}}
        </div>
      `).join('');

      sourcesHtml = `
        <div class="mt-3 pt-3 border-t border-slate-100 flex flex-col gap-2">
          <div class="text-[11.5px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[15px] text-primary-navy">menu_book</span>
            <span>Căn cứ pháp lý trích xuất (${{sources.length}})</span>
          </div>
          <div class="flex flex-col gap-1.5">
            ${{items}}
          </div>
        </div>
      `;
    }}

    const followUpChipsHtml = followUps.map(f => `
      <button data-query="${{escapeHtml(f)}}" class="follow-up-chip px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-[11.5px] text-slate-700 transition-colors">
        ${{escapeHtml(f)}}
      </button>
    `).join('');

    return `
      <div class="flex items-start gap-3.5 w-full mt-2">
        <div class="brand-logo-box w-8 h-8 rounded-lg shadow-sm" title="VinaLaw AI">
          {AI_AVATAR_SVG}
        </div>

        <div class="flex-1 flex flex-col gap-3 min-w-0">
          <!-- Header metadata line with pulsing green dot -->
          <div class="flex flex-wrap items-center justify-between gap-2 pb-1 border-b border-slate-100">
            <div class="flex items-center gap-2.5">
              <span class="text-[15px] font-bold text-primary-navy tracking-tight">VinaLaw-Traffic AI</span>
              <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[11.5px] font-medium border border-slate-200">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Văn bản pháp luật hiện hành</span>
              </div>
            </div>
          </div>

          <!-- Markdown Content Body -->
          <div class="ai-markdown-content text-slate-800 leading-relaxed bg-white border border-slate-200/70 rounded-2xl p-4 shadow-2xs">
            ${{parsedHtml}}
            ${{sourcesHtml}}
          </div>

          <!-- Action toolbar & Follow-up chips -->
          <div class="flex flex-col gap-2 pt-1 border-t border-slate-100">
            <div class="flex items-center justify-between text-slate-400 text-[12px]">
              <div class="flex items-center gap-1">
                <button type="button" class="btn-copy-resp p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" data-copy="${{escapeHtml(rawContent)}}" title="Sao chép câu trả lời">
                  <span class="material-symbols-outlined text-[17px]">content_copy</span>
                </button>
                <button type="button" class="p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" title="Hữu ích" onclick="this.classList.toggle('text-emerald-600')">
                  <span class="material-symbols-outlined text-[17px]">thumb_up</span>
                </button>
                <button type="button" class="p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" title="Chưa hài lòng" onclick="this.classList.toggle('text-red-600')">
                  <span class="material-symbols-outlined text-[17px]">thumb_down</span>
                </button>
              </div>
            </div>

            <!-- Follow-up chips -->
            <div class="flex flex-wrap items-center gap-2 pt-0.5">
              <span class="text-[11.5px] font-medium text-slate-500">Hỏi tiếp:</span>
              ${{followUpChipsHtml}}
            </div>
          </div>

        </div>
      </div>
    `;
  }}

  function renderBotMessage(msg) {{
    if (msg.render_mode === 'structured') {{
      return renderStructuredBotMessage(msg);
    }}
    return renderMarkdownBotMessage(msg);
  }}

  /* Giữ nguyên thiết kế có cấu trúc (5 khung thẻ) đã kiểm định để sử dụng sau */
  function renderStructuredBotMessage(msg) {{
    const copyText = msg.content || '';
    const verdict = msg.verdict || {{
      title: 'Hành vi vi phạm giao thông',
      desc: msg.content || 'Theo quy định hiện hành, hành vi này bị xử phạt vi phạm hành chính và áp dụng chế tài bổ sung.'
    }};
    const penalty = msg.penalty || {{
      fine: '800.000đ – 1.000.000đ',
      fine_note: 'Mức áp dụng phổ biến: <strong>900.000 VNĐ</strong> (trung bình khung).',
      sub: 'Tước GPLX từ 01 – 03 tháng',
      sub_note: 'Nếu gây tai nạn: Tước GPLX <strong>02 – 04 tháng</strong>.',
      vehicle: 'Xe mô tô, xe gắn máy',
      detention: 'Không tạm giữ xe (nếu xuất trình đủ GPLX & Đăng ký)'
    }};
    const citations = msg.citations || [
      {{
        title: 'Điểm e Khoản 4 Điều 6 Nghị định 100/2019/NĐ-CP',
        quote: '“Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy thực hiện hành vi: Không chấp hành hiệu lệnh của đèn tín hiệu giao thông;”'
      }},
      {{
        title: 'Điểm b Khoản 10 Điều 6 Nghị định 100/2019/NĐ-CP (sửa đổi bởi NĐ 123/2021/NĐ-CP)',
        quote: '“Bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng; trường hợp gây tai nạn giao thông thì bị tước từ 02 tháng đến 04 tháng.”'
      }}
    ];

    let citationsHtml = '';
    citations.forEach(c => {{
      citationsHtml += `
        <div class="border-l-2 border-accent-red pl-3.5 py-1">
          <div class="text-[12.5px] font-semibold text-slate-800 mb-0.5">${{escapeHtml(c.title)}}</div>
          <p class="italic text-[13px] text-slate-600 leading-relaxed">${{escapeHtml(c.quote)}}</p>
        </div>
      `;
    }});

    return `
      <div class="flex items-start gap-3.5 w-full mt-2">
        <div class="brand-logo-box w-8 h-8 rounded-lg shadow-sm" title="VinaLaw AI">
          {AI_AVATAR_SVG}
        </div>

        <div class="flex-1 flex flex-col gap-4 min-w-0">
          <!-- Header metadata line with pulsing green dot -->
          <div class="flex flex-wrap items-center justify-between gap-2 pb-1 border-b border-slate-100">
            <div class="flex items-center gap-2.5">
              <span class="text-[15px] font-bold text-primary-navy tracking-tight">VinaLaw-Traffic AI</span>
              <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[11.5px] font-medium border border-slate-200">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Văn bản pháp luật hiện hành</span>
              </div>
            </div>
          </div>

          <!-- 1. Executive Verdict Banner -->
          <div class="rounded-xl bg-red-50/70 border border-red-200/80 p-4 flex flex-col gap-2">
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-accent-red text-white text-[11px] font-bold tracking-wide uppercase shadow-xs">
                <span class="material-symbols-outlined text-[14px]">warning</span>
                Hành vi vi phạm giao thông
              </span>
              <span class="text-[13px] font-semibold text-accent-red">${{escapeHtml(verdict.title)}}</span>
            </div>
            <p class="text-[14px] text-slate-700 leading-relaxed">
              ${{verdict.desc}}
            </p>
          </div>

          <!-- 2. Penalty & Sanction Summary -->
          <div class="rounded-xl bg-white border border-slate-200 p-4 flex flex-col gap-3.5 shadow-xs">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5 text-[11.5px] font-bold text-slate-500 uppercase tracking-wider">
                <span class="material-symbols-outlined text-[16px] text-accent-red">gavel</span>
                <span>Khung hình phạt &amp; Chế tài áp dụng</span>
              </div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">Phương tiện: ${{escapeHtml(penalty.vehicle)}}</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div class="flex flex-col gap-1 border-r border-slate-200/60 pr-2">
                <span class="text-[12px] font-medium text-slate-500 flex items-center gap-1">
                  <span class="material-symbols-outlined text-[15px] text-accent-red">payments</span>
                  Phạt tiền trực tiếp:
                </span>
                <div class="text-[22px] font-bold text-accent-red tracking-tight leading-none mt-0.5">
                  ${{escapeHtml(penalty.fine)}}
                </div>
                <span class="text-[12px] text-slate-500 mt-1.5">
                  ${{penalty.fine_note}}
                </span>
              </div>

              <div class="flex flex-col gap-1.5">
                <span class="text-[12px] font-medium text-slate-500 flex items-center gap-1">
                  <span class="material-symbols-outlined text-[15px] text-amber-800">badge</span>
                  Hình thức xử lý bổ sung:
                </span>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 text-[12.5px] font-bold border border-amber-200/60 leading-none shadow-xs">
                    ${{escapeHtml(penalty.sub)}}
                  </span>
                </div>
                <span class="text-[12px] text-slate-500 mt-1">
                  ${{penalty.sub_note}}
                </span>
              </div>
            </div>

            <div class="pt-2.5 border-t border-slate-200/70 flex flex-wrap items-center justify-between gap-2 text-[12px] text-slate-600">
              <div class="flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[14px] text-emerald-500">check_circle</span>
                <span>Tạm giữ phương tiện: <strong class="text-slate-800 font-semibold">${{escapeHtml(penalty.detention)}}</strong></span>
              </div>
              <div class="flex items-center gap-1.5 text-slate-500 text-[11.5px]">
                <span class="material-symbols-outlined text-[14px] text-primary-navy">security</span>
                <span>Thẩm quyền xử phạt: <strong class="text-slate-700 font-medium">CSGT đường bộ</strong></span>
              </div>
            </div>
          </div>

          <!-- 3. Legal Citations -->
          <div class="flex flex-col gap-2.5">
            <div class="text-[11.5px] font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[15px] text-primary-navy">menu_book</span>
              Căn cứ pháp lý nguyên văn
            </div>
            <div class="flex flex-col gap-2.5">
              ${{citationsHtml}}
            </div>
          </div>

          <!-- 4. Practical note -->
          <div class="flex items-start gap-2.5 p-3 rounded-lg bg-blue-50/50 border border-blue-100 text-[12.5px] text-slate-700 leading-relaxed">
            <span class="material-symbols-outlined text-[18px] text-primary-navy shrink-0 mt-0.5">tips_and_updates</span>
            <div>
              <strong class="text-primary-navy">Gợi ý xử lý:</strong> Người vi phạm có thể tra cứu và nộp phạt trực tuyến nhanh gọn qua <strong>Cổng Dịch vụ công Quốc gia</strong> mà không cần đến trực tiếp trụ sở Công an xử lý vi phạm.
            </div>
          </div>

          <!-- 5. Action toolbar & Follow-up chips -->
          <div class="flex flex-col gap-2.5 pt-2 border-t border-slate-100">
            <div class="flex items-center justify-between text-slate-400 text-[12px]">
              <div class="flex items-center gap-1">
                <button type="button" class="btn-copy-resp p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" data-copy="${{escapeHtml(copyText)}}" title="Sao chép câu trả lời">
                  <span class="material-symbols-outlined text-[17px]">content_copy</span>
                </button>
                <button type="button" class="p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" title="Hữu ích" onclick="this.classList.toggle('text-emerald-600')">
                  <span class="material-symbols-outlined text-[17px]">thumb_up</span>
                </button>
                <button type="button" class="p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center" title="Chưa hài lòng" onclick="this.classList.toggle('text-red-600')">
                  <span class="material-symbols-outlined text-[17px]">thumb_down</span>
                </button>
              </div>
            </div>

            <!-- Follow-up chips -->
            <div class="flex flex-wrap items-center gap-2 pt-0.5">
              <span class="text-[11.5px] font-medium text-slate-500">Hỏi tiếp:</span>
              <button data-query="Quy trình nộp phạt nguội online như thế nào?" class="follow-up-chip px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-[11.5px] text-slate-700 transition-colors">
                Cách nộp phạt online
              </button>
              <button data-query="Biển phụ nào thì xe máy được rẽ phải khi đèn đỏ?" class="follow-up-chip px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-[11.5px] text-slate-700 transition-colors">
                Biển phụ rẽ phải
              </button>
              <button data-query="Thủ tục nộp phạt và nhận lại bằng lái xe bị tạm giữ?" class="follow-up-chip px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-[11.5px] text-slate-700 transition-colors">
                Thủ tục nhận lại GPLX
              </button>
            </div>
          </div>

        </div>
      </div>
    `;
  }}

  function escapeHtml(str) {{
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }}
}}
"""

_CHAT_MESSAGE_COMPONENT = component(
    name="vinalaw_chat_messages",
    html=CHAT_MESSAGE_HTML,
    js=CHAT_MESSAGE_JS,
    isolate_styles=False
)

def render_chat_messages(messages: list, key: str = "chat_msg_comp"):
    """Mount component hiển thị danh sách tin nhắn hội thoại và bắt sự kiện starter_prompt."""
    result = _CHAT_MESSAGE_COMPONENT(
        key=key,
        data={"messages": messages},
        on_starter_prompt_change=lambda: None
    )
    return result
