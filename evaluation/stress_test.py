"""
Module: stress_test.py
Mục đích: Kịch bản kiểm thử tải đồng thời (Stress / Concurrency Testing) cho hệ thống API FastAPI.
          Giả lập 10 - 20 người dùng gửi yêu cầu đồng thời tới máy chủ để đo lường thông lượng (RPS)
          và độ trễ phản hồi (Latency P50, P90, P95, P99).
Người phụ trách: Thành viên 4 (Evaluation & Testing Lead)

Đặc tả chỉ số đo lường hiệu năng công nghiệp:
---------------------------------------------
1. Concurrency (Số người dùng đồng thời): Giả lập 10 - 20 người dùng gửi request cùng một thời điểm.
2. Throughput / RPS (Requests Per Second): Số lượng yêu cầu máy chủ xử lý thành công trong 1 giây.
3. Latency Distribution:
   - Min, Average, Median (P50)
   - P90 (90% người dùng nhận kết quả dưới mốc thời gian này)
   - P95 (95% người dùng nhận kết quả dưới mốc thời gian này)
   - P99 (99% người dùng nhận kết quả dưới mốc thời gian này)
   - Max
4. Cache Acceleration Effect: So sánh độ trễ giữa Cache Miss (truy xuất RAG đầy đủ)
   và Cache Hit (phản hồi tức thì từ bộ đệm RAM).
"""

import os
import sys
import time
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import httpx

# Đảm bảo root directory luôn nằm trong sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Đảm bảo in tiếng Việt chuẩn trên Windows Console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Tập câu hỏi thử nghiệm thực tế đa dạng chủ đề giao thông
SAMPLE_TEST_QUERIES = [
    "Quy định mức phạt vượt đèn đỏ đối với xe máy?",
    "Mức phạt nồng độ cồn kịch khung đối với xe ô tô?",
    "Lùi xe trên đường cao tốc bị phạt bao nhiêu tiền và trừ mấy điểm?",
    "Xe ô tô trễ hạn đăng kiểm trên 01 tháng bị phạt bao nhiêu?",
    "Đi xe máy không đội mũ bảo hiểm bị xử phạt như thế nào?",
    "Chạy quá tốc độ từ 10 đến 20 km/h đối với xe ô tô bị phạt bao nhiêu?",
    "Không mang theo giấy phép lái xe khi tham gia giao thông bị phạt bao nhiêu?",
    "Đi xe máy vào đường cao tốc bị xử phạt mức nào?",
    "Mức phạt đối với hành vi chở quá số người quy định trên xe ô tô?",
    "Bấm còi trong đô thị từ 22h đêm đến 5h sáng hôm sau bị xử phạt ra sao?",
    "Điều kiện tham gia giao thông của xe cơ giới theo Luật Trật tự an toàn giao thông đường bộ?",
    "Thẩm quyền dừng phương tiện kiểm tra giấy tờ của CSGT theo Thông tư 73/2024?",
    "Quy trình bốc biển số xe định danh theo Thông tư 79/2024?",
    "Hành vi lạng lách đánh võng trên đường đô thị bị phạt bao nhiêu tiền?",
    "Người đi bộ vượt giải phân cách không đúng nơi quy định bị phạt bao nhiêu?"
]


class StressTester:
    """
    Bộ máy thực thi kiểm thử tải đồng thời bất đồng bộ (Asynchronous Stress Test Engine).
    Hỗ trợ cả chế độ Live Server (HTTP REST) và chế độ Direct In-Memory Test (ASGITransport).
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        endpoint: str = "/api/chat",
        concurrency: int = 15,
        total_requests: int = 50,
        timeout_seconds: float = 30.0
    ):
        """
        Khởi tạo runner kiểm thử tải.

        Args:
            base_url (str): Địa chỉ máy chủ Backend (mặc định: http://127.0.0.1:8000).
            endpoint (str): Endpoint API cần kiểm thử (mặc định: /api/chat).
            concurrency (int): Số lượng tác vụ / người dùng đồng thời (mặc định: 15).
            total_requests (int): Tổng số requests gửi đi trong phiên kiểm thử.
            timeout_seconds (float): Thời gian tối đa chờ phản hồi cho mỗi request.
        """
        self.base_url = base_url.rstrip("/")
        self.endpoint = endpoint
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.timeout_seconds = timeout_seconds
        self.results: List[Dict[str, Any]] = []

    async def _send_single_request(
        self,
        client: httpx.AsyncClient,
        req_id: int,
        query: str,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Gửi 1 request đơn lẻ và bấm giờ độ trễ chính xác."""
        payload = {
            "query": query,
            "top_k": 3,
            "temperature": 0.2
        }

        url = f"{self.base_url}{self.endpoint}"
        async with semaphore:
            start_t = time.perf_counter()
            status_code = None
            is_cached = False
            error_msg = None

            try:
                resp = await client.post(url, json=payload, timeout=self.timeout_seconds)
                latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
                status_code = resp.status_code

                if resp.status_code == 200:
                    data = resp.json()
                    is_cached = bool(data.get("cached", False))
                else:
                    error_msg = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
                error_msg = str(e)

            return {
                "request_id": req_id,
                "query": query,
                "status_code": status_code,
                "success": (status_code == 200),
                "latency_ms": latency_ms,
                "is_cached": is_cached,
                "error": error_msg
            }

    async def run(self, force_inmemory: bool = False) -> Dict[str, Any]:
        """
        Thực thi kiểm thử tải đồng thời.
        Nếu server Live chưa bật, tự động chuyển sang Direct ASGITransport (In-memory).
        """
        target_url = f"{self.base_url}{self.endpoint}"
        print(f"[STRESS TEST] Mục tiêu: {target_url}")
        print(f"[STRESS TEST] Cấu hình: Concurrency={self.concurrency} | Total Requests={self.total_requests}")

        # Kiểm tra xem máy chủ có đang phản hồi không
        use_inmemory = force_inmemory
        if not use_inmemory:
            try:
                async with httpx.AsyncClient() as check_client:
                    res = await check_client.get(f"{self.base_url}/api/health", timeout=1.5)
                    if res.status_code != 200:
                        use_inmemory = True
            except Exception:
                use_inmemory = True

        semaphore = asyncio.Semaphore(self.concurrency)
        tasks = []

        overall_start = time.perf_counter()

        if use_inmemory:
            print("[STRESS TEST] Máy chủ Live HTTP chưa khởi chạy -> Chuyển sang Direct ASGI Transport (FastAPI in-memory).")
            from backend.src.api.main import app
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                for i in range(self.total_requests):
                    q = SAMPLE_TEST_QUERIES[i % len(SAMPLE_TEST_QUERIES)]
                    tasks.append(self._send_single_request(client, i + 1, q, semaphore))
                self.results = await asyncio.gather(*tasks)
        else:
            print("[STRESS TEST] Kết nối thành công tới Live FastAPI REST Server.")
            limits = httpx.Limits(max_connections=self.concurrency * 2, max_keepalive_connections=self.concurrency)
            async with httpx.AsyncClient(limits=limits) as client:
                for i in range(self.total_requests):
                    q = SAMPLE_TEST_QUERIES[i % len(SAMPLE_TEST_QUERIES)]
                    tasks.append(self._send_single_request(client, i + 1, q, semaphore))
                self.results = await asyncio.gather(*tasks)

        total_elapsed = time.perf_counter() - overall_start
        return self._generate_report(total_elapsed, mode="in_memory_asgi" if use_inmemory else "live_rest")

    def _generate_report(self, total_elapsed: float, mode: str) -> Dict[str, Any]:
        """Tổng hợp và tính toán toàn bộ chỉ số thống kê phân phối độ trễ."""
        successful_reqs = [r for r in self.results if r["success"]]
        failed_reqs = [r for r in self.results if not r["success"]]

        latencies = [r["latency_ms"] for r in successful_reqs]
        latencies.sort()

        total = len(self.results)
        success_count = len(successful_reqs)
        fail_count = len(failed_reqs)
        success_rate = round((success_count / total) * 100, 2) if total > 0 else 0.0

        throughput = round(total / total_elapsed, 2) if total_elapsed > 0 else 0.0

        # Phân vị (Percentiles)
        def percentile(arr: List[float], p: float) -> float:
            if not arr:
                return 0.0
            k = (len(arr) - 1) * (p / 100.0)
            f = int(k)
            c = f + 1
            if c < len(arr):
                return round(arr[f] + (k - f) * (arr[c] - arr[f]), 2)
            return round(arr[f], 2)

        p50 = percentile(latencies, 50)
        p90 = percentile(latencies, 90)
        p95 = percentile(latencies, 95)
        p99 = percentile(latencies, 99)
        min_lat = round(min(latencies), 2) if latencies else 0.0
        max_lat = round(max(latencies), 2) if latencies else 0.0
        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        # Phân tích Cache
        cached_reqs = [r for r in successful_reqs if r.get("is_cached")]
        uncached_reqs = [r for r in successful_reqs if not r.get("is_cached")]
        cache_hit_rate = round((len(cached_reqs) / success_count) * 100, 2) if success_count > 0 else 0.0
        avg_cached_lat = round(sum(r["latency_ms"] for r in cached_reqs) / len(cached_reqs), 2) if cached_reqs else 0.0
        avg_uncached_lat = round(sum(r["latency_ms"] for r in uncached_reqs) / len(uncached_reqs), 2) if uncached_reqs else 0.0

        report = {
            "metadata": {
                "framework": "Async Concurrency Stress Engine",
                "target_endpoint": self.endpoint,
                "execution_mode": mode,
                "concurrency": self.concurrency,
                "total_requests": total,
                "duration_seconds": round(total_elapsed, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "summary_metrics": {
                "success_rate_percentage": f"{success_rate}%",
                "successful_requests": success_count,
                "failed_requests": fail_count,
                "throughput_rps": throughput,
                "latency_min_ms": min_lat,
                "latency_avg_ms": avg_lat,
                "latency_median_p50_ms": p50,
                "latency_p90_ms": p90,
                "latency_p95_ms": p95,
                "latency_p99_ms": p99,
                "latency_max_ms": max_lat
            },
            "cache_performance": {
                "cache_hit_rate_percentage": f"{cache_hit_rate}%",
                "cached_requests": len(cached_reqs),
                "uncached_requests": len(uncached_reqs),
                "avg_cached_latency_ms": avg_cached_lat,
                "avg_uncached_latency_ms": avg_uncached_lat,
                "speedup_factor": round(avg_uncached_lat / max(avg_cached_lat, 0.01), 1) if avg_cached_lat > 0 else "N/A"
            },
            "raw_samples": self.results[:20]
        }

        return report

    def export_report(self, report: Dict[str, Any], output_path: str = "evaluation/stress_test_report.json") -> str:
        """Lưu báo cáo kiểm thử tải ra tệp JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[STRESS TEST] Đã lưu báo cáo kiểm thử tải vào: {output_path}")
        return output_path


def run_stress_test(
    concurrency: int = 15,
    requests: int = 50,
    force_inmemory: bool = False
) -> Dict[str, Any]:
    """Hàm interface thực thi stress test từ các module khác."""
    tester = StressTester(concurrency=concurrency, total_requests=requests)
    report = asyncio.run(tester.run(force_inmemory=force_inmemory))
    tester.export_report(report)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chạy kiểm thử tải đồng thời cho API Chatbot Luật Giao thông")
    parser.add_argument("--concurrency", type=int, default=15, help="Số lượng người dùng đồng thời (mặc định: 15)")
    parser.add_argument("--requests", type=int, default=45, help="Tổng số request (mặc định: 45)")
    parser.add_argument("--inmemory", action="store_true", help="Bắt buộc chạy in-memory ASGI Transport")
    args = parser.parse_args()

    print("=" * 70)
    print("KHỞI CHẠY KIỂM THỬ TẢI ĐỒNG THỜI (PHÂN HỆ 4 - STRESS TEST ENGINE)")
    print("=" * 70)

    tester = StressTester(concurrency=args.concurrency, total_requests=args.requests)
    report = asyncio.run(tester.run(force_inmemory=args.inmemory))
    tester.export_report(report)

    summary = report["summary_metrics"]
    cache = report["cache_performance"]

    print("\n" + "=" * 70)
    print("KẾT QUẢ KIỂM THỬ HIỆU NĂNG & ĐỘ CHỊU TẢI:")
    print(f"- Số người dùng đồng thời: {report['metadata']['concurrency']}")
    print(f"- Tổng số requests:        {report['metadata']['total_requests']}")
    print(f"- Tỷ lệ thành công:        {summary['success_rate_percentage']} ({summary['successful_requests']}/{report['metadata']['total_requests']})")
    print(f"- Thông lượng (RPS):       {summary['throughput_rps']} req/s")
    print(f"- Độ trễ Min:              {summary['latency_min_ms']} ms")
    print(f"- Độ trễ Trung bình:       {summary['latency_avg_ms']} ms")
    print(f"- Độ trễ Trung vị (P50):   {summary['latency_median_p50_ms']} ms")
    print(f"- Độ trễ P90:              {summary['latency_p90_ms']} ms")
    print(f"- Độ trễ P95:              {summary['latency_p95_ms']} ms")
    print(f"- Độ trễ P99:              {summary['latency_p99_ms']} ms")
    print(f"- Độ trễ Max:              {summary['latency_max_ms']} ms")
    print("-" * 70)
    print(f"- Tỷ lệ trúng Cache:       {cache['cache_hit_rate_percentage']}")
    print(f"- Độ trễ Cache Hit TB:     {cache['avg_cached_latency_ms']} ms")
    print(f"- Độ trễ Cache Miss TB:    {cache['avg_uncached_latency_ms']} ms")
    print(f"- Tốc độ tăng tốc Cache:   {cache['speedup_factor']}x")
    print("=" * 70)
