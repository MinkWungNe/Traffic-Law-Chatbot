# 📖 SỔ TAY HƯỚNG DẪN VẬN HÀNH BỘ MÁY ĐÁNH GIÁ (RUNBOOK PHÂN HỆ 4)
**Dự án:** Traffic-Law-Chatbot (Trợ lý AI Luật Giao thông VinaLaw)  
**Phân hệ:** Phân hệ 4 (Evaluation & Testing Lead)  
**Mục tiêu:** Hướng dẫn thành viên nhóm và Giảng viên chạy thực nghiệm các kịch bản kiểm thử, đánh giá chất lượng RAGAS và đo tải hệ thống.

---

## 1. CÀI ĐẶT MÔI TRƯỜNG THỰC THI

Bộ công cụ của Phân hệ 4 yêu cầu Python 3.10+ (đã kiểm thử và tương thích hoàn toàn trên Python 3.14).

Cài đặt các gói thư viện kiểm thử cần thiết:
```bash
pip install pytest httpx pandas pydantic fastapi uvicorn
```

---

## 2. KỊCH BẢN 1: CHẠY ĐÁNH GIÁ BENCHMARK TRÊN TẬP 683 CÂU HỎI

Tác vụ này sẽ nạp file dữ liệu gốc `data/raw/683_CauHoi_TTATGTDB.csv`, trích xuất căn cứ pháp lý, tính toán chỉ số Hit-rate@K, Recall@K, MRR và xuất báo cáo JSON.

### 2.1. Chạy đánh giá toàn bộ 683 câu hỏi (Full Evaluation)
```bash
python evaluation/benchmark_runner.py
```
*Kết quả sẽ hiển thị bảng chỉ số tổng quan trên Console và tự động ghi vào tệp `evaluation/benchmark_report.json`.*

### 2.2. Chạy đánh giá nhanh (Quick Evaluation) qua Python Console
```python
from evaluation.benchmark_runner import BenchmarkRunner

runner = BenchmarkRunner()
# Chạy thử nghiệm nhanh trên 50 câu hỏi đầu tiên với Top-K = 3
report = runner.evaluate_retrieval(top_k=3, max_samples=50)
print(report["summary_metrics"])
```

---

## 3. KỊCH BẢN 2: CHẠY ĐÁNH GIÁ CHẤT LƯỢNG RAGAS (FAITHFULNESS & RELEVANCE)

Bộ đánh giá `RagasEvaluator` đo lường mức độ trung thực (chống ảo giác số luật) và độ phù hợp câu trả lời trên tập 50 câu hỏi mẫu.

```bash
python evaluation/ragas_eval.py --samples 50
```
- **Tham số `--samples`:** Số lượng mẫu câu hỏi cần đánh giá (mặc định: 50).
- **Kết quả xuất bản:**
  - Tệp chi tiết: `evaluation/ragas_report.json`
  - Đồng thời tự động cập nhật trường `quality_metrics` trong `evaluation/benchmark_report.json`.

---

## 4. KỊCH BẢN 3: CHẠY KIỂM THỬ TẢI ĐỒNG THỜI (CONCURRENCY & STRESS TEST)

Bộ máy `StressTester` sử dụng `httpx` bất đồng bộ để đo lường thông lượng (RPS) và các phân vị độ trễ (P50, P90, P95, P99) dưới áp lực 10 - 20 người dùng truy vấn cùng lúc.

### 4.1. Lệnh thực thi cơ bản
```bash
python evaluation/stress_test.py --concurrency 15 --requests 45
```
- **`--concurrency`:** Số người dùng giả lập đồng thời (ví dụ: 10, 15, 20).
- **`--requests`:** Tổng số câu hỏi gửi đến API (ví dụ: 30, 45, 60).
- **`--inmemory`:** *(Tùy chọn)* Buộc chạy trực tiếp qua ASGI In-memory Transport nếu không muốn bật server HTTP ngoài.

### 4.2. Báo cáo sinh ra
Dữ liệu đo đạc chi tiết từng mili-giây được lưu tại:
`evaluation/stress_test_report.json`

---

## 5. KỊCH BẢN 4: CHẠY TOÀN BỘ UNIT TEST TỰ ĐỘNG (PYTEST)

Kiểm tra tính toàn vẹn của mã nguồn, thuật toán toán học và cấu trúc schema dữ liệu.

### 5.1. Chạy riêng bộ kiểm thử của Phân hệ 4
```bash
python -m pytest backend/tests/test_evaluation.py -v
```

### 5.2. Chạy toàn bộ test suite của toàn dự án
```bash
python -m pytest backend/tests/ -v
```
*Kỳ vọng: 18/18 bài kiểm thử đạt trạng thái **PASSED 100%**.*

---

## 6. KỊCH BẢN 5: TÍCH HỢP HÀM VÀO ADMIN API CHO PHÂN HỆ 3

Phân hệ 3 khi xây dựng các endpoint trong `backend/src/api/routes/admin_routes.py` chỉ cần import các hàm do Phân hệ 4 cung cấp:

```python
from evaluation.benchmark_runner import (
    get_latest_report,
    get_paginated_samples,
    run_benchmark_task
)

# 1. Endpoint lấy tóm tắt báo cáo
@router.get("/api/admin/benchmark/latest")
def api_get_latest_benchmark():
    return get_latest_report()

# 2. Endpoint lấy danh sách câu hỏi phân trang
@router.get("/api/admin/benchmark/samples")
def api_get_benchmark_samples(page: int = 1, limit: int = 20, status: str = "all", search: str = None):
    return get_paginated_samples(page=page, limit=limit, status=status, search=search)

# 3. Endpoint kích hoạt chạy đánh giá ngầm (Background Task)
@router.post("/api/admin/benchmark/run", status_code=202)
def api_run_benchmark(background_tasks: BackgroundTasks, top_k: int = 3, max_samples: int = 50):
    background_tasks.add_task(run_benchmark_task, top_k=top_k, max_samples=max_samples)
    return {"message": "Đã bắt đầu tác vụ đánh giá ngầm.", "status": "running"}
```

---

## 7. QUẢN LÝ TỆP DỮ LIỆU ĐẦU RA (ARTIFACTS DIRECTORY)

| Tệp báo cáo JSON | Mục đích sử dụng |
| :--- | :--- |
| `evaluation/benchmark_report.json` | Chứa số liệu Hit-rate, Recall, MRR, RAGAS Quality Metrics và toàn bộ chi tiết 683 câu hỏi phục vụ hiển thị Admin Dashboard. |
| `evaluation/ragas_report.json` | Chứa chi tiết điểm Faithfulness (đối soát Claims) và Answer Relevance của 50 câu hỏi mẫu. |
| `evaluation/stress_test_report.json` | Chứa số liệu hiệu năng chịu tải, RPS, P50, P90, P95, P99 và phân tích tỷ lệ tăng tốc của Cache. |
