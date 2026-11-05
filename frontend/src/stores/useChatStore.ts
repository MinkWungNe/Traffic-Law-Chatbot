import { create } from "zustand";
import { ChatMessage, SessionItem } from "@/types/chat";
import { queryChatApi, sessionApi } from "@/lib/api";
import { useAuthStore } from "./useAuthStore";

// Controller lưu trữ tham chiếu phiên request hiện tại để hỗ trợ hủy tức thời
let activeAbortController: AbortController | null = null;

interface ChatState {
  messages: ChatMessage[];
  activeTab: "chat" | "docs" | "faq" | "login" | "admin";
  sessionTitle: string;
  currentSessionId: string | null;
  sessions: SessionItem[];
  inputText: string;
  isLoading: boolean;

  setActiveTab: (tab: "chat" | "docs" | "faq" | "login" | "admin") => void;
  setInputText: (text: string) => void;
  setSessionTitle: (title: string) => void;
  setCurrentSessionId: (id: string | null) => void;
  clearMessages: () => void;
  sendMessage: (query: string) => Promise<void>;
  stopGeneration: () => void;

  // Multi-session actions
  loadSessions: () => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  createNewSession: () => void;
  renameSession: (sessionId: string, newTitle: string) => Promise<void>;
  togglePinSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  activeTab: "chat",
  sessionTitle: "Tư vấn luật giao thông",
  currentSessionId: null,
  sessions: [],
  inputText: "",
  isLoading: false,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setInputText: (text) => set({ inputText: text }),
  setSessionTitle: (title) => set({ sessionTitle: title }),
  setCurrentSessionId: (id) => set({ currentSessionId: id }),
  clearMessages: () => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    set({ messages: [], inputText: "", currentSessionId: null, isLoading: false });
  },

  loadSessions: async () => {
    const isAuth = useAuthStore.getState().isAuthenticated;
    if (!isAuth) {
      set({ sessions: [] });
      return;
    }
    try {
      const list = await sessionApi.listSessions();
      set({ sessions: list });
    } catch (e) {
      console.warn("Lỗi load sessions:", e);
    }
  },

  selectSession: async (sessionId: string) => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    set({ isLoading: true, activeTab: "chat" });
    try {
      const detail = await sessionApi.getSessionDetail(sessionId);
      const formattedMessages: ChatMessage[] = detail.messages.map((m) => ({
        id: m.id,
        role: m.role as "user" | "bot",
        content: m.content,
        sources: m.sources,
        timestamp: m.timestamp || new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      }));
      set({
        currentSessionId: detail.id,
        sessionTitle: detail.title,
        messages: formattedMessages,
        isLoading: false,
      });
    } catch (e) {
      console.error("Lỗi khi tải chi tiết phiên:", e);
      set({ isLoading: false });
    }
  },

  createNewSession: () => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    set({
      currentSessionId: null,
      sessionTitle: "Cuộc trò chuyện mới",
      messages: [],
      inputText: "",
      isLoading: false,
      activeTab: "chat",
    });
  },

  renameSession: async (sessionId: string, newTitle: string) => {
    const trimmed = newTitle.trim();
    if (!trimmed) return;
    try {
      await sessionApi.updateSession(sessionId, { title: trimmed });
      set((state) => ({
        sessionTitle: state.currentSessionId === sessionId ? trimmed : state.sessionTitle,
        sessions: state.sessions.map((s) => (s.id === sessionId ? { ...s, title: trimmed } : s)),
      }));
    } catch (e) {
      console.error("Lỗi đổi tên phiên:", e);
    }
  },

  togglePinSession: async (sessionId: string) => {
    const current = get().sessions.find((s) => s.id === sessionId);
    if (!current) return;
    const nextPin = !current.is_pinned;
    try {
      await sessionApi.updateSession(sessionId, { is_pinned: nextPin });
      await get().loadSessions();
    } catch (e) {
      console.error("Lỗi ghim phiên:", e);
    }
  },

  deleteSession: async (sessionId: string) => {
    try {
      await sessionApi.deleteSession(sessionId);
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== sessionId),
        ...(state.currentSessionId === sessionId
          ? { currentSessionId: null, sessionTitle: "Cuộc trò chuyện mới", messages: [] }
          : {}),
      }));
    } catch (e) {
      console.error("Lỗi xóa phiên:", e);
    }
  },

  stopGeneration: () => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }

    const stopNoticeMessage: ChatMessage = {
      id: `bot-stop-${Date.now()}`,
      role: "bot",
      content: "Người dùng đã dừng phản hồi.",
      isStopped: true,
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    };

    set((state) => ({
      isLoading: false,
      messages: [...state.messages, stopNoticeMessage],
    }));
  },

  sendMessage: async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || get().isLoading) return;

    if (activeAbortController) {
      activeAbortController.abort();
    }
    const controller = new AbortController();
    activeAbortController = controller;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      inputText: "",
      sessionTitle:
        state.messages.length === 0
          ? trimmed.length > 30
            ? trimmed.substring(0, 30) + "..."
            : trimmed
          : state.sessionTitle,
    }));

    try {
      const activeSid = get().currentSessionId;
      const res = await queryChatApi(trimmed, activeSid, 3, 0.2, controller.signal);

      // Nếu đã bị hủy trong quá trình xử lý thì không ghi đè kết quả
      if (controller.signal.aborted) {
        return;
      }

      const botMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        role: "bot",
        content: res.answer,
        sources: res.sources,
        isFallback: res.isFallback,
        timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
      };

      set((state) => ({
        messages: [...state.messages, botMessage],
        currentSessionId: res.sessionId || state.currentSessionId,
        isLoading: false,
      }));

      // Cập nhật session nội bộ trong Zustand store (không cần gọi lại GET /api/sessions qua mạng)
      if (res.sessionId && useAuthStore.getState().isAuthenticated) {
        set((state) => {
          const sid = res.sessionId!;
          const existing = state.sessions.find((s) => s.id === sid);
          if (existing) {
            const updated: SessionItem = {
              ...existing,
              updated_at: new Date().toISOString(),
              message_count: (existing.message_count || 0) + 2,
            };
            const others = state.sessions.filter((s) => s.id !== sid);
            return {
              sessions: updated.is_pinned
                ? [updated, ...others]
                : [...others.filter((s) => s.is_pinned), updated, ...others.filter((s) => !s.is_pinned)],
            };
          } else {
            const newSessionItem: SessionItem = {
              id: sid,
              title: state.sessionTitle,
              is_pinned: false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              message_count: 2,
            };
            return {
              sessions: [newSessionItem, ...state.sessions],
            };
          }
        });
      }
    } catch (err: unknown) {
      if ((err as { name?: string })?.name === "AbortError" || controller.signal.aborted) {
        // Yêu cầu đã được dừng bởi người dùng, stopGeneration đã hiển thị thông báo
        return;
      }
      console.error("Error sending message:", err);
      set({
        isLoading: false,
      });
    } finally {
      if (activeAbortController === controller) {
        activeAbortController = null;
      }
    }
  },
}));
