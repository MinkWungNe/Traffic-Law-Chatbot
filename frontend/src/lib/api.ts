import { Citation, UserProfile, SessionItem, AuditLogItem } from "@/types/chat";
import { BenchmarkReportResponse } from "@/types/benchmark";
import { getAuthToken } from "@/stores/useAuthStore";

export const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS) || 60000;

function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export interface BackendSource {
  title: string;
  snippet: string;
  score?: number | null;
}

export interface ChatApiResponse {
  query?: string;
  answer: string;
  sources: Citation[];
  sessionId?: string;
  isFallback: boolean;
  error?: string;
}

function getOfflineFallback(query: string): { answer: string; sources: Citation[] } {
  return {
    answer: `### Thông báo kết nối máy chủ AI\n\nHệ thống hiện chưa nhận được phản hồi từ máy chủ xử lý AI (FastAPI tại ${BACKEND_BASE_URL}).\n\n- Câu hỏi: **"${query}"**\n- Vui lòng kiểm tra lại kết nối hoặc thử lại sau khi máy chủ hoàn tất khởi động.`,
    sources: [],
  };
}

/**
 * Gửi câu hỏi đến FastAPI backend (/api/chat).
 * Tự động gắn token và session_id nếu đã đăng nhập.
 * Hỗ trợ AbortSignal để hủy truy vấn ngay lập tức khi người dùng bấm dừng.
 */
export async function queryChatApi(
  query: string,
  sessionId?: string | null,
  topK = 3,
  temperature = 0.2,
  signal?: AbortSignal
): Promise<ChatApiResponse> {
  const trimmed = query.trim();
  if (trimmed.length < 2) {
    return {
      answer: "Câu hỏi của bạn quá ngắn. Vui lòng nhập ít nhất 2 ký tự để hệ thống có thể tra cứu luật chính xác.",
      sources: [],
      isFallback: true,
      error: "Query too short",
    };
  }

  if (signal?.aborted) {
    throw new DOMException("The operation was aborted", "AbortError");
  }

  try {
    const timeoutSignal = AbortSignal.timeout(DEFAULT_TIMEOUT_MS);
    let fetchSignal: AbortSignal;
    if (signal && typeof AbortSignal.any === "function") {
      fetchSignal = AbortSignal.any([signal, timeoutSignal]);
    } else if (signal) {
      fetchSignal = signal;
    } else {
      fetchSignal = timeoutSignal;
    }

    const res = await fetch(`${BACKEND_BASE_URL}/api/chat`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        query: trimmed,
        session_id: sessionId || null,
        top_k: topK,
        temperature,
      }),
      signal: fetchSignal,
    });

    if (signal?.aborted) {
      throw new DOMException("The operation was aborted", "AbortError");
    }

    if (res.ok) {
      const data = await res.json();
      const sources: Citation[] = (data.sources || []).map((s: BackendSource) => ({
        title: s.title,
        snippet: s.snippet,
        raw: s.snippet,
        score: typeof s.score === "number" ? s.score : null,
      }));

      return {
        query: data.query || trimmed,
        answer: data.answer || "",
        sources,
        sessionId: data.session_id,
        isFallback: false,
      };
    }

    if (res.status === 422) {
      const errData = await res.json().catch(() => null);
      const detailMsg = errData?.detail?.[0]?.msg || "Dữ liệu câu hỏi không hợp lệ.";
      return {
        answer: `Lỗi yêu cầu (422): ${detailMsg}`,
        sources: [],
        isFallback: true,
        error: detailMsg,
      };
    }
  } catch (err: any) {
    if (signal?.aborted || err?.name === "AbortError") {
      throw err;
    }
    console.warn("FastAPI backend offline or timeout, switching to offline fallback:", err);
  }

  // Fallback thông báo khi backend chưa kết nối được
  const fallback = getOfflineFallback(trimmed);
  return {
    query: trimmed,
    answer: fallback.answer,
    sources: fallback.sources,
    isFallback: true,
  };
}

// ==============================================================================
// CÁC HÀM XÁC THỰC & HỒ SƠ TÀI KHOẢN (AUTH API)
// ==============================================================================
export const authApi = {
  async register(email: string, password: string): Promise<{ access_token: string; user: UserProfile }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đăng ký không thành công.");
    }
    return res.json();
  },

  async login(email: string, password: string): Promise<{ access_token: string; user: UserProfile }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đăng nhập không thành công.");
    }
    return res.json();
  },

  async getMe(): Promise<UserProfile> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/auth/me`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Không thể lấy thông tin người dùng.");
    }
    return res.json();
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/auth/change-password`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đổi mật khẩu không thành công.");
    }
    return res.json();
  },
};

// ==============================================================================
// CÁC HÀM QUẢN LÝ PHIÊN TRÒ CHUYỆN (SESSION API)
// ==============================================================================
export const sessionApi = {
  async listSessions(): Promise<SessionItem[]> {
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/api/sessions`, {
        method: "GET",
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        return data.sessions || [];
      }
    } catch (e) {
      console.warn("Không thể tải danh sách phiên từ backend:", e);
    }
    return [];
  },

  async getSessionDetail(sessionId: string): Promise<{
    id: string;
    title: string;
    is_pinned: boolean;
    messages: Array<{
      id: string;
      role: "user" | "bot";
      content: string;
      sources?: Citation[];
      timestamp?: string;
    }>;
  }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/sessions/${sessionId}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Không thể tải chi tiết phiên trò chuyện.");
    }
    return res.json();
  },

  async updateSession(
    sessionId: string,
    data: { title?: string; is_pinned?: boolean }
  ): Promise<SessionItem> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/sessions/${sessionId}`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      throw new Error("Cập nhật phiên trò chuyện thất bại.");
    }
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/sessions/${sessionId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Xóa phiên trò chuyện thất bại.");
    }
  },
};

// ==============================================================================
// CÁC HÀM QUẢN TRỊ VIÊN ADMIN (ADMIN API)
// ==============================================================================
export const adminApi = {
  async listUsers(page = 1, limit = 20, search = ""): Promise<{ users: UserProfile[]; total: number }> {
    const query = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    if (search.trim()) {
      query.append("search", search.trim());
    }

    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/users?${query.toString()}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Không thể tải danh sách người dùng.");
    }
    return res.json();
  },

  async updateUserStatus(userId: string, isActive: boolean, reason?: string): Promise<{ message: string }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/users/${userId}/status`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ is_active: isActive, reason }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Cập nhật trạng thái người dùng thất bại.");
    }
    return res.json();
  },

  async resetUserPassword(userId: string, newPassword: string): Promise<{ message: string }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/users/${userId}/reset-password`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ new_password: newPassword }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đặt lại mật khẩu thất bại.");
    }
    return res.json();
  },

  async deleteUser(userId: string): Promise<{ message: string }> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/users/${userId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Xóa người dùng thất bại.");
    }
    return res.json();
  },

  async listAuditLogs(page = 1, limit = 30, action = ""): Promise<{ logs: AuditLogItem[]; total: number }> {
    const query = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    if (action.trim()) {
      query.append("action", action.trim());
    }

    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/audit-logs?${query.toString()}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Không thể tải nhật ký kiểm toán.");
    }
    return res.json();
  },
};

// ==============================================================================
// CÁC HÀM ĐÁNH GIÁ BENCHMARK (BENCHMARK API)
// ==============================================================================
export const benchmarkApi = {
  /**
   * Lấy kết quả benchmark mới nhất từ backend
   */
  async getResults(): Promise<BenchmarkReportResponse> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/admin/benchmark/results`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Lỗi khi tải dữ liệu benchmark (Mã: ${res.status})`);
    }

    return res.json();
  },

  /**
   * Kích hoạt chạy đánh giá benchmark
   */
  async runBenchmark(
    topK = 3,
    maxSamples = 50
  ): Promise<BenchmarkReportResponse> {
    const res = await fetch(
      `${BACKEND_BASE_URL}/api/admin/benchmark/run?top_k=${topK}&max_samples=${maxSamples}`,
      {
        method: "POST",
        headers: getAuthHeaders(),
      }
    );

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Lỗi khi thực thi benchmark (Mã: ${res.status})`);
    }

    return res.json();
  },
};
