import { Citation } from "@/types/chat";

export const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT_MS = Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS) || 60000;

export interface BackendSource {
  title: string;
  snippet: string;
  score?: number | null;
}

export interface ChatApiResponse {
  query?: string;
  answer: string;
  sources: Citation[];
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
 * Tự động chuyển sang offline fallback nếu backend chưa khởi chạy hoặc gặp lỗi kết nối.
 */
export async function queryChatApi(
  query: string,
  topK = 3,
  temperature = 0.2
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

  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: trimmed,
        top_k: topK,
        temperature,
      }),
      signal: AbortSignal.timeout(DEFAULT_TIMEOUT_MS),
    });

    if (res.ok) {
      const data = await res.json();
      const sources: Citation[] = (data.sources || []).map((s: BackendSource) => ({
        title: s.title,
        snippet: s.snippet,
        raw: s.snippet, // Đảm bảo tính tương thích ngược cho cả template hiển thị cũ và mới
        score: typeof s.score === "number" ? s.score : null,
      }));

      return {
        query: data.query || trimmed,
        answer: data.answer || "",
        sources,
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

    if (res.status === 500) {
      const errData = await res.json().catch(() => null);
      console.warn("Backend 500 error:", errData);
    }
  } catch (err) {
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
}

/**
 * Lấy danh mục văn bản quy phạm pháp luật từ FastAPI (/api/documents)
 */
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
      }) => ({
        id: doc.id,
        category: doc.category,
        typeLabel: doc.type_label,
        typeBadgeBg:
          doc.category === "luat"
            ? "bg-red-50 border-red-200"
            : doc.category === "quy-chuan"
            ? "bg-emerald-50 border-emerald-200"
            : "bg-blue-50 border-blue-200",
        typeBadgeText:
          doc.category === "luat"
            ? "text-red-700"
            : doc.category === "quy-chuan"
            ? "text-emerald-700"
            : "text-blue-700",
        title: doc.title,
        number: doc.number,
        date: doc.date,
        status: doc.status,
        desc: doc.desc,
      }));
    }
  } catch (err) {
    console.warn("Could not fetch documents from FastAPI backend:", err);
  }
  return [];
}

/**
 * Tìm kiếm nhanh căn cứ pháp lý (/api/search)
 */
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