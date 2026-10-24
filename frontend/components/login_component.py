"""Màn hình Đăng nhập"""

import streamlit as st
from streamlit.components.v2 import component
from frontend.utils import load_image, load_svg

# 1. Nạp Logo SVG (kích thước được quản lý tập trung qua .brand-logo-box svg trong style.css)
LOGO_SVG = load_svg("Chatbot_Logo.svg", color="#FFFFFF")

# 2. Nạp ảnh nền
BG_DATA_URL = load_image("LoginBackGround.jpg")

LOGIN_HTML = f"""
<div class="fixed inset-0 w-screen h-screen overflow-hidden select-none font-sans" style="background-color: #64748B; z-index: 9999; top: 0; left: 0; right: 0; bottom: 0;">
  
  <!--=== LAYER 1 (z-0): Right-aligned Background Image ===-->
  <div class="absolute top-0 right-0 bottom-0 h-full pointer-events-none hidden lg:flex items-center justify-end overflow-hidden" 
       style="z-index: 0; width: calc(100vw - 530px);">
    
    <!-- Ambient atmosphere mờ rộng bổ trợ nền đồng điệu -->
    <div class="absolute inset-0 w-full h-full bg-cover bg-center filter blur-lg opacity-80 scale-110" 
         style="background-image: url('{BG_DATA_URL}');"></div>

    <!-- Ảnh 3:4 hiển thị trọn vẹn 100% full kích thước (h-full w-auto không cắt xén) -->
    <img src="{BG_DATA_URL}" alt="Login Background" 
         class="relative h-full w-auto max-w-none object-contain object-right" />
  </div>

  <!--=== LAYER 2 (z-10): STATIC ROADWAY & ANIMATED DASHED LANE  ===-->
  <div class="absolute inset-0 w-full h-full pointer-events-none hidden lg:block overflow-hidden" style="z-index: 10;">
    <svg class="w-full h-full absolute inset-0" viewBox="0 0 1440 1200" preserveAspectRatio="none">
      <defs>
        <!-- Shadow cho Lớp 2 (Mặt đường) đổ lên ảnh nền đường phố: đậm hơn rõ rệt (opacity 0.75, độ tỏa 15px) -->
        <filter id="roadShadow" x="-20%" y="-10%" width="160%" height="120%">
          <feDropShadow dx="10" dy="0" stdDeviation="15" flood-color="#000000" flood-opacity="0.75" />
        </filter>
      </defs>

      <!-- 1. LỚP 2: Dải mặt đường -->
      <path d="M -50,0 L 595,0 C 610,100 610,200 595,300 C 580,400 580,500 595,600 C 610,700 610,800 595,900 C 580,1000 580,1100 595,1200 L -50,1200 Z" 
            fill="#0F172A" fill-opacity="0.45" filter="url(#roadShadow)" />

      <!-- 2a. VẠCH MÉP ĐƯỜNG NÉT LIỀN BÊN TRÁI -->
      <path class="road-line transition-all duration-150" d="M 547,0 C 562,100 562,200 547,300 C 532,400 532,500 547,600 C 562,700 562,800 547,900 C 532,1000 532,1100 547,1200" 
            fill="none" stroke="#B91C1C" stroke-width="2.5" stroke-linecap="round" />

      <!-- 2b. VẠCH MÉP ĐƯỜNG NÉT LIỀN BÊN PHẢI  -->
      <path class="road-line transition-all duration-150" d="M 588,0 C 603,100 603,200 588,300 C 573,400 573,500 588,600 C 603,700 603,800 588,900 C 573,1000 573,1100 588,1200" 
            fill="none" stroke="#B91C1C" stroke-width="2.5" stroke-linecap="round" />

      <!-- 2c. VẠCH TIM ĐƯỜNG NÉT ĐỨT MÀU ĐỎ -->
      <path class="road-line animate-road-dash transition-all duration-150" d="M 567.5,0 C 582.5,100 582.5,200 567.5,300 C 552.5,400 552.5,500 567.5,600 C 582.5,700 582.5,800 567.5,900 C 552.5,1000 552.5,1100 567.5,1200" 
            fill="none" stroke="#B91C1C" stroke-width="2.5" stroke-linecap="round" />

      <!-- 3. LỚP 3: Khối trắng -->
      <path d="M -50,0 L 540,0 C 555,100 555,200 540,300 C 525,400 525,500 540,600 C 555,700 555,800 540,900 C 525,1000 525,1100 540,1200 L -50,1200 Z" 
            fill="#FFFFFF" />
    </svg>
  </div>

  <!-- Mobile/Tablet Fallback Backdrop (< 1024px) -->
  <div class="absolute inset-0 pointer-events-none lg:hidden bg-white/95 backdrop-blur-sm" style="z-index: 25;"></div>

  <!--=== LAYER 3 (z-30): FORM PANEL ===-->
  <div class="login-form-panel relative h-full flex flex-col justify-between w-full sm:w-[530px] lg:w-[530px] xl:w-[540px] max-w-[540px] overflow-hidden select-none" style="z-index: 30;">
    
    <!-- Top Left Header Branding (Padding top & left đồng bộ) -->
    <div class="flex items-center gap-3 select-none pt-5 pl-5 sm:pt-6 sm:pl-6 lg:pt-7 lg:pl-7 pr-6 mb-2">
      <div class="brand-logo-box w-10 h-10 rounded-xl bg-accent-red flex items-center justify-center shadow-md shadow-accent-red/25 shrink-0 overflow-hidden" title="VinaLaw-Traffic">
        {LOGO_SVG}
      </div>
      <div class="flex flex-col">
        <span class="font-bold text-[19px] tracking-tight text-primary-navy leading-none">VinaLaw-Traffic</span>
        <span class="text-[10.5px] text-text-muted font-semibold tracking-wider uppercase mt-1">Trợ lý AI Luật Giao thông</span>
      </div>
    </div>

    <!-- Centered Form Area -->
    <div class="my-auto py-1 w-full flex flex-col justify-center px-[36px] sm:px-[60px] lg:px-[72px]">
      <div class="mb-3 text-center">
        <h1 class="text-[30px] font-bold text-primary-navy tracking-tight mb-2">Đăng nhập</h1>
      </div>

      <!-- Interactive Form -->
      <form id="loginForm" class="flex flex-col gap-3">
        
        <!-- Khung nhập Email -->
        <div class="flex flex-col gap-1">
          <label for="usernameInput" class="text-[12.5px] font-semibold text-slate-700">Email</label>
          <div class="input-wrapper relative flex items-center h-[42px] rounded-xl bg-white border border-slate-200 shadow-xs transition-all duration-150">
            <span class="material-symbols-outlined absolute left-3.5 text-slate-400 text-[18px] pointer-events-none">alternate_email</span>
            <input id="usernameInput" name="username" type="text" placeholder="usermail@email.com" required
                   class="w-full h-full bg-transparent pl-10 pr-4 text-[13.5px] text-slate-800 placeholder:text-slate-400 border-none outline-none focus:outline-none focus:ring-0" />
          </div>
        </div>

        <!-- Khung nhập Mật khẩu -->
        <div class="flex flex-col gap-1">
          <div class="flex items-center justify-between">
            <label for="passwordInput" class="text-[12.5px] font-semibold text-slate-700">Mật khẩu</label>
            <a href="#" class="text-[11.5px] font-medium text-accent-red hover:text-red-700 hover:underline transition-colors">Quên mật khẩu?</a>
          </div>
          <div class="input-wrapper relative flex items-center h-[42px] rounded-xl bg-white border border-slate-200 shadow-xs transition-all duration-150">
            <span class="material-symbols-outlined absolute left-3.5 text-slate-400 text-[18px] pointer-events-none">lock</span>
            <input id="passwordInput" name="password" type="password" placeholder="••••••••••••" required
                   class="w-full h-full bg-transparent pl-10 pr-10 text-[13.5px] text-slate-800 placeholder:text-slate-400 border-none outline-none focus:outline-none focus:ring-0" />
            <button id="togglePasswordBtn" type="button" class="absolute right-2 p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors" title="Ẩn / Hiện mật khẩu">
              <span id="togglePasswordIcon" class="material-symbols-outlined text-[18px]">visibility</span>
            </button>
          </div>
        </div>

        <!-- Ghi nhớ đăng nhập Checkbox -->
        <div class="flex items-center justify-between pt-0.5">
          <label class="flex items-center gap-2 cursor-pointer select-none group">
            <input id="rememberMe" name="remember" type="checkbox" 
                   class="w-3.5 h-3.5 rounded border-slate-300 focus:outline-none outline-none cursor-pointer" />
            <span class="text-[12px] text-slate-600 group-hover:text-slate-900 transition-colors">Ghi nhớ đăng nhập trên thiết bị này</span>
          </label>
        </div>

        <!-- Primary CTA: Nút Đăng nhập -->
        <button id="submitBtn" type="submit" 
                class="w-full mt-1 py-2.5 px-4 rounded-xl bg-accent-red hover:bg-[#DC2626] active:scale-[0.99] text-white font-bold text-[14px] flex items-center justify-center gap-2 transition-all duration-150 cursor-pointer">
          <span>Đăng nhập</span>
          <span class="material-symbols-outlined text-[18px] transition-transform group-hover:translate-x-0.5" style="font-variation-settings: 'FILL' 1;">arrow_forward</span>
        </button>

        <!-- Dòng thông báo lỗi -->
        <div id="loginError" class="h-4 mt-1 flex items-center justify-center text-[11.5px] font-semibold text-accent-red invisible transition-opacity duration-150">
          <span class="material-symbols-outlined text-[14px] mr-1">error</span>
          <span id="loginErrorMessage"></span>
        </div>
      </form>

      <!-- Đường kẻ phân cách (Tăng khoảng cách phía trên để giao diện thông thoáng) -->
      <div class="relative mt-4 mb-3 flex items-center justify-center pt-2 pb-2">
        <div class="w-full h-px bg-slate-200"></div>
        <span class="absolute bg-white px-2.5 text-[10.5px] font-semibold uppercase tracking-wider text-slate-400">
          Hoặc trải nghiệm thử nghiệm
        </span>
      </div>

      <!-- Demo Credentials Card & Button -->
      <div class="bg-canvas border border-subtle px-3 py-2 rounded-xl flex items-center justify-between text-xs transition-all hover:border-slate-300 shadow-2xs">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-lg bg-blue-100/70 border border-blue-200/80 flex items-center justify-center text-primary-navy shrink-0">
            <span class="material-symbols-outlined text-[15px]">school</span>
          </div>
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-primary-navy uppercase tracking-wider">Tài khoản mẫu:</span>
            <span class="font-mono text-[11px] text-slate-700 font-medium">demo@student.edu.vn</span>
          </div>
        </div>
        <button id="btn-fill-demo" type="button" 
                class="px-2 py-1 rounded-lg bg-white border border-slate-200 hover:border-accent-red hover:text-accent-red text-slate-700 font-semibold text-[11px] shadow-2xs hover:shadow-xs transition-all flex items-center gap-1 cursor-pointer">
          <span class="material-symbols-outlined text-[13px]">bolt</span>
          <span>Điền nhanh</span>
        </button>
      </div>

      <!-- Direct Guest Explore Option -->
      <div class="mt-2 text-center">
        <button id="btn-bypass" type="button" class="text-[12px] text-slate-500 hover:text-primary-navy hover:underline font-medium transition-colors cursor-pointer">
          Truy cập nhanh với tư cách Khách &rarr;
        </button>
      </div>

      <!-- Registration Link -->
      <div class="mt-2 pt-2 border-t border-slate-100 text-center">
        <p class="text-[12px] text-slate-600">
          Chưa có tài khoản VinaLaw-Traffic?
          <a href="#" class="text-[12px] text-accent-red hover:text-red-700 font-bold hover:underline ml-1">Đăng ký ngay</a>
        </p>
      </div>
    </div>

    <!-- Institutional Footer -->
    <div class="pb-5 sm:pb-6 lg:pb-7 px-[36px] sm:px-[60px] lg:px-[72px] pt-2 flex items-center justify-between text-[10.5px] text-slate-400 font-medium border-t border-slate-100">
      <span>© 2026 VinaLaw-Traffic AI</span>
      <div class="flex items-center gap-3">
        <a href="#" class="hover:text-primary-navy hover:underline transition-colors">Điều khoản</a>
        <span>•</span>
        <a href="#" class="hover:text-primary-navy hover:underline transition-colors">Bảo mật</a>
        <span>•</span>
        <a href="#" class="hover:text-primary-navy hover:underline transition-colors">Hỗ trợ</a>
      </div>
    </div>

  </div>

</div>
"""

LOGIN_JS = """
export default function(component) {
  const { data, parentElement, setTriggerValue } = component;

  // 1. Ẩn / Hiện mật khẩu
  const toggleBtn = parentElement.querySelector('#togglePasswordBtn');
  const passInput = parentElement.querySelector('#passwordInput');
  const passIcon = parentElement.querySelector('#togglePasswordIcon');
  if (toggleBtn && passInput && passIcon) {
    toggleBtn.onclick = (e) => {
      e.preventDefault();
      if (passInput.type === 'password') {
        passInput.type = 'text';
        passIcon.textContent = 'visibility_off';
      } else {
        passInput.type = 'password';
        passIcon.textContent = 'visibility';
      }
    };
  }

  // 2. Điền nhanh tài khoản mẫu với hiệu ứng nhấp nháy highlight
  const demoBtn = parentElement.querySelector('#btn-fill-demo');
  const userInput = parentElement.querySelector('#usernameInput');
  if (demoBtn && userInput && passInput) {
    demoBtn.onclick = (e) => {
      e.preventDefault();
      userInput.value = 'demo@student.edu.vn';
      passInput.value = 'VinaLaw@Traffic2025';

      const userWrap = userInput.closest('.input-wrapper');
      const passWrap = passInput.closest('.input-wrapper');
      if (userWrap && passWrap) {
        userWrap.style.borderColor = '#94A3B8';
        userWrap.style.boxShadow = 'inset 0 0 0 1px #94A3B8';
        passWrap.style.borderColor = '#94A3B8';
        passWrap.style.boxShadow = 'inset 0 0 0 1px #94A3B8';
        setTimeout(() => {
          userWrap.style.borderColor = '';
          userWrap.style.boxShadow = '';
          passWrap.style.borderColor = '';
          passWrap.style.boxShadow = '';
        }, 500);
      }
    };
  }

  // Bỏ viền focus dính của checkbox khi click
  const rememberCheckbox = parentElement.querySelector('#rememberMe');
  if (rememberCheckbox) {
    rememberCheckbox.addEventListener('click', () => {
      rememberCheckbox.blur();
    });
  }

  // 3. Xử lý gửi Form Đăng nhập & Thông báo lỗi chống giật layout
  const loginForm = parentElement.querySelector('#loginForm');
  const submitBtn = parentElement.querySelector('#submitBtn');
  const loginError = parentElement.querySelector('#loginError');
  const loginErrorMsg = parentElement.querySelector('#loginErrorMessage');

  function showError(msg) {
    if (loginError && loginErrorMsg) {
      loginErrorMsg.textContent = msg;
      loginError.classList.remove('invisible');
    }
  }

  function hideError() {
    if (loginError) {
      loginError.classList.add('invisible');
    }
  }

  // Tự động ẩn dòng báo lỗi khi người dùng gõ phím hoặc điền mẫu
  if (userInput) userInput.addEventListener('input', hideError);
  if (passInput) passInput.addEventListener('input', hideError);
  if (demoBtn) demoBtn.addEventListener('click', hideError);

  // Micro-interaction: Khi hover nút Đăng nhập -> Bộ 3 đường nét đỏ sáng màu kèm glow nhẹ
  const roadLines = parentElement.querySelectorAll('.road-line');
  if (submitBtn && roadLines.length > 0) {
    submitBtn.addEventListener('mouseenter', () => {
      roadLines.forEach(line => line.classList.add('road-line-bright'));
    });
    submitBtn.addEventListener('mouseleave', () => {
      roadLines.forEach(line => line.classList.remove('road-line-bright'));
    });
  }

  if (loginForm && submitBtn) {
    loginForm.onsubmit = (e) => {
      e.preventDefault();
      hideError();

      const username = userInput ? userInput.value.trim() : '';
      const password = passInput ? passInput.value : '';

      // Kiểm tra tính hợp lệ cơ bản
      if (!username || !password) {
        showError('Vui lòng nhập đầy đủ email và mật khẩu');
        return;
      }

      if (!username.includes('@')) {
        showError('Định dạng email không hợp lệ');
        return;
      }

      // Xử lý đăng nhập bình thường: không đổi kích thước hay đẩy giật layout
      submitBtn.disabled = true;
      submitBtn.classList.add('opacity-80', 'cursor-not-allowed');

      setTimeout(() => {
        setTriggerValue('login_success', {
          username: username || 'demo@student.edu.vn',
          role: username.startsWith('demo') ? 'student' : 'citizen'
        });
      }, 350);
    };
  }

  // 4. Bỏ qua đăng nhập / Truy cập nhanh với tư cách Khách
  const bypassBtn = parentElement.querySelector('#btn-bypass');
  if (bypassBtn) {
    bypassBtn.onclick = (e) => {
      e.preventDefault();
      setTriggerValue('login_success', {
        username: 'guest',
        role: 'guest'
      });
    };
  }
}
"""

_LOGIN_COMPONENT = component(
    name="vinalaw_login",
    html=LOGIN_HTML,
    js=LOGIN_JS,
    isolate_styles=False
)

def render_login(key: str = "login_comp"):
    """Mount Streamlit Custom Component v2 cho màn hình Đăng nhập và bắt sự kiện login_success."""
    return _LOGIN_COMPONENT(
        key=key,
        data={},
        on_login_success_change=lambda: None
    )
