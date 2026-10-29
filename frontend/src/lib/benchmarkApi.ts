import { BenchmarkReportResponse } from "@/types/benchmark";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const benchmarkApi = {
  /**
   * Lấy kết quả benchmark mới nhất từ backend
   */
  async getResults(token?: string): Promise<BenchmarkReportResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE_URL}/api/admin/benchmark/results`, {
      method: "GET",
      headers,
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
    token?: string,
    topK: number = 3,
    maxSamples: number = 50
  ): Promise<BenchmarkReportResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(
      `${API_BASE_URL}/api/admin/benchmark/run?top_k=${topK}&max_samples=${maxSamples}`,
      {
        method: "POST",
        headers,
      }
    );

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Lỗi khi thực thi benchmark (Mã: ${res.status})`);
    }

    return res.json();
  },
};
