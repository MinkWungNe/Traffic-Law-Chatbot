"use client";

import React, { useState, useEffect } from "react";
import { useChatStore } from "@/stores/useChatStore";

export const Sidebar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    sessionTitle,
    setSessionTitle,
    clearMessages,
    backendStatus,
    backendMessage,
    checkBackend,
  } = useChatStore();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    checkBackend();
  }, [checkBackend]);

  const handleNewChat = () => {
    clearMessages();
    setSessionTitle("Cuộc trò chuyện mới");
    setActiveTab("chat");
  };

  const navItems = [
    { id: "chat" as const, label: "Trợ lý AI", icon: "smart_toy" },
    { id: "docs" as const, label: "Tra cứu Văn bản Pháp luật", icon: "menu_book" },
    { id: "faq" as const, label: "Câu hỏi thường gặp", icon: "help_center" },
  ];

  return (
    <aside className="w-[270px] shrink-0 bg-sidebar/[0.02] border-r border-subtle flex flex-col justify-between h-screen select-none z-20 relative">
      <div className="flex flex-col p-3 overflow-y-auto">
        {/* Brand Header */}
        <div className="flex items-center gap-2.5 px-2 py-2 mb-2">
          <div className="w-9 h-9 rounded-xl bg-accent-red flex items-center justify-center shrink-0 shadow-sm p-1.5" title="VinaLaw-Traffic">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/assets/Chatbot_Logo.svg" alt="" className="w-full h-full object-contain filter invert brightness-0" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-[15px] tracking-tight text-primary-navy leading-none">VinaLaw-Traffic</span>
            <span className="text-[11px] text-text-muted font-medium mt-1">Trợ lý AI Luật Giao thông</span>
          </div>
        </div>

        {/* Backend Status Pill */}
        <div
          className={`flex items-center justify-between px-3 py-1.5 mb-3 rounded-xl border text-[11px] transition-colors ${
            backendStatus === "connected"
              ? "bg-emerald-50/80 border-emerald-200/80 text-emerald-800"
              : backendStatus === "checking"
              ? "bg-blue-50/80 border-blue-200/80 text-blue-800"
              : "bg-amber-50/80 border-amber-200/80 text-amber-800"
          }`}
          title={backendMessage}
        >
          <div className="flex items-center gap-1.5 min-w-0">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                backendStatus === "connected"
                  ? "bg-emerald-500 animate-pulse"
                  : backendStatus === "checking"
                  ? "bg-blue-500 animate-ping"
                  : "bg-amber-500"
              }`}
            />
            <span className="truncate font-medium">
              {backendStatus === "connected"
                ? "Backend: Kết nối (Port 8000)"
                : backendStatus === "checking"
                ? "Đang ping Backend..."
                : "Backend: Ngoại tuyến"}
            </span>
          </div>
          <button
            type="button"
            onClick={() => checkBackend()}
            className="p-1 rounded hover:bg-black/5 text-slate-500 hover:text-slate-800 transition-colors shrink-0 cursor-pointer"
            title="Kiểm tra lại kết nối"
          >
            <span
              className={`material-symbols-outlined text-[14px] ${
                backendStatus === "checking" ? "animate-spin" : ""
              }`}
            >
              refresh
            </span>
          </button>
        </div>

        {/* New Chat Button with Spotlight Border */}
        <button
          onClick={handleNewChat}
          className="spotlight-border flex items-center gap-3 w-full px-4 py-2.5 rounded-full bg-white shadow-2xs text-text-main mb-4 text-left group relative cursor-pointer"
          style={{ "--glow-color": "#B91C1C" } as React.CSSProperties}
        >
          <div className="relative z-10 flex items-center gap-3 w-full">
            <span className="material-symbols-outlined text-[20px] text-accent-red">add</span>
            <span className="text-[13px] font-semibold text-slate-800">Cuộc trò chuyện mới</span>
          </div>
        </button>

        {/* Main Navigation Tabs */}
        <nav className="flex flex-col gap-1 mb-5">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all cursor-pointer ${
                  isActive
                    ? "bg-white text-primary-navy font-bold shadow-xs border border-slate-200/60"
                    : "text-text-muted hover:text-text-main hover:bg-white/60"
                }`}
              >
                <span className={`material-symbols-outlined text-[18px] ${isActive ? "text-accent-red" : "group-hover:text-accent-red"}`}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* History Section: Single Session */}
        <div className="flex flex-col">
          <div className="flex items-center justify-between px-2.5 py-1 mb-1.5 text-slate-500">
            <span className="text-[11px] font-bold tracking-wider uppercase">Lịch sử trò chuyện</span>
            <span className="material-symbols-outlined text-[16px] cursor-pointer hover:text-slate-900">expand_more</span>
          </div>

          <div className="relative flex flex-col gap-0.5">
            <div className="group relative flex items-center w-full px-2 py-1.5 rounded-lg hover:bg-white/70 transition-all text-[12.5px] text-slate-700">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpen(!menuOpen);
                }}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-slate-200/80 text-slate-500 hover:text-slate-800 transition-opacity shrink-0 mr-1.5 flex items-center justify-center cursor-pointer"
                title="Tùy chọn phiên"
              >
                <span className="material-symbols-outlined text-[16px]">more_vert</span>
              </button>
              <span
                onClick={() => setActiveTab("chat")}
                className="truncate cursor-pointer flex-1 font-medium"
              >
                {sessionTitle}
              </span>
            </div>

            {menuOpen && (
              <div className="absolute left-2 top-8 z-50 w-36 bg-white rounded-lg shadow-lg border border-slate-200 py-1 flex flex-col text-[12px] text-slate-700">
                <button
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px] text-slate-500">push_pin</span>
                  <span>Ghim</span>
                </button>
                <button
                  onClick={() => {
                    const newTitle = prompt("Nhập tiêu đề mới:", sessionTitle);
                    if (newTitle) setSessionTitle(newTitle);
                    setMenuOpen(false);
                  }}
                  className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px] text-slate-500">edit</span>
                  <span>Đổi tên</span>
                </button>
                <button
                  onClick={() => {
                    clearMessages();
                    setSessionTitle("Cuộc trò chuyện mới");
                    setMenuOpen(false);
                  }}
                  className="flex items-center gap-2 px-3 py-1.5 hover:bg-red-50 text-red-600 text-left transition-colors border-t border-slate-100 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px] text-red-500">delete</span>
                  <span>Xóa</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer Account Button */}
      <div className="p-3 border-t border-subtle">
        <button
          onClick={() => setActiveTab("login")}
          className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all cursor-pointer ${
            activeTab === "login"
              ? "bg-white text-primary-navy font-bold shadow-xs border border-slate-200/60"
              : "text-text-muted hover:text-text-main hover:bg-white/60"
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">account_circle</span>
          <span>Tài khoản / Đăng nhập</span>
        </button>
      </div>
    </aside>
  );
};