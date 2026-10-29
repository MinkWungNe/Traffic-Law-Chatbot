"use client";

import React, { useState } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { useAuthStore } from "@/stores/useAuthStore";
import { authApi } from "@/lib/api";
import { AtSign, Lock, Eye, EyeOff, Loader2, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";

export const LoginView: React.FC = () => {
  const { setActiveTab, loadSessions } = useChatStore();
  const { setAuth } = useAuthStore();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    const cleanEmail = email.trim();
    const cleanPassword = password.trim();

    if (!cleanEmail || !cleanPassword) {
      setErrorMessage("Vui lòng điền đầy đủ email và mật khẩu.");
      return;
    }

    if (mode === "register" && cleanPassword.length < 6) {
      setErrorMessage("Mật khẩu đăng ký phải có độ dài tối thiểu 6 ký tự.");
      return;
    }

    setIsSubmitting(true);

    try {
      if (mode === "login") {
        const res = await authApi.login(cleanEmail, cleanPassword);
        setAuth(res.access_token, res.user);
        await loadSessions();
        if (res.user.role === "admin") {
          setActiveTab("admin");
        } else {
          setActiveTab("chat");
        }
      } else {
        const res = await authApi.register(cleanEmail, cleanPassword);
        setAuth(res.access_token, res.user);
        await loadSessions();
        setSuccessMessage("Đăng ký tài khoản thành công! Đang chuyển hướng...");
        setTimeout(() => {
          setActiveTab("chat");
        }, 800);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Đã xảy ra lỗi trong quá trình xác thực.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden select-none font-sans bg-text-muted z-50">
      {/* LAYER 1: Right-aligned Background Image */}
      <div className="absolute top-0 right-0 bottom-0 h-full pointer-events-none hidden lg:flex items-center justify-end overflow-hidden z-0 w-[calc(100vw-530px)]">
        <div
          className="absolute inset-0 w-full h-full bg-cover bg-center filter blur-lg opacity-80 scale-110"
          style={{ backgroundImage: "url('/assets/LoginBackGround.jpg')" }}
        />
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/assets/LoginBackGround.jpg"
          alt="Login Background"
          className="relative h-full w-auto max-w-none object-contain object-right"
        />
      </div>

      {/* LAYER 2: Roadway SVG with Animated Dashed Line */}
      <div className="absolute inset-0 w-full h-full pointer-events-none hidden lg:block overflow-hidden z-10">
        <svg className="w-full h-full absolute inset-0" viewBox="0 0 1440 1200" preserveAspectRatio="none">
          <defs>
            <filter id="roadShadow" x="-20%" y="-10%" width="160%" height="120%">
              <feDropShadow dx="10" dy="0" stdDeviation="15" floodColor="#000000" floodOpacity="0.75" />
            </filter>
          </defs>

          {/* Dải mặt đường cong */}
          <path
            d="M -50,0 L 595,0 C 610,100 610,200 595,300 C 580,400 580,500 595,600 C 610,700 610,800 595,900 C 580,1000 580,1100 595,1200 L -50,1200 Z"
            className="fill-sidebar"
            fillOpacity="0.45"
            filter="url(#roadShadow)"
          />

          {/* Vạch mép liền trái */}
          <path
            d="M 547,0 C 562,100 562,200 547,300 C 532,400 532,500 547,600 C 562,700 562,800 547,900 C 532,1000 532,1100 547,1200"
            fill="none"
            stroke="#B91C1C"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Vạch mép liền phải */}
          <path
            d="M 588,0 C 603,100 603,200 588,300 C 573,400 573,500 588,600 C 603,700 603,800 588,900 C 573,1000 573,1100 588,1200"
            fill="none"
            stroke="#B91C1C"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Vạch tim đường nét đứt chạy liên tục */}
          <path
            className="animate-road-dash"
            d="M 567.5,0 C 582.5,100 582.5,200 567.5,300 C 552.5,400 552.5,500 567.5,600 C 582.5,700 582.5,800 567.5,900 C 552.5,1000 552.5,1100 567.5,1200"
            fill="none"
            stroke="#B91C1C"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Khối trắng nền form */}
          <path
            d="M -50,0 L 540,0 C 555,100 555,200 540,300 C 525,400 525,500 540,600 C 555,700 555,800 540,900 C 525,1000 525,1100 540,1200 L -50,1200 Z"
            fill="#FFFFFF"
          />
        </svg>
      </div>

      {/* Mobile/Tablet Fallback Backdrop (< 1024px) */}
      <div className="absolute inset-0 pointer-events-none lg:hidden bg-white/95 backdrop-blur-sm z-20" />

      {/* LAYER 3: FORM PANEL */}
      <div className="relative h-full flex flex-col justify-between w-full sm:w-[530px] lg:w-[530px] xl:w-[540px] max-w-[540px] overflow-hidden select-none z-30">
        {/* Brand Header & Mode Toggle căn phải */}
        <div className="flex items-center justify-between select-none pt-5 pl-5 sm:pt-6 sm:pl-6 lg:pt-7 lg:pl-7 pr-5 sm:pr-6 lg:pr-7 mb-2">
          {/* Cụm Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-accent-red flex items-center justify-center shadow-md shrink-0 p-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/assets/Chatbot_Logo.svg" alt="" className="w-full h-full object-contain filter invert brightness-0" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-[19px] tracking-tight text-primary-navy leading-none">VinaLaw-Traffic</span>
              <span className="text-[10.5px] text-slate-400 font-semibold tracking-wider uppercase mt-1">
                Trợ lý AI Luật Giao thông
              </span>
            </div>
          </div>

          {/* Toggle Đăng nhập / Đăng ký ngang hàng, căn phải */}
          <div className="flex items-center gap-1 p-1 bg-slate-100/90 rounded-xl border border-slate-200/90 shadow-2xs">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setErrorMessage(null);
              }}
              className={`px-3 py-1 rounded-lg text-[12px] font-semibold transition-all cursor-pointer ${
                mode === "login"
                  ? "bg-white text-primary-navy shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setErrorMessage(null);
              }}
              className={`px-3 py-1 rounded-lg text-[12px] font-semibold transition-all cursor-pointer ${
                mode === "register"
                  ? "bg-white text-primary-navy shadow-xs"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              Đăng ký
            </button>
          </div>
        </div>

        {/* Centered Form Area */}
        <div className="my-auto py-1 w-full flex flex-col justify-center px-[36px] sm:px-[60px] lg:px-[72px]">
          <div className="mb-3 text-center">
            <h1 className="text-[26px] font-bold text-primary-navy tracking-tight mb-1">
              {mode === "login" ? "Chào mừng trở lại" : "Tạo tài khoản mới"}
            </h1>
            <p className="text-[12px] text-slate-500">
              {mode === "login"
                ? "Đăng nhập để lưu và đồng bộ lịch sử tư vấn luật đa phiên."
                : "Đăng ký nhanh để kích hoạt bộ nhớ đa phiên và tính năng bảo mật."}
            </p>
          </div>

          {/* Error / Success Alert */}
          {errorMessage && (
            <div className="mb-3 p-2.5 rounded-xl bg-red-50 border border-red-200 flex items-start gap-2 text-[12.5px] text-red-700 animate-in fade-in duration-150">
              <AlertCircle size={16} className="text-red-500 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="mb-3 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-2 text-[12.5px] text-emerald-700 animate-in fade-in duration-150">
              <CheckCircle2 size={16} className="text-emerald-500 shrink-0 mt-0.5" />
              <span>{successMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            {/* Email Input */}
            <div className="flex flex-col gap-1">
              <label htmlFor="emailInput" className="text-[12.5px] font-semibold text-slate-700">
                Email
              </label>
              <div
                className="spotlight-border relative flex items-center h-[42px] rounded-xl bg-white shadow-xs border border-slate-200"
                style={{ "--glow-color": "#B5B5B5" } as React.CSSProperties}
              >
                <AtSign size={18} className="absolute left-3.5 text-slate-400 pointer-events-none z-10 shrink-0" />
                <input
                  id="emailInput"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full h-full bg-transparent pl-10 pr-4 text-[13.5px] text-slate-800 placeholder:text-slate-400 border-none outline-none focus:outline-none focus:ring-0 relative z-10"
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <label htmlFor="passInput" className="text-[12.5px] font-semibold text-slate-700">
                  Mật khẩu
                </label>
                {mode === "login" && (
                  <span className="text-[11px] text-slate-400">
                    Admin test: <code className="text-accent-red font-mono">admin@vinalaw.vn</code>
                  </span>
                )}
              </div>
              <div
                className="spotlight-border relative flex items-center h-[42px] rounded-xl bg-white shadow-xs border border-slate-200"
                style={{ "--glow-color": "#B5B5B5" } as React.CSSProperties}
              >
                <Lock size={18} className="absolute left-3.5 text-slate-400 pointer-events-none z-10 shrink-0" />
                <input
                  id="passInput"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full h-full bg-transparent pl-10 pr-10 text-[13.5px] text-slate-800 placeholder:text-slate-400 border-none outline-none focus:outline-none focus:ring-0 relative z-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2 p-1 rounded-lg text-slate-400 hover:text-slate-700 transition-colors z-20 cursor-pointer flex items-center justify-center"
                >
                  {showPassword ? <EyeOff size={18} className="shrink-0" /> : <Eye size={18} className="shrink-0" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full h-[42px] rounded-xl bg-accent-red hover:bg-red-700 text-white font-semibold text-[14px] shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer mt-1 active:scale-[0.99]"
            >
              {isSubmitting ? (
                <Loader2 size={18} className="animate-spin shrink-0" />
              ) : (
                <>
                  <span>{mode === "login" ? "Đăng nhập" : "Đăng ký ngay"}</span>
                  <ArrowRight size={18} className="shrink-0" />
                </>
              )}
            </button>
          </form>

          {/* Quick guest bypass */}
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => setActiveTab("chat")}
              className="text-[12.5px] text-slate-500 hover:text-primary-navy underline cursor-pointer"
            >
              Tiếp tục với tư cách Khách (Phiên tạm)
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="p-5 text-center text-[11px] text-slate-400">
          © 2026 VinaLaw-Traffic. Hệ thống tư vấn chuẩn luật giao thông Việt Nam.
        </div>
      </div>
    </div>
  );
};
