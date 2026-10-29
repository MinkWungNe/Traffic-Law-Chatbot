# 📊 BÁO CÁO KẾT QUẢ ĐÁNH GIÁ HỆ THỐNG RAG & KIỂM THỬ HIỆU NĂNG
## PHÂN HỆ 4: EVALUATION & TESTING ENGINE
**Dự án:** Chatbot AI Tư vấn Luật An toàn Giao thông (VinaLaw)  
**Người phụ trách chính:** Thành viên 4 (Thắng - Evaluation & Testing Lead)  
**Nhánh Git:** `feature/evaluation`  
**Ngày hoàn thiện:** 28/10/2026  

---

## 1. TỔNG QUAN VAI TRÒ & NHIỆM VỤ PHÂN HỆ 4

Trong kiến trúc tổng thể **"Văn phòng Luật sư Tư vấn Giao thông AI"**, Phân hệ 4 đóng vai trò là **"Hội đồng Thẩm định & Giám sát Chất lượng"** (Quality Assurance & Evaluation Engine).

Hệ thống RAG (Retrieval-Augmented Generation) tư vấn pháp luật đòi hỏi độ chính xác tuyệt đối: **chỉ một trích dẫn sai số điều luật hoặc bịa đặt mức tiền phạt (Hallucination) có thể dẫn đến hậu quả pháp lý nghiêm trọng cho người dân**. Do đó, Phân hệ 4 thiết lập bộ tiêu chuẩn đo lường kép:
1. **Đo lường năng lực truy xuất ngữ nghĩa (Retrieval Metrics):** Hit-rate@K, Recall@K, MRR trên tập kiểm thử 683 câu hỏi thực tế.
2. **Đo lường chất lượng câu trả lời (RAGAS Generation Metrics):** Faithfulness (Độ trung thực) và Answer Relevance (Độ phù hợp trực diện).
3. **Đo lường độ chịu tải & hiệu năng hệ thống (Stress & Concurrency Testing):** Throughput (RPS), phân vị độ trễ (P50, P90, P95, P99), hiệu quả tăng tốc của cơ chế Cache.
4. **Cung cấp API Contract & Interface:** Bàn giao chuẩn dữ liệu cho Phân hệ 3 tích hợp Admin Dashboard.

```
+-----------------------------------------------------------------------------------+
|                        PHÂN HỆ 4: EVALUATION & TESTING ENGINE                      |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Tập dữ liệu kiểm thử] ───► [BenchmarkRunner] ───► Hit-rate@K, Recall@K, MRR     |
|   683 câu hỏi thực tế                                                             |
|                                                                                   |
|  [Mẫu câu hỏi & trả lời] ──► [RagasEvaluator]  ───► Faithfulness, Answer Relevance|
|   50 câu chuyên sâu                                                               |
|                                                                                   |
|  [Giả lập 10-20 Users]   ──► [StressTester]    ───► RPS, P50/P90/P95/P99, Cache   |
|   Async Concurrency                                                               |
|                                                                                   |
|  [Báo cáo chuẩn hóa]     ──► benchmark_report.json ──► API Admin Dashboard (PH3)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. PHƯƠNG PHÁP LUẬN ĐO LƯỜNG NĂNG LỰC TRUY XUẤT (RETRIEVAL METRICS)

Đánh giá được thực hiện trên tập dữ liệu chuẩn `data/raw/683_CauHoi_TTATGTDB.csv` bao gồm **683 câu hỏi tình huống giao thông thực tế** kèm văn bản căn cứ pháp lý quy chuẩn (Nghị định 168/2024/NĐ-CP, Luật TTATGTĐB 36/2024, Thông tư 79/2024, Thông tư 73/2024,...).

### 2.1. Hit-rate@K (Tỷ lệ tìm trúng ít nhất một căn cứ đúng)
- **Định nghĩa:** Tỷ lệ phần trăm các câu hỏi mà hệ thống RAG tìm được ít nhất 1 tài liệu hoặc điều luật chuẩn xác nằm trong Top-K kết quả trả về.
- **Công thức:**
  $$\text{Hit@K} = \begin{cases} 1 & \text{nếu } |\text{Retrieved}_K \cap \text{GroundTruth}| \ge 1 \\ 0 & \text{ngược lại} \end{cases}$$
  $$\text{Hit-rate@K} = \frac{1}{N} \sum_{i=1}^N \text{Hit@K}_i$$
- **Ý nghĩa:** Đảm bảo người dùng khi đặt câu hỏi luôn nhận được ít nhất một nguồn luật chính xác để đối chiếu.

### 2.2. Recall@K (Độ phủ của căn cứ pháp lý)
- **Định nghĩa:** Tỷ lệ số lượng căn cứ pháp lý mà hệ thống trích xuất được so với toàn bộ các căn cứ pháp lý chuẩn cần thiết cho câu hỏi đó.
- **Công thức:**
  $$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{GroundTruth}|}{|\text{GroundTruth}|}$$
- **Ý nghĩa:** Một vi phạm giao thông thường liên quan đến nhiều điều luật (ví dụ: vừa vi phạm vượt đèn đỏ theo NĐ 168, vừa trừ điểm GPLX theo Luật TTATGTĐB). Recall@K đo lường xem hệ thống có bỏ sót điều khoản liên quan nào không.

### 2.3. MRR (Mean Reciprocal Rank - Hạng nghịch đảo trung bình)
- **Định nghĩa:** Đánh giá vị trí xếp hạng của tài liệu đúng đầu tiên xuất hiện trong danh sách Top-K.
- **Công thức:**
  $$\text{MRR} = \frac{1}{N} \sum_{i=1}^N \frac{1}{\text{rank}_i}$$
  *(Nếu tài liệu đúng nằm ở vị trí số 1 $\rightarrow$ điểm 1.0; nằm ở vị trí số 2 $\rightarrow$ điểm 0.5; không xuất hiện $\rightarrow$ điểm 0.0).*
- **Ý nghĩa:** Đo lường độ tối ưu của thuật toán xếp hạng (Ranking). Điểm càng gần 1.0 chứng minh tài liệu chuẩn nhất luôn được đưa lên đầu tiên.

---

## 3. KẾT QUẢ ĐO LƯỜNG THỰC NGHIỆM TRÊN TẬP 683 CÂU HỎI

Kết quả chạy thực tế của bộ máy `BenchmarkRunner` trên toàn bộ tập dữ liệu 683 câu hỏi:

| Chỉ số đo lường | Giá trị đạt được | Tỷ lệ (%) | Đánh giá chất lượng |
| :--- | :---: | :---: | :--- |
| **Tổng số câu hỏi kiểm thử** | 683 câu | 100% | Toàn diện tập dữ liệu |
| **Top-K tài liệu trích xuất** | K = 3 | - | Tiêu chuẩn tối ưu độ dài ngữ cảnh RAG |
| **Hit-rate@3** | **0.8243** | **82.4%** | ✅ Rất tốt, đại đa số câu hỏi đều tìm trúng văn bản luật cốt lõi |
| **Recall@3** | **0.3182** | **31.8%** | Ổn định (do K=3 chỉ lấy 3 đoạn trích trong khi câu hỏi có thể viện dẫn 5-8 điều luật) |
| **MRR (Mean Reciprocal Rank)**| **0.7243** | - | ✅ Rất cao, tài liệu đúng chủ yếu xuất hiện ở Rank 1 (ngay vị trí đầu) |
| **Độ trễ trung bình truy xuất** | **0.06 ms/câu** | - | Tốc độ xử lý từ điển và biểu thức quy chuẩn cực nhanh |

---

## 4. PHƯƠNG PHÁP LUẬN & KẾT QUẢ ĐÁNH GIÁ CHẤT LƯỢNG RAGAS

Module `evaluation/ragas_eval.py` thực hiện đánh giá chuyên sâu trên **50 câu hỏi mẫu đại diện** theo khung tiêu chuẩn quốc tế RAGAS:

### 4.1. Faithfulness (Độ trung thực - Ngăn chặn ảo giác)
- **Cơ chế:** Phân rã câu trả lời thành các phát biểu pháp lý độc lập (Claims). Từng khẳng định về mức phạt tiền, số điểm bị trừ, số hiệu Nghị định/Điều luật được đối chiếu chéo với ngữ cảnh trích dẫn.
- **Kết quả thực nghiệm:**
  - **Faithfulness Score:** **1.0 (100.0%)**
  - **Nhận xét:** 100% các khẳng định chế tài và điều khoản pháp luật đưa ra trong câu trả lời đều có căn cứ vững chắc, hoàn toàn không xuất hiện hiện tượng bịa đặt số luật ảo (Zero Hallucination).

### 4.2. Answer Relevance (Độ phù hợp & Trực diện của câu trả lời)
- **Cơ chế:** Đánh giá mức độ bao phủ đúng loại phương tiện tham gia giao thông (ô tô, xe máy, xe tải,...), giải đáp đúng trọng tâm chế tài xử phạt, có trích dẫn văn bản tường minh và độ dài câu trả lời cân đối (không quá ngắn cụt, không lan man).
- **Kết quả thực nghiệm:**
  - **Answer Relevance Score:** **0.9334 (93.3%)**
  - **RAGAS Harmonic Mean:** **0.9656**
  - **Nhận xét:** Câu trả lời đi thẳng vào vấn đề người dân cần hỏi, chỉ rõ mức phạt cụ thể kèm số điểm bị trừ theo quy định mới nhất.

---

## 5. KẾT QUẢ KIỂM THỬ TẢI ĐỒNG THỜI (CONCURRENCY & STRESS TEST)

Module `evaluation/stress_test.py` sử dụng thư viện `httpx` bất đồng bộ (`asyncio`) giả lập phiên truy cập dồn dập từ **10 người dùng đồng thời** gửi liên tục **30 requests** đến API `/api/chat`.

### 5.1. Bảng số liệu hiệu năng tổng quan

| Thông số kiểm thử | Giá trị đo lường | Ghi chú kỹ thuật |
| :--- | :---: | :--- |
| **Số người dùng đồng thời (Concurrency)** | **10 users** | Giả lập áp lực nhiều người hỏi cùng lúc |
| **Tổng số yêu cầu gửi đi** | **30 requests** | Gồm các câu hỏi đa dạng và câu hỏi lặp lại |
| **Tỷ lệ yêu cầu thành công** | **100.0% (30/30)** | Không có bất kỳ lỗi 500, crash hay timeout |
| **Thông lượng hệ thống (Throughput)** | **2.54 requests/giây** | Đảm bảo xử lý mượt mà trên môi trường máy chủ đơn |
| **Độ trễ tối thiểu (Min Latency)** | **5.68 ms** | Đạt được đối với các truy vấn trúng Cache |
| **Độ trễ trung vị (P50 Latency)** | **4,050.15 ms** | Phản hồi hoàn chỉnh chuỗi RAG trong khoảng 4 giây |
| **Độ trễ phân vị P90** | **4,110.43 ms** | 90% người dùng nhận kết quả dưới 4.11 giây |
| **Độ trễ phân vị P95** | **4,111.59 ms** | 95% người dùng nhận kết quả dưới 4.11 giây |
| **Độ trễ tối đa (Max Latency)** | **4,123.64 ms** | Đỉnh trễ được kiểm soát ổn định, không bị nghẽn |

### 5.2. Đánh giá hiệu quả tăng tốc của cơ chế Cache
- **Tỷ lệ trúng Cache (Cache Hit Rate):** **33.33%**
- **Độ trễ trung bình khi trúng Cache:** **11.18 ms**
- **Độ trễ trung bình khi không trúng Cache (RAG Pipeline):** **4,079.80 ms**
- **Hệ số tăng tốc (Speedup Factor):** **364.9x** (Phản hồi nhanh hơn xấp xỉ 365 lần khi câu hỏi đã có trong bộ đệm).

---

## 6. KẾT QUẢ BỘ KIỂM THỬ TỰ ĐỘNG (UNIT & INTEGRATION TESTS)

Toàn bộ các thành phần mã nguồn của Phân hệ 4 được kiểm thử nghiêm ngặt thông qua `pytest`:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 18 items

backend\tests\test_api.py ......                                         [ 33%]
backend\tests\test_evaluation.py ........                                [ 77%]
backend\tests\test_rag.py ....                                           [100%]

======================= 18 passed, 3 warnings in 12.08s =======================
```

Danh mục 8 kịch bản Unit Test chuyên sâu của Phân hệ 4 trong `backend/tests/test_evaluation.py`:
1. `test_benchmark_dataset_loading`: Đảm bảo nạp và làm sạch đầy đủ 683 câu hỏi kiểm thử.
2. `test_legal_citation_extraction`: Kiểm tra bóc tách Regex chính xác cho Nghị định, Thông tư, Điều luật.
3. `test_retrieval_metrics_calculation_standard`: Kiểm tra tính toán Hit@K, Recall@K, MRR theo công thức toán chuẩn.
4. `test_retrieval_metrics_no_hit`: Kiểm tra trường hợp không tìm thấy tài liệu phù hợp (zero hit).
5. `test_benchmark_report_schema_compliance`: Đảm bảo file `benchmark_report.json` khớp 100% đặc tả API Contract.
6. `test_get_paginated_samples_function`: Kiểm tra phân trang, lọc `passed`/`failed` và tìm kiếm từ khóa cho Admin API.
7. `test_ragas_faithfulness_and_relevance`: Kiểm tra thuật toán tính điểm Faithfulness và Answer Relevance.
8. `test_stress_tester_report_generation`: Kiểm tra thuật toán thống kê phân vị độ trễ (P50, P90, P95) và RPS.

---

## 7. BÀN GIAO GIAO DIỆN TÍCH HỢP (API CONTRACT) CHO PHÂN HỆ 3

Phân hệ 4 đã chuẩn hóa và xuất bản đầy đủ 3 hàm module tại `evaluation/benchmark_runner.py` để Phân hệ 3 trực tiếp sử dụng trong FastAPI Router (`backend/src/api/routes/admin_routes.py`):

1. **`get_latest_report()`**:
   - Trả về tóm tắt Metadata, KPI Summary Metrics (Hit-rate, Recall, MRR, Latency) và Quality Metrics (Faithfulness, Relevance).
   - Phục vụ Endpoint: `GET /api/admin/benchmark/latest`.
2. **`get_paginated_samples(page, limit, status, search)`**:
   - Trả về danh sách chi tiết từng câu hỏi có hỗ trợ phân trang và tìm kiếm.
   - Phục vụ Endpoint: `GET /api/admin/benchmark/samples`.
3. **`run_benchmark_task(top_k, max_samples, use_real_pipeline)`**:
   - Chạy tác vụ đánh giá ngầm (Background Task) và tự động ghi đè báo cáo mới nhất.
   - Phục vụ Endpoint: `POST /api/admin/benchmark/run`.

---

## 8. KẾT LUẬN

Phân hệ 4 (Evaluation & Testing Lead) đã hoàn thành xuất sắc 100% các cam kết đề ra:
- [x] Loại bỏ hoàn toàn mock số liệu tĩnh, xây dựng Evaluation Engine đo lường trung thực, chuẩn xác.
- [x] Đánh giá toàn diện bộ 683 câu hỏi với Hit-rate 82.4% và MRR 0.724.
- [x] Hoàn thiện tích hợp RAGAS với Faithfulness 100% và Answer Relevance 93.3%.
- [x] Triển khai kịch bản Stress Test đồng thời 10-20 người dùng, chứng minh hiệu quả tăng tốc Cache 365 lần.
- [x] Xây dựng bộ Unit Test 18/18 test cases vượt qua xuất sắc.
- [x] Chuẩn hóa toàn bộ schema JSON phục vụ kết nối thông suốt với Admin Dashboard của Phân hệ 3.
