import { create } from "zustand";
import { ChatMessage, UserProfile } from "@/types/chat";
import { queryChatApi, checkBackendHealth } from "@/lib/api";

interface ChatState {
  messages: ChatMessage[];
  activeTab: "chat" | "docs" | "faq" | "login";
  sessionTitle: string;
  inputText: string;
  fillText: string;
  isLoading: boolean;
  userProfile: UserProfile | null;
  backendStatus: "connected" | "disconnected" | "checking";
  backendMessage: string;

  setActiveTab: (tab: "chat" | "docs" | "faq" | "login") => void;
  setInputText: (text: string) => void;
  setFillText: (text: string) => void;
  setSessionTitle: (title: string) => void;
  clearMessages: () => void;
  setUserProfile: (profile: UserProfile | null) => void;
  checkBackend: () => Promise<boolean>;
  sendMessage: (query: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  activeTab: "chat",
  sessionTitle: "Tư vấn luật giao thông",
  inputText: "",
  fillText: "",
  isLoading: false,
  userProfile: { username: "Chuyên viên tư vấn", fullName: "Nguyễn Văn Luật" },
  backendStatus: "checking",
  backendMessage: "Đang kiểm tra kết nối...",

  setActiveTab: (tab) => set({ activeTab: tab }),
  setInputText: (text) => set({ inputText: text, fillText: text }),
  setFillText: (text) => set({ inputText: text, fillText: text }),
  setSessionTitle: (title) => set({ sessionTitle: title }),
  clearMessages: () => set({ messages: [], inputText: "", fillText: "" }),
  setUserProfile: (profile) => set({ userProfile: profile }),

  checkBackend: async () => {
    set({ backendStatus: "checking", backendMessage: "Đang ping máy chủ..." });
    const res = await checkBackendHealth();
    set({
      backendStatus: res.isOnline ? "connected" : "disconnected",
      backendMessage: res.message,
    });
    return res.isOnline;
  },

  sendMessage: async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || get().isLoading) return;

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
      fillText: "",
      sessionTitle:
        state.messages.length === 0
          ? trimmed.length > 30
            ? trimmed.substring(0, 30) + "..."
            : trimmed
          : state.sessionTitle,
    }));

    try {
      const res = await queryChatApi(trimmed);
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
        isLoading: false,
        backendStatus: res.isFallback ? "disconnected" : "connected",
        backendMessage: res.isFallback
          ? "Đang dùng dữ liệu dự phòng offline (FastAPI backend chưa phản hồi)"
          : "Kết nối API FastAPI hoạt động tốt",
      }));
    } catch (err) {
      console.error("Error sending message:", err);
      set({
        isLoading: false,
        backendStatus: "disconnected",
        backendMessage: "Không thể kết nối API",
      });
    }
  },
}));