"use client";

import React, { useState, useEffect } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { useAuthStore } from "@/stores/useAuthStore";
import { SessionItem } from "@/types/chat";
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
  ShieldAlert,
  LogOut,
  Sparkles,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    sessionTitle,
    currentSessionId,
    sessions,
    loadSessions,
    selectSession,
    createNewSession,
    renameSession,
    togglePinSession,
    deleteSession,
    clearMessages,
  } = useChatStore();

  const { user, isAuthenticated, isAdmin, clearAuth, initFromStorage } = useAuthStore();

  const [menuOpen, setMenuOpen] = useState(false);
  const [activeMenuSession, setActiveMenuSession] = useState<SessionItem | null>(null);
  const [menuPosition, setMenuPosition] = useState<{ top: number; left: number }>({
    top: 0,
    left: 275,
  });
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);

  // Dialog modals (thay thế browser prompt và confirm)
  const [renameModal, setRenameModal] = useState<{
    isOpen: boolean;
    sessionId: string | null;
    title: string;
  } | null>(null);

  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    sessionId: string | null;
    title: string;
  } | null>(null);

  const [logoutModalOpen, setLogoutModalOpen] = useState(false);

  // Khởi tạo Auth từ localStorage khi component tải
  useEffect(() => {
    initFromStorage();
  }, [initFromStorage]);

  // Tải danh sách phiên trò chuyện khi đăng nhập
  useEffect(() => {
    if (isAuthenticated) {
      loadSessions();
    }
  }, [isAuthenticated, loadSessions]);

  const handleNewChat = () => {
    createNewSession();
    setActiveTab("chat");
  };

  const handleConfirmRename = () => {
    if (!renameModal) return;
    const trimmed = renameModal.title.trim();
    if (trimmed) {
      if (renameModal.sessionId) {
        renameSession(renameModal.sessionId, trimmed);
      } else {
        useChatStore.getState().setSessionTitle(trimmed);
      }
    }
    setRenameModal(null);
  };

  const handleConfirmDelete = () => {
    if (!deleteModal) return;
    if (deleteModal.sessionId) {
      deleteSession(deleteModal.sessionId);
    } else {
      clearMessages();
      useChatStore.getState().setSessionTitle("Cuộc trò chuyện mới");
    }
    setDeleteModal(null);
  };

  const handleLogout = () => {
    setLogoutModalOpen(true);
  };

  const navItems = [
    { id: "chat" as const, label: "Trợ lý AI", icon: Bot },
    { id: "docs" as const, label: "Tra cứu Văn bản Pháp luật", icon: BookOpen },
    { id: "faq" as const, label: "Câu hỏi thường gặp", icon: HelpCircle },
    ...(isAdmin ? [{ id: "admin" as const, label: "Quản trị hệ thống", icon: ShieldAlert }] : []),
  ];

  const handleOpenMenu = (e: React.MouseEvent<HTMLButtonElement>, sessionItem: SessionItem | null) => {
    e.stopPropagation();
    setActiveMenuSession(sessionItem);
    const rect = e.currentTarget.getBoundingClientRect();
    const calculatedTop = Math.min(rect.top + 40, typeof window !== "undefined" ? window.innerHeight - 150 : rect.top);
    setMenuPosition({
      top: Math.max(10, calculatedTop),
      left: 210,
    });
    setMenuOpen(true);
  };

  return (
    <>
      <aside className="w-[270px] shrink-0 bg-sidebar border-r border-sidebar-border shadow-lg flex flex-col h-screen select-none z-20 relative overflow-hidden">
        {/* Layer 0: Hình nền Sidebar */}
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

        {/* PHẦN ĐỈNH: CỐ ĐỊNH / CỨNG */}
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
            className="spotlight-border flex items-center gap-3 w-full px-4 py-2.5 rounded-full bg-white shadow-2xs text-text-main mb-4 text-left group relative cursor-pointer shrink-0 transition-all duration-150 ease-out active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-red/40 focus-visible:ring-offset-1 focus-visible:ring-offset-sidebar"
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
                  className={`group flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all duration-150 ease-out cursor-pointer active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-navy/40 focus-visible:ring-offset-1 focus-visible:ring-offset-sidebar ${
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

        {/* PHẦN GIỮA: LỊCH SỬ TRÒ CHUYỆN (MULTI-SESSION) */}
        <div className="flex-1 flex flex-col min-h-0 px-3 pb-2 overflow-hidden relative z-10">
          <div
            onClick={() => {
              setIsHistoryCollapsed(!isHistoryCollapsed);
              setMenuOpen(false);
            }}
            className="group flex items-center justify-between px-2.5 py-1.5 mb-1 text-slate-500 hover:text-slate-900 cursor-pointer transition-colors duration-150 shrink-0 select-none"
            title={isHistoryCollapsed ? "Mở rộng lịch sử trò chuyện" : "Thu gọn lịch sử trò chuyện"}
          >
            <span className="text-[11px] font-bold tracking-wider uppercase transition-colors duration-150">
              Lịch sử trò chuyện {isAuthenticated && `(${sessions.length})`}
            </span>
            <ChevronDown
              size={16}
              className={`text-slate-400 group-hover:text-slate-700 transition-transform duration-200 shrink-0 ${
                isHistoryCollapsed ? "-rotate-90" : "rotate-0"
              }`}
            />
          </div>

          {!isHistoryCollapsed && (
            <div
              onScroll={() => {
                if (menuOpen) setMenuOpen(false);
              }}
              className="flex-1 overflow-y-auto min-h-0 pr-1 flex flex-col gap-1 select-none"
            >
              {/* Nếu là Khách (Guest) */}
              {!isAuthenticated ? (
                <div className="flex flex-col gap-2 p-1">
                  <div
                    onClick={() => setActiveTab("chat")}
                    className={`group relative flex items-center justify-between w-full px-2.5 py-1.5 rounded-xl transition-all duration-150 text-[12.5px] select-none cursor-pointer active:scale-[0.99] ${
                      activeTab === "chat"
                        ? "bg-white/75 border border-white/85 shadow-xs text-primary-navy"
                        : "border border-transparent text-slate-700 hover:text-primary-navy hover:bg-white/75"
                    }`}
                  >
                    <span className="truncate flex-1 pr-1 font-semibold text-primary-navy">
                      {sessionTitle || "Phiên tạm thời"}
                    </span>
                    <span className="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-mono">Khách</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-white/50 border border-slate-200/60 text-[11px] text-slate-500 flex flex-col gap-1.5">
                    <div className="flex items-center gap-1.5 font-semibold text-slate-700">
                      <Sparkles size={13} className="text-accent-red" />
                      <span>Lưu trữ Đa phiên</span>
                    </div>
                    <p className="leading-relaxed">Đăng nhập tài khoản để lưu trữ nhiều phiên trò chuyện trên Supabase.</p>
                    <button
                      onClick={() => setActiveTab("login")}
                      className="text-accent-red hover:underline font-semibold text-left cursor-pointer"
                    >
                      Đăng nhập ngay →
                    </button>
                  </div>
                </div>
              ) : (
                /* Nếu là Thành viên đã đăng nhập (Multi-Session Cloud List) */
                <>
                  {sessions.length === 0 ? (
                    <div className="py-4 text-center text-[12px] text-slate-400">
                      Chưa có phiên trò chuyện nào. Hãy đặt câu hỏi để bắt đầu!
                    </div>
                  ) : (
                    sessions.map((s) => {
                      const isSelected = currentSessionId === s.id;
                      return (
                        <div
                          key={s.id}
                          onClick={() => selectSession(s.id)}
                          className={`group relative flex items-center justify-between w-full px-2.5 py-1.5 rounded-xl transition-all duration-150 text-[12.5px] select-none cursor-pointer active:scale-[0.99] ${
                            isSelected
                              ? "bg-white text-primary-navy font-bold shadow-xs border border-slate-200/80"
                              : "border border-transparent text-slate-700 hover:text-primary-navy hover:bg-white/75 hover:shadow-xs"
                          }`}
                        >
                          <div className="flex items-center gap-1.5 truncate flex-1 pr-1">
                            {s.is_pinned && <Pin size={12} className="text-accent-red shrink-0 fill-accent-red" />}
                            <span className="truncate">{s.title}</span>
                          </div>

                          <button
                            type="button"
                            onClick={(e) => handleOpenMenu(e, s)}
                            className="p-1 text-slate-400 hover:text-slate-800 opacity-0 group-hover:opacity-100 transition-opacity shrink-0 cursor-pointer"
                            title="Tùy chọn phiên"
                          >
                            <MoreVertical size={15} />
                          </button>
                        </div>
                      );
                    })
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* PHẦN ĐÁY: TÀI KHOẢN & ĐĂNG XUẤT */}
        <div className="p-3 border-t border-sidebar-border shrink-0 relative z-10 flex flex-col gap-2">
          {!isAuthenticated ? (
            <button
              onClick={() => setActiveTab("login")}
              className={`group flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] w-full text-left transition-all duration-150 ease-out cursor-pointer active:scale-[0.98] ${
                activeTab === "login"
                  ? "bg-white text-primary-navy font-bold shadow-sm border border-slate-200/80"
                  : "bg-white/45 backdrop-blur-[2px] border border-white/60 text-slate-700 font-medium shadow-2xs hover:bg-white/80 hover:text-primary-navy"
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
          ) : (
            <div className="flex items-center justify-between p-2 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <div className="flex items-center gap-2 min-w-0 pr-1">
                <div className="w-7 h-7 rounded-full bg-accent-red text-white flex items-center justify-center font-bold text-[12px] uppercase shrink-0">
                  {user?.email.charAt(0) || "U"}
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-[12px] font-bold text-primary-navy truncate">{user?.email}</span>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">
                    {user?.role === "admin" ? "Super Admin" : "Thành viên"}
                  </span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors shrink-0 cursor-pointer"
                title="Đăng xuất"
              >
                <LogOut size={16} />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* FLYOUT MENU 3 CHẤM CỦA PHIÊN CHAT */}
      {menuOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
          <div
            style={{
              top: `${menuPosition.top}px`,
              left: `${menuPosition.left}px`,
            }}
            className="fixed z-50 w-38 bg-white rounded-xl shadow-xl border border-slate-200/90 py-1 flex flex-col text-[12px] text-slate-700 animate-in fade-in zoom-in-95 duration-150"
          >
            {activeMenuSession && (
              <button
                onClick={() => {
                  togglePinSession(activeMenuSession.id);
                  setMenuOpen(false);
                }}
                className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors cursor-pointer"
              >
                <Pin size={14} className="text-slate-500 shrink-0" />
                <span>{activeMenuSession.is_pinned ? "Bỏ ghim" : "Ghim lên đầu"}</span>
              </button>
            )}

            <button
              onClick={() => {
                const currentT = activeMenuSession ? activeMenuSession.title : sessionTitle;
                setRenameModal({
                  isOpen: true,
                  sessionId: activeMenuSession ? activeMenuSession.id : null,
                  title: currentT,
                });
                setMenuOpen(false);
              }}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 text-left transition-colors cursor-pointer"
            >
              <Edit3 size={14} className="text-slate-500 shrink-0" />
              <span>Đổi tên</span>
            </button>

            <button
              onClick={() => {
                const currentT = activeMenuSession ? activeMenuSession.title : (sessionTitle || "Cuộc trò chuyện hiện tại");
                setDeleteModal({
                  isOpen: true,
                  sessionId: activeMenuSession ? activeMenuSession.id : null,
                  title: currentT,
                });
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

      {/* MODAL ĐỔI TÊN PHIÊN TRÒ CHUYỆN */}
      {renameModal?.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200/90 w-full max-w-sm p-5 flex flex-col gap-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-primary-navy flex items-center justify-center shrink-0">
                <Edit3 size={16} />
              </div>
              <h3 className="font-bold text-[15px] text-slate-800">Đổi tên cuộc trò chuyện</h3>
            </div>
            <input
              type="text"
              autoFocus
              value={renameModal.title}
              onChange={(e) => setRenameModal({ ...renameModal, title: e.target.value })}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleConfirmRename();
                if (e.key === "Escape") setRenameModal(null);
              }}
              placeholder="Nhập tiêu đề mới..."
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-[13.5px] text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-navy/20 focus:border-primary-navy transition-all"
            />
            <div className="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setRenameModal(null)}
                className="px-3.5 py-2 rounded-xl text-[13px] font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={handleConfirmRename}
                disabled={!renameModal.title.trim()}
                className="px-4 py-2 rounded-xl text-[13px] font-semibold text-white bg-primary-navy hover:bg-slate-800 disabled:opacity-40 transition-all cursor-pointer shadow-xs"
              >
                Lưu thay đổi
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL XÁC NHẬN XÓA PHIÊN TRÒ CHUYỆN */}
      {deleteModal?.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200/90 w-full max-w-sm p-5 flex flex-col gap-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-red-50 text-accent-red flex items-center justify-center shrink-0">
                <Trash2 size={16} />
              </div>
              <h3 className="font-bold text-[15px] text-slate-800">Xóa cuộc trò chuyện?</h3>
            </div>
            <p className="text-[13px] text-slate-600 leading-relaxed">
              Bạn có chắc muốn xóa <span className="font-semibold text-slate-900">&ldquo;{deleteModal.title}&rdquo;</span>? Thao tác này không thể hoàn tác.
            </p>
            <div className="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setDeleteModal(null)}
                className="px-3.5 py-2 rounded-xl text-[13px] font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                className="px-4 py-2 rounded-xl text-[13px] font-semibold text-white bg-accent-red hover:bg-red-700 transition-all cursor-pointer shadow-xs"
              >
                Xóa vĩnh viễn
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL XÁC NHẬN ĐĂNG XUẤT */}
      {logoutModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200/90 w-full max-w-sm p-5 flex flex-col gap-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                <LogOut size={16} />
              </div>
              <h3 className="font-bold text-[15px] text-slate-800">Đăng xuất tài khoản?</h3>
            </div>
            <p className="text-[13px] text-slate-600 leading-relaxed">
              Bạn sẽ trở về chế độ Khách (Guest) và các phiên riêng tư sẽ được ẩn cho đến lần đăng nhập tiếp theo.
            </p>
            <div className="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setLogoutModalOpen(false)}
                className="px-3.5 py-2 rounded-xl text-[13px] font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Ở lại
              </button>
              <button
                type="button"
                onClick={() => {
                  setLogoutModalOpen(false);
                  clearAuth();
                  clearMessages();
                  setActiveTab("chat");
                }}
                className="px-4 py-2 rounded-xl text-[13px] font-semibold text-white bg-accent-red hover:bg-red-700 transition-all cursor-pointer shadow-xs"
              >
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
