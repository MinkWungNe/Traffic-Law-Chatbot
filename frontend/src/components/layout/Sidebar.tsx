"use client";

import React, { useState } from "react";
import { useChatStore } from "@/stores/useChatStore";
import {
  Plus,
  Bot,
  BookOpen,
  HelpCircle,
  ChevronDown,
  MoreVertical,
  UserCircle,
  Pin,
  Edit3,
  Trash2,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const {
    activeTab, setActiveTab,
    sessionTitle, setSessionTitle,
    clearMessages,
  } = useChatStore();

  const [menuOpen, setMenuOpen] = useState(false);
  const [menuPosition, setMenuPosition] = useState<{ top: number; left: number }>({
    top: 0,
    left: 275,
  });
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const isChatSelected = activeTab === "chat";

  const handleNewChat = () => {
    clearMessages();
    setSessionTitle("Cuộc trò chuyện mới");
    setActiveTab("chat");
  };

  const navItems = [
    { id: "chat" as const, label: "Trợ lý AI", icon: Bot },
    { id: "docs" as const, label: "Tra cứu Văn bản Pháp luật", icon: BookOpen },
    { id: "faq" as const, label: "Câu hỏi thường gặp", icon: HelpCircle },
  ];

  const handleOpenMenu = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (menuOpen) {
      setMenuOpen(false);
      return;
    }
    const rect = e.currentTarget.getBoundingClientRect();
    // Neo menu bên ngoài và bên PHẢI sidebar (270px + 5px khoảng đệm = 275px). Giới hạn để không bị tràn đáy màn hình
    const calculatedTop = Math.min(rect.top + 40, typeof window !== "undefined" ? window.innerHeight - 140 : rect.top);
    setMenuPosition({
      top: Math.max(10, calculatedTop),
      left: 210,
    });
    setMenuOpen(true);
  };

  return (
    <>
      <aside className="w-[270px] shrink-0 bg-[#ecf0f6] border-r border-[#D5DFEB] shadow-lg flex flex-col h-screen select-none z-20 relative overflow-hidden">
        {/* Layer 0: Hình nền Sidebar neo ở dưới, full chiều ngang, chiều cao tự nhiên theo tỉ lệ, fade mờ cạnh trên 20% */}
        <div
          className="absolute bottom-0 left-0 right-0 w-full pointer-events-none select-none z-0 overflow-hidden opacity-20 leading-none"
          style={{
            maskImage: "linear-gradient(to bottom, transparent 0%, #000 20%, #000 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, transparent 0%, #000 20%, #000 100%)",
          }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/assets/SidebarBackGround.jpg"
            alt=""
            className="w-full h-auto block object-cover object-bottom pointer-events-none select-none"
            loading="eager"
          />
        </div>

        {/* PHẦN ĐỈNH: CỐ ĐỊNH / CỨNG, KHÔNG CUỘN */}
        <div className="flex flex-col p-3 pb-0 shrink-0 relative z-10">
          {/* Brand Header */}
          <div className="flex items-center gap-2.5 px-2 py-2 mb-2 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-accent-red flex items-center justify-center shrink-0 shadow-md p-1.5" title="VinaLaw-Traffic">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/assets/Chatbot_Logo.svg" alt="" className="w-full h-full object-contain filter invert brightness-0" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-[15px] tracking-tight text-primary-navy leading-none">VinaLaw-Traffic</span>
              <span className="text-[11px] text-text-muted font-medium mt-1">Trợ lý AI Luật Giao thông</span>
            </div>
          </div>

          {/* New Chat Button with Spotlight Border */}
          <button
            onClick={handleNewChat}
            className="spotlight-border flex items-center gap-3 w-full px-4 py-2.5 rounded-full bg-white shadow-2xs text-text-main mb-4 text-left group relative cursor-pointer shrink-0 transition-all duration-150 ease-out active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-red/40 focus-visible:ring-offset-1 focus-visible:ring-offset-[#ecf0f6]"
            style={{ "--glow-color": "#B91C1C" } as React.CSSProperties}
          >
            <div className="relative z-10 flex items-center gap-3 w-full">
              <Plus size={18} className="text-accent-red shrink-0" strokeWidth={2.5} />
              <span className="text-[13px] font-semibold text-slate-800">Cuộc trò chuyện mới</span>
            </div>
          </button>

          {/* Main Navigation Tabs */}
          <nav className="flex flex-col gap-1 mb-3 shrink-0">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`group flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all duration-150 ease-out cursor-pointer active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-navy/40 focus-visible:ring-offset-1 focus-visible:ring-offset-[#ecf0f6] ${
                    isActive
                      ? "bg-white text-primary-navy font-bold shadow-md border border-slate-200/80"
                      : "text-slate-600 font-medium bg-transparent border border-transparent hover:bg-white/70 hover:text-primary-navy hover:shadow-xs hover:border-white/80"
                  }`}
                >
                  <Icon
                    size={18}
                    className={`shrink-0 transition-colors duration-150 ${
                      isActive ? "text-accent-red" : "text-slate-400 group-hover:text-accent-red"
                    }`}
                  />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* PHẦN GIỮA: LỊCH SỬ TRÒ CHUYỆN */}
        <div className="flex-1 flex flex-col min-h-0 px-3 pb-2 overflow-hidden relative z-10">
          {/* Tiêu đề Lịch sử & Nút Thu gọn/Mở rộng */}
          <div
            onClick={() => {
              setIsHistoryCollapsed(!isHistoryCollapsed);
              setMenuOpen(false);
            }}
            className="group flex items-center justify-between px-2.5 py-1.5 mb-1 text-slate-500 hover:text-slate-900 cursor-pointer transition-colors duration-150 shrink-0 select-none"
            title={isHistoryCollapsed ? "Mở rộng lịch sử trò chuyện" : "Thu gọn lịch sử trò chuyện"}
          >
            <span className="text-[11px] font-bold tracking-wider uppercase transition-colors duration-150">
              Lịch sử trò chuyện
            </span>
            <ChevronDown
              size={16}
              className={`text-slate-400 group-hover:text-slate-700 transition-transform duration-200 shrink-0 ${
                isHistoryCollapsed ? "-rotate-90" : "rotate-0"
              }`}
            />
          </div>

          {/* KHUNG ĐỰNG ITEM PHIÊN CHAT */}
          {!isHistoryCollapsed && (
            <div
              onScroll={() => {
                if (menuOpen) setMenuOpen(false);
              }}
              className="flex-1 overflow-y-auto min-h-0 pr-1 flex flex-col gap-1 select-none"
            >
              <div
                onClick={() => setActiveTab("chat")}
                className={`group relative flex items-center justify-between w-full px-2.5 py-1 rounded-xl transition-all duration-150 text-[12.5px] select-none cursor-pointer active:scale-[0.99] ${
                  isChatSelected
                    ? "bg-white/75 border border-white/85 shadow-xs text-primary-navy"
                    : "border border-transparent text-slate-700 hover:text-primary-navy hover:bg-white/75 hover:shadow-xs hover:border-white/85 active:shadow-sm"
                }`}
              >
                <span className={`truncate flex-1 pr-1 transition-all ${isChatSelected ? "font-bold text-primary-navy" : "font-medium"}`}>
                  {sessionTitle}
                </span>
                <button
                  type="button"
                  onClick={handleOpenMenu}
                  className={`pt-1 pb-1 bg-transparent hover:bg-transparent transition-opacity shrink-0 flex items-center justify-center cursor-pointer ${
                    menuOpen ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                  }`}
                  title="Tùy chọn phiên"
                >
                  <MoreVertical
                    size={16}
                    className={`transition-colors duration-150 ${
                      menuOpen ? "text-slate-900" : "text-slate-400 hover:text-slate-800"
                    }`}
                  />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* PHẦN ĐÁY: TÀI KHOẢN */}
        <div className="p-3 border-t border-[#D5DFEB] shrink-0 relative z-10">
          <button
            onClick={() => setActiveTab("login")}
            className={`group flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all duration-150 ease-out cursor-pointer active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-navy/40 focus-visible:ring-offset-1 focus-visible:ring-offset-[#ecf0f6] ${
              activeTab === "login"
                ? "bg-white text-primary-navy font-bold shadow-sm border border-slate-200/80"
                : "bg-white/45 backdrop-blur-[2px] border border-white/60 text-slate-700 font-medium shadow-2xs hover:bg-white/80 hover:text-primary-navy hover:shadow-xs hover:border-white/90"
            }`}
          >
            <UserCircle
              size={18}
              className={`shrink-0 transition-colors duration-150 ${
                activeTab === "login" ? "text-accent-red" : "text-slate-500 group-hover:text-accent-red"
              }`}
            />
            <span>Tài khoản / Đăng nhập</span>
          </button>
        </div>
      </aside>

      {/* FLYOUT MENU 3 CHẤM: HIỂN THỊ ĐỘC LẬP BÊN NGOÀI VÀ BÊN PHẢI CỦA SIDEBAR */}
      {menuOpen && (
        <>
          {/* Backdrop vô hình đóng menu khi click ra ngoài */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setMenuOpen(false)}
          />

          {/* Menu ngữ cảnh đặt tại tọa độ fixed bên phải sidebar, thẳng hàng icon 3 chấm */}
          <div
            style={{
              top: `${menuPosition.top}px`,
              left: `${menuPosition.left}px`,
            }}
            className="fixed z-50 w-38 bg-white rounded-xl shadow-xl border border-slate-200/90 py-1 flex flex-col text-[12px] text-slate-700 animate-in fade-in zoom-in-95 duration-150"
          >
            <button
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors cursor-pointer"
            >
              <Pin size={14} className="text-slate-500 shrink-0" />
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
              <Edit3 size={14} className="text-slate-500 shrink-0" />
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
              <Trash2 size={14} className="text-red-500 shrink-0" />
              <span>Xóa</span>
            </button>
          </div>
        </>
      )}
    </>
  );
};
