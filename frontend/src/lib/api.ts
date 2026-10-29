import { Citation, UserProfile, SessionItem, AuditLogItem } from "@/types/chat";
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

export interface HealthCheckResult {
  isOnline: boolean;
  message: string;
  status?: string;
}

/**
 * Kiểm tra trạng thái máy chủ FastAPI (/api/health)
 */
export async function checkBackendHealth(): Promise<HealthCheckResult> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/health`, {
      method: "GET",
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) {
      const data = await res.json();
      return {
        isOnline: true,
        status: data.status || "ok",
        message: data.message || "Hệ thống AI Chatbot đang hoạt động ổn định",
      };
    }
    return {
      isOnline: false,
      message: `Máy chủ phản hồi mã lỗi ${res.status}`,
    };
  } catch {
    return {
      isOnline: false,
      message: "Không thể kết nối đến máy chủ Backend (Port 8000)",
    };
  }
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

  // Fallback offline chuẩn xác theo văn bản luật khi backend chưa chạy
  const fallback = getOfflineFallback(trimmed);
  return {
    query: trimmed,
    answer: fallback.answer,
    sources: fallback.sources,
    isFallback: true,
  };
}

function getOfflineFallback(query: string): { answer: string; sources: Citation[] } {
  const qLower = query.toLowerCase();

  if (qLower.includes("rẽ phải") || qLower.includes("đèn đỏ")) {
    return {
      answer: `### Kết luận: Không được phép rẽ phải khi đèn đỏ

Khi ngã tư có tín hiệu đèn đỏ mà **không có biển báo phụ** (như biển *"Đèn đỏ được phép rẽ phải"*), không có đèn mũi tên xanh và không có hiệu lệnh của CSGT, người điều khiển xe máy **bắt buộc phải dừng trước vạch dừng xe**.

#### Khung hình phạt áp dụng:
- **Phạt tiền trực tiếp:** **800.000đ – 1.000.000đ** (Mức phổ biến áp dụng: **900.000 VNĐ**).
- **Hình thức phạt bổ sung:** Tước quyền sử dụng Giấy phép lái xe từ **01 đến 03 tháng** (Nếu gây TNGT: Tước **02 – 04 tháng**).
- **Tạm giữ phương tiện:** Không tạm giữ nếu người điều khiển xuất trình đủ giấy tờ xe hợp lệ.

> **Căn cứ pháp lý:** Điểm e Khoản 4 và Điểm b Khoản 10 Điều 6 Nghị định 100/2019/NĐ-CP (sửa đổi, bổ sung bởi Nghị định 123/2021/NĐ-CP).`,
      sources: [
        {
          title: "Điểm e Khoản 4 Điều 6 Nghị định 100/2019/NĐ-CP",
          snippet: "Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy không chấp hành hiệu lệnh của đèn tín hiệu giao thông.",
          raw: "Phạt tiền từ 800.000 đồng đến 1.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy không chấp hành hiệu lệnh của đèn tín hiệu giao thông.",
          score: 0.95,
        },
        {
          title: "Nghị định 123/2021/NĐ-CP",
          snippet: "Bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng; gây tai nạn giao thông tước từ 02 đến 04 tháng.",
          raw: "Bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng; gây tai nạn giao thông tước từ 02 đến 04 tháng.",
          score: 0.9,
        },
      ],
    };
  }

  if (qLower.includes("nồng độ cồn") || qLower.includes("rượu") || qLower.includes("bia")) {
    return {
      answer: `### Kết luận: Nghiêm cấm tuyệt đối nồng độ cồn khi điều khiển phương tiện

Luật Trật tự, an toàn giao thông đường bộ 2024 nghiêm cấm triệt để hành vi điều khiển phương tiện tham gia giao thông mà trong máu hoặc hơi thở có nồng độ cồn.

#### Mức xử phạt kịch khung đối với xe máy:
- **Phạt tiền:** **6.000.000đ – 8.000.000đ** (khi nồng độ cồn vượt quá 80mg/100ml máu hoặc vượt quá 0.4mg/l khí thở).
- **Hình phạt bổ sung:** Tước quyền sử dụng GPLX từ **22 đến 24 tháng**.
- **Biện pháp ngăn chặn:** Tạm giữ phương tiện đến **07 ngày làm việc**.

> **Căn cứ pháp lý:** Điểm e Khoản 8 Điều 6 Nghị định 100/2019/NĐ-CP.`,
      sources: [
        {
          title: "Điểm e Khoản 8 Điều 6 Nghị định 100/2019/NĐ-CP",
          snippet: "Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở.",
          raw: "Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng đối với người điều khiển xe mô tô, xe gắn máy mà trong máu hoặc hơi thở có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở.",
          score: 0.98,
        },
      ],
    };
  }

  return {
    answer: `### Giải đáp quy định pháp luật về: "${query}"

Căn cứ Luật Trật tự, an toàn giao thông đường bộ 2024 và các Nghị định hướng dẫn xử phạt vi phạm hành chính:

- Mọi hành vi vi phạm trật tự an toàn giao thông đường bộ đều được xử lý theo nguyên tắc đúng người, đúng hành vi, đúng tính chất và mức độ vi phạm.
- Người tham gia giao thông có nghĩa vụ chấp hành nghiêm chỉnh hệ thống báo hiệu đường bộ và hiệu lệnh của người điều khiển giao thông.

> *(Lưu ý: Bạn có thể khởi động máy chủ FastAPI tại cổng 8000 để nhận phân tích chi tiết từ mô hình AI RAG đầy đủ).*`,
    sources: [
      {
        title: "Luật Trật tự, an toàn giao thông đường bộ 2024 (Luật số 36/2024/QH15)",
        snippet: "Quy tắc chung và quy định chấp hành an toàn giao thông đường bộ.",
        raw: "Quy tắc chung và quy định chấp hành an toàn giao thông đường bộ.",
        score: 0.85,
      },
    ],
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

  async createSession(title?: string): Promise<SessionItem> {
    const res = await fetch(`${BACKEND_BASE_URL}/api/sessions`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ title: title || "Cuộc trò chuyện mới" }),
    });
    if (!res.ok) {
      throw new Error("Không thể tạo phiên trò chuyện mới.");
    }
    return res.json();
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
// VĂN BẢN PHÁP LUẬT
// ==============================================================================
export interface RelatedDocItem {
  relationType: "goc" | "sua_doi";
  relationLabel: string;
  title: string;
  number: string;
  sourceUrl: string;
}

export interface LegalDocItem {
  id: string;
  category: "luat" | "nghi-dinh" | "thong-tu" | "quy-chuan";
  typeLabel: string;
  typeBadgeBg: string;
  typeBadgeText: string;
  title: string;
  number: string;
  date: string;
  status: string;
  desc: string;
  sourceUrl?: string;
  isConsolidated?: boolean;
  relatedDocs?: RelatedDocItem[];
}

export async function fetchLegalDocuments(): Promise<LegalDocItem[]> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/documents`, {
      method: "GET",
      signal: AbortSignal.timeout(4000),
    });
    if (res.ok) {
      const data = await res.json();
      return (data.documents || []).map((doc: {
        id: string;
        category: "luat" | "nghi-dinh" | "thong-tu" | "quy-chuan";
        type_label: string;
        title: string;
        number: string;
        date: string;
        status: string;
        desc: string;
        source_url?: string;
        is_consolidated?: boolean;
        related_docs?: Array<{
          relation_type: "goc" | "sua_doi";
          relation_label: string;
          title: string;
          number: string;
          source_url: string;
        }>;
      }) => ({
        id: doc.id,
        category: doc.category,
        typeLabel: doc.type_label,
        typeBadgeBg:
          doc.category === "luat"
            ? "bg-red-50 border-red-200"
            : doc.category === "quy-chuan"
            ? "bg-emerald-50 border-emerald-200"
            : doc.category === "thong-tu"
            ? "bg-purple-50 border-purple-200"
            : "bg-blue-50 border-blue-200",
        typeBadgeText:
          doc.category === "luat"
            ? "text-red-700"
            : doc.category === "quy-chuan"
            ? "text-emerald-700"
            : doc.category === "thong-tu"
            ? "text-purple-700"
            : "text-blue-700",
        title: doc.title,
        number: doc.number,
        date: doc.date,
        status: doc.status,
        desc: doc.desc,
        sourceUrl: doc.source_url || "",
        isConsolidated: !!doc.is_consolidated,
        relatedDocs: (doc.related_docs || []).map((r) => ({
          relationType: r.relation_type,
          relationLabel: r.relation_label,
          title: r.title,
          number: r.number,
          sourceUrl: r.source_url,
        })),
      }));
    }
  } catch (err) {
    console.warn("Could not fetch documents from FastAPI backend:", err);
  }
  return [];
}

export async function searchLegalSources(query: string, topK = 3): Promise<Citation[]> {
  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK }),
      signal: AbortSignal.timeout(10000),
    });
    if (res.ok) {
      const data = await res.json();
      return (data.sources || []).map((s: BackendSource) => ({
        title: s.title,
        snippet: s.snippet,
        raw: s.snippet,
        score: typeof s.score === "number" ? s.score : null,
      }));
    }
  } catch (err) {
    console.warn("Search API failed:", err);
  }
  return [];
}
