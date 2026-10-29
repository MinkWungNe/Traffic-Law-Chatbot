import { create } from "zustand";
import { UserProfile } from "@/types/chat";

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  isAdmin: boolean;

  setAuth: (token: string, user: UserProfile) => void;
  clearAuth: () => void;
  initFromStorage: () => void;
}

const TOKEN_KEY = "vinalaw_auth_token";
const USER_KEY = "vinalaw_auth_user";

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  isAdmin: false,

  setAuth: (token: string, user: UserProfile) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    set({
      token,
      user,
      isAuthenticated: true,
      isAdmin: user.role === "admin",
    });
  },

  clearAuth: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    set({
      token: null,
      user: null,
      isAuthenticated: false,
      isAdmin: false,
    });
  },

  initFromStorage: () => {
    if (typeof window === "undefined") return;
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      if (storedToken && storedUser) {
        const parsedUser: UserProfile = JSON.parse(storedUser);
        set({
          token: storedToken,
          user: parsedUser,
          isAuthenticated: true,
          isAdmin: parsedUser.role === "admin",
        });
      }
    } catch (e) {
      console.warn("Lỗi đọc auth data từ localStorage:", e);
    }
  },
}));

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return useAuthStore.getState().token || localStorage.getItem(TOKEN_KEY);
}
