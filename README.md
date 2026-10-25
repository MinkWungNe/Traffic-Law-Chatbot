# 🚗 CHATBOT AI TƯ VẤN LUẬT AN TOÀN GIAO THÔNG
> **Tài liệu hướng dẫn kiến trúc & quy chuẩn làm việc nhóm theo mô hình "Bộ khung chuẩn (Skeleton Architecture)"**  
> Dự án áp dụng phương pháp thiết kế giao diện trước (Interface-First / Contract-Driven), giúp mọi thành viên đều nắm trọn vẹn bức tranh tổng thể, tự tin code và phát triển tính năng nâng cao mà không lo xung đột mã nguồn.

---

## 🏢 HÌNH TƯỢNG HÓA KIẾN TRÚC: MÔ HÌNH "VĂN PHÒNG LUẬT SƯ"

Toàn bộ hệ thống được mô phỏng như một **Văn phòng Luật sư Tư vấn Giao thông tự động**:

```
[ Người dùng đặt câu hỏi trên Web ]
            │
            ▼
[ BÀN LỄ TÂN (frontend/ - Next.js & Tailwind CSS) ] ────► Tiếp nhận câu hỏi, điều hướng, hiển thị câu trả lời & căn cứ pháp lý
            │
            ▼ (Gửi yêu cầu HTTP REST API: /api/chat)
[ PHÒNG TIẾP NHẬN (backend/src/api/) ]          ────► Kiểm tra tính hợp lệ dữ liệu (chat_schema.py)
            │
            ▼
[ PHÒNG NGHIÊN CỨU ÁN (backend/src/rag/) ]
    ├── Kính quét ngữ nghĩa (Embedding Model qua vector_builder.py)
    ├── Tra cứu TỦ HỒ SƠ ĐIỆN TỬ (ChromaDB Vectorstore)
    └── LUẬT SƯ TRƯỞNG (vinallama-7b-chat qua llm_engine.py) tổng hợp câu trả lời chuẩn luật
```

---

## 🌳 SƠ ĐỒ CÂY THƯ MỤC CHI TIẾT & DANH MỤC FILE BỘ KHUNG (SKELETON)

Mọi file mã nguồn trong dự án đã được định nghĩa sẵn tên file, lớp (`class`), hàm (`def`), tham số đầu vào và kiểu dữ liệu trả về:

```text
Chatbot_AI_AnToanGiaoThong/
│
├── assets/                          <-- Kho tài nguyên truyền thông (Logo, sơ đồ kiến trúc, banner)
├── models/                          <-- Lưu trữ mô hình AI offline (.gguf)
│   └── Tai_models.md                <-- Hướng dẫn tải VinaLlama & Embedding model
│
├── data/                            <-- Kho dữ liệu tri thức của hệ thống
│   ├── raw/                         <-- Dữ liệu luật gốc (23 văn bản Luật/NĐ/TT mới nhất + 734_CauHoi_TTATGTDB.csv)
│   ├── processed/                   <-- Dữ liệu văn bản sau khi làm sạch
│   └── vectorstore/                 <-- Cơ sở dữ liệu vector ChromaDB
│
├── docs/                            <-- Báo cáo đề tài, biên bản họp nhóm
├── evaluation/                      <-- ĐÁNH GIÁ & KIỂM THỬ MÔ HÌNH (Benchmark)
│   └── benchmark_runner.py          <-- Class BenchmarkRunner: đo lường tự động tập 734 câu hỏi
│
├── requirements.txt                 <-- Toàn bộ thư viện Python cần cài đặt cho toàn dự án
├── backend/                         <-- KHỐI XỬ LÝ TRUNG TÂM (AI RAG & API)
│   ├── tests/
│   │   └── test_rag.py              <-- Kịch bản Unit Test kiểm tra luồng RAG
│   └── src/
│       ├── ingestion/               <-- PHÂN HỆ NẠP DỮ LIỆU
│       │   ├── document_loader.py   <-- Class DocumentLoader: đọc file Word (.docx), PDF
│       │   ├── text_splitter.py     <-- Class LegalTextSplitter: cắt văn bản theo Điều/Khoản
│       │   └── vector_builder.py    <-- Class VectorBuilder: nhúng vector và lưu vào ChromaDB
│       │
│       ├── rag/                     <-- PHÂN HỆ AI CỐT LÕI (RAG CORE)
│       │   ├── prompt_templates.py  <-- Mẫu Prompt chuẩn ép cấu trúc trích dẫn luật
│       │   ├── llm_engine.py        <-- Class LLMEngine: nạp và thực thi mô hình VinaLlama
│       │   └── rag_pipeline.py      <-- Class LegalRAGPipeline: điều phối truy xuất và sinh câu trả lời
│       │
│       ├── api/                     <-- PHÂN HỆ DỊCH VỤ MẠNG (FastAPI)
│       │   ├── main.py              <-- Điểm khởi chạy FastAPI, cấu hình CORS
│       │   ├── schemas/
│       │   │   └── chat_schema.py   <-- Pydantic models: ChatRequest, ChatResponse, SourceDocument
│       │   └── routes/
│       │       └── chat_routes.py   <-- Endpoints: POST /api/chat, GET /api/health
│       │
│       └── utils/                   <-- CÔNG CỤ TIỆN ÍCH DÙNG CHUNG
│           └── text_cleaner.py      <-- Class TextCleaner: làm sạch tiếng Việt, bóc tách số hiệu luật
│
└── frontend/                        <-- GIAO DIỆN WEB NGƯỜI DÙNG HIỆN ĐẠI (Next.js, TypeScript, Tailwind CSS)
    ├── public/                      <-- Tài nguyên tĩnh (Logo, favicon, icons)
    ├── src/
    │   ├── app/                     <-- Next.js App Router (layout.tsx, page.tsx, globals.css)
    │   ├── components/              <-- Các UI Component chính
    │   │   ├── chat/                <-- ChatDock, MessageBubble, ChatScrollArea, StarterCards
    │   │   ├── layout/              <-- Sidebar điều hướng & trạng thái kết nối Backend
    │   │   ├── views/               <-- Màn hình chức năng: LegalDocsView, FAQView, LoginView
    │   │   └── ambient/             <-- Hiệu ứng trống đồng Đông Sơn nền chuyển động
    │   ├── lib/
    │   │   └── api.ts               <-- API Client gọi FastAPI (/api/chat, /api/health) kèm timeout 60s
    │   ├── stores/
    │   │   └── useChatStore.ts      <-- Quản lý State toàn cục qua Zustand (tin nhắn, kết nối API)
    │   ├── types/
    │   │   └── chat.ts              <-- Định nghĩa kiểu dữ liệu (ChatMessage, Citation)
    │   └── hooks/                   <-- Custom Hooks điều phối Spotlight Border
    ├── package.json                 <-- Quản lý dependencies Node.js (React 19, Next.js, Zustand)
    └── .env.local                   <-- Cấu hình URL máy chủ Backend (http://127.0.0.1:8000)
```

---

## 🎯 BỘ QUY TẮC LÀM VIỆC NHÓM THEO BỘ KHUNG (SKELETON WORKFLOW)

### 1. Triết lý làm việc: "Hiểu cả bức tranh - Làm chắc bộ khung - Đột phá tính năng"
- **Không ai phải tự mò mẫm tạo file từ đầu:** Bộ khung đã dựng sẵn toàn bộ các tệp `.py`. Ở đầu mỗi file đều có khối chú thích (`docstring`) ghi rõ mục đích, người phụ trách, các hàm cần cài đặt, kiểu tham số đầu vào (`Args`) và kết quả trả về (`Returns`).
- **Khung cơ bản (Base Features) - Ai cũng phải nắm:**
  Mỗi thành viên khi nhận module chỉ việc "điền vào chỗ trống" (`fill-in-the-blank`) bên trong các phương thức của bộ khung. Vì các phương thức đã được quy chuẩn sẵn, nên khi ghép nối giữa Ingestion $\rightarrow$ ChromaDB $\rightarrow$ RAG $\rightarrow$ FastAPI $\rightarrow$ Streamlit sẽ khớp hoàn toàn 100%.
- **Tính năng nâng cao (Advanced Features) - Đất diễn cho sự sáng tạo:**
  Sau khi hoàn thành khung cơ bản, mỗi thành viên được khuyến khích nghiên cứu và bổ sung các kỹ thuật nâng cao vào module của mình (ví dụ: Re-ranking, HyDE, Multi-turn Conversation Memory, Cache truy vấn Redis/SQLite, Báo cáo biểu đồ nâng cao...).

---

### 2. Bảng phân công trách nhiệm: Mô hình "Mỗi người sở hữu 1 Phân hệ độc lập" (Single Ownership)

Để tránh tình trạng chồng chéo, đùn đẩy hoặc ỷ lại trách nhiệm, dự án chia thành **4 phân hệ độc lập tương ứng với 4 thành viên**. Mỗi người toàn quyền quyết định và chịu trách nhiệm 100% về chất lượng code của phân hệ mình:

| Phân hệ & Thành viên | Phạm vi thư mục độc lập | Nhiệm vụ Khung cơ bản (Bắt buộc) | Hướng phát triển Nâng cao (Tự chọn & Báo cáo) |
| :--- | :--- | :--- | :--- |
| **Phân hệ 1: Data Ingestion**<br>👤 *Vinh* `feature/data-ingestion` | `src/ingestion/`<br>`src/utils/`<br>`data/` | - Đọc trích xuất file Word/PDF trong `document_loader.py`.<br>- Tách văn bản chuẩn theo Điều/Khoản trong `text_splitter.py`.<br>- Làm sạch chuỗi và bóc tách số hiệu luật trong `text_cleaner.py`. | - Tự động bóc tách metadata (Chương, Mục, Thẩm quyền xử phạt).<br>- Nhận diện cấu trúc bảng biểu mức phạt tiền.<br>- Phát hiện cảnh báo điều khoản hết hiệu lực. |
| **Phân hệ 2: RAG Core & Vector DB**<br>👤 *Chí* `feature/rag-core` | `src/rag/`<br>`models/`<br>`src/ingestion/vector_builder.py` | - Nhúng vector và lưu trữ ChromaDB trong `vector_builder.py`.<br>- Nạp và cấu hình VinaLlama cục bộ trong `llm_engine.py`.<br>- Ghép Prompt và sinh phản hồi chuẩn luật trong `rag_pipeline.py`. | - Tích hợp Re-ranking (Cross-Encoder / BGE-Reranker).<br>- Áp dụng kỹ thuật HyDE (Hypothetical Document Embeddings).<br>- Tối ưu hóa GPU Offloading (cuBLAS) tăng tốc độ sinh token. |
| **Phân hệ 3: API & Web Frontend**<br>👤 *Quân* `feature/api-ui` | `backend/src/api/`<br>`frontend/` | - Vận hành FastAPI REST Server trong `main.py` & `chat_routes.py`.<br>- Phát triển giao diện Web Next.js hiện đại trong `frontend/`.<br>- Kết nối API FastAPI với thanh Dock Chat, trích dẫn luật và tra cứu. | - Quản lý lịch sử hội thoại nhiều lượt (Multi-turn chat memory).<br>- Caching câu hỏi phổ biến để phản hồi dưới 0.1s.<br>- Tính năng xuất nội dung tư vấn ra tệp PDF/Word. |
| **Phân hệ 4: Evaluation & Testing**<br>👤 *Thắng* `feature/evaluation` | `evaluation/`<br>`backend/tests/`<br>`frontend/pages/`<br>`docs/` | - Đọc tập 734 câu hỏi kiểm thử trong `benchmark_runner.py`.<br>- Đo lường chỉ số Recall@K, Hit-rate trên tập câu hỏi.<br>- Xây dựng trang hiển thị báo cáo trong `pages/2_Danh_Gia.py`. | - Đánh giá chuyên sâu bằng RAGAS (Faithfulness, Relevance).<br>- Viết kịch bản kiểm thử tải đồng thời (Stress testing API).<br>- Xây dựng trang tra cứu nhanh luật trong `pages/1_Tra_Cuu_Luat.py`. |

---

### 3. Quy chế sinh hoạt nhóm & Cơ chế "Weekly Tech-Sharing" (Họp tuần cung cấp thông tin)

Dù mỗi người code một phần độc lập, nhưng **khi bảo vệ đồ án hoặc đi thi, bất kỳ ai cũng có thể bị giảng viên/giám khảo hỏi về code của các phần khác**. Do đó, buổi họp tuần là cầu nối bắt buộc để mọi người nắm trọn vẹn toàn bộ dự án:

1. **Thời gian họp:** Cố định 1 buổi/tuần (thời lượng 45 - 60 phút).
2. **Quy trình họp tuần (Bắt buộc từng thành viên):**
   - **Báo cáo tiến độ (5 phút/người):** Trình bày phần khung cơ bản đã hoàn thành đến đâu.
   - **Thuyết trình kỹ thuật & Code Walkthrough (10 phút/người):**
     - Mở trực tiếp mã nguồn phân hệ mình phụ trách lên màn hình.
     - **Giải thích luồng dữ liệu:** *"Đầu vào là gì? Hàm này xử lý ra sao? Đầu ra trả về định dạng thế nào?"*.
     - Giới thiệu các tính năng nâng cao mới nghiên cứu và đưa vào code.
     - Demo chạy thử trực tiếp tính năng đó.
   - **Hỏi đáp & Giải tỏa thắc mắc (5 phút/người):** Ba thành viên còn lại đặt câu hỏi để hiểu rõ cách phân hệ đó hoạt động.
3. **Quy tắc phối hợp Git tuần hoàn (Weekly Git Lifecycle):**
   - **Tên nhánh:** Đặt đúng tiền tố `feature/` kèm tên phân hệ (ví dụ: `feature/data-ingestion`, `feature/rag-core`, `feature/api-ui`, `feature/evaluation`). Tiền tố này giúp Git tự động gom nhóm nhánh gọn gàng.
   - **Quy trình chuẩn mỗi tuần:**
     1. **Trong tuần:** Mỗi người chỉ làm việc và commit trên nhánh `feature/...` của mình:
        ```bash
        git checkout feature/<ten-phan-he>
        git add .
        git commit -m "feat: mo ta cong viec da lam"
        git push origin feature/<ten-phan-he>
        ```
     2. **Trước buổi họp tuần:** Từng người tạo Pull Request (PR) để merge nhánh của mình vào nhánh `main`.
     3. **Sau buổi họp tuần:** Mọi người cập nhật bản `main` mới nhất về nhánh của mình để tiếp tục code tuần tiếp theo:
        ```bash
        git checkout main
        git pull origin main
        git checkout feature/<ten-phan-he>
        git merge main
        ```

4. **Xử lý khi cần dùng code của nhau & Giải quyết Xung đột (Conflict Resolution):**
   - **Tình huống 1: "Tôi cần gọi code của phân hệ khác để test thì sao?"**
     - *Giải pháp tối ưu:* **Dùng luôn hàm Mock có sẵn trong Bộ khung Skeleton**. Bộ khung đã định nghĩa sẵn các hàm trả về dữ liệu mẫu chuẩn (Dummy Data). Bạn hoàn toàn có thể test phân hệ của mình mà không cần đợi người khác code xong!
     - *Nếu thực sự cần test trực tiếp code mới nhất của bạn B:* Bạn có thể gõ `git checkout feature/<nhanh-cua-B>` để test thử, nhưng **tuyệt đối không chỉnh sửa code trong thư mục của B**.
   - **Tình huống 2: "Lỡ người A kéo code người B về, sửa file của B rồi merge vào main gây xung đột thì làm sao?"**
     - **Nguyên tắc cốt lõi (Rule of Ownership):** *Người A không bao giờ được tự ý sửa file thuộc phân hệ của người B*. Nếu thấy code người B có lỗi hoặc cần bổ sung tham số, A hãy nhắn trực tiếp để B tự sửa trên nhánh của B.
     - **Nếu xung đột (Merge Conflict) vẫn xảy ra:**
       1. Git sẽ đánh dấu vùng xung đột trong file:
          ```text
          <<<<<<< HEAD (Code hiện tại trên main)
          # Code do người A hoặc B đã merge trước đó
          =======
          # Code do người merge sau mang lên
          >>>>>>> feature/...
          ```
       2. **Không được tự ý giải quyết một mình:** Cả A và B phải ngồi lại với nhau (hoặc gọi Discord/Meet chia sẻ màn hình).
       3. Mở file xung đột trên VS Code (VS Code sẽ hiển thị sẵn các nút bấm trực quan: `Accept Current Change`, `Accept Incoming Change`, `Accept Both`).
       4. B (với tư cách là Owner của file đó) sẽ là người quyết định dòng code nào là đúng và mới nhất để giữ lại.
       5. Xóa các ký hiệu xung đột, lưu file và thực hiện commit giải quyết xung đột:
          ```bash
          git add <file-xung-dot>
          git commit -m "fix: resolve merge conflict between branch A and B"
          git push
          ```

---

### 4. Quy chuẩn định danh mã nguồn (Coding Conventions - PEP 8)

Dự án tuân thủ nghiêm ngặt chuẩn **PEP 8**:
- **Tên tệp (`.py`):** Viết thường nối nhau bằng dấu gạch dưới (`snake_case`), ví dụ: `text_splitter.py`, `chat_routes.py`.
- **Tên lớp (`class`):** Viết hoa chữ cái đầu mỗi từ (`PascalCase`), ví dụ: `DocumentLoader`, `LegalRAGPipeline`.
- **Tên hàm/phương thức (`def`):** Bắt đầu bằng động từ, viết thường (`snake_case`), ví dụ: `load_docx()`, `answer_question()`.
- **Chú thích tài liệu (`Docstrings`):** Tất cả các hàm và lớp mới viết thêm đều phải có mô tả tóm tắt, liệt kê `Args:` và `Returns:`.

---

### 5. Quy chuẩn thông điệp Commit (Conventional Commits)

Để lịch sử dự án trên Git chuyên nghiệp như tại các công ty công nghệ lớn, dự án áp dụng chuẩn **Conventional Commits**:

#### 📌 Cấu trúc chuẩn của một Commit Message:
```text
<type>(<scope>): <mô tả ngắn gọn công việc vừa làm>
```

* **`type` (Loại thay đổi - Bắt buộc):**
  * `feat`: Thêm tính năng mới (*Feature*)
  * `fix`: Sửa lỗi (*Bug Fix*)
  * `docs`: Thêm hoặc chỉnh sửa tài liệu, README, docstrings
  * `refactor`: Tái cấu trúc mã nguồn (sắp xếp lại code mà không thay đổi tính năng)
  * `perf`: Tối ưu hóa hiệu năng (tăng tốc độ phản hồi, giảm tiêu thụ RAM/GPU)
  * `test`: Thêm hoặc cập nhật kịch bản kiểm thử, benchmark
  * `chore`: Cập nhật cấu hình, file phụ trợ (`requirements.txt`, `.gitignore`)

* **`scope` (Phân hệ bị ảnh hưởng - Khuyên dùng):**
  * `ingestion`: Phân hệ nạp và xử lý văn bản luật
  * `rag`: Phân hệ AI suy luận, VinaLlama, Prompt
  * `api`: Phân hệ FastAPI routes/schemas
  * `ui`: Giao diện Web Streamlit
  * `eval`: Phân hệ kiểm thử benchmark 734 câu
  * `utils`: Các hàm tiện ích xử lý chuỗi

#### 💡 Ví dụ thực tế áp dụng trong dự án:

| Commit chuẩn chuyên nghiệp | Giải thích ý nghĩa |
| :--- | :--- |
| `feat(ingestion): them regex tach van ban theo dieu khoan` | Thêm tính năng tách điều khoản trong `text_splitter.py` |
| `feat(rag): tich hop mo hinh vinallama offline qua llamacpp` | Nạp mô hình LLM vào `llm_engine.py` |
| `fix(api): xu ly loi timeout khi gui cau hoi dai` | Sửa lỗi endpoint `/api/chat` |
| `feat(ui): them hop trich dan nguon luat expander` | Bổ sung hiển thị căn cứ pháp lý trong `app.py` |
| `perf(rag): cache embeddings giup tang toc truy van len 2x` | Tối ưu hóa hiệu năng truy xuất |
| `test(eval): them kich ban tinh recall@3 tren 734 cau hoi` | Viết kịch bản đánh giá trong `benchmark_runner.py` |
| `chore(deps): bo sung thu vien python-docx vao requirements.txt` | Cập nhật file thư viện phụ thuộc |
| `docs(readme): cap nhat quy tac lam viec nhom va huong dan git` | Chỉnh sửa tài liệu dự án |

> [!WARNING] **CẤM TUYỆT ĐỐI các commit cẩu thả kiểu:**
> ❌ `git commit -m "update"`  
> ❌ `git commit -m "fix bug"`  
> ❌ `git commit -m "xong roi"`  
> ❌ `git commit -m "asdfgh"`  
> Những commit này khiến cả nhóm không thể theo dõi được bạn đã sửa những gì khi xảy ra lỗi.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY HỆ THỐNG

### 📋 Yêu cầu môi trường tiền đề (Prerequisites)
1. **Python:** Phiên bản 3.10 – 3.13 (64-bit).
2. **Node.js & npm:** Phiên bản Node.js LTS (khuyến nghị **>= 18.x** hoặc **>= 20.x**) để chạy giao diện Next.js.  
   *(Tải Node.js chính thức tại: [nodejs.org](https://nodejs.org/))*.

---

### 🌟 CÁCH 1: KHỞI CHẠY NHANH BẰNG SCRIPT ĐIỀU PHỐI (Khuyên dùng)

Dự án cung cấp script khởi chạy tự động [scripts/run.py](file:///d:/Traffic-Law-Chatbot/scripts/run.py) đa nền tảng (Windows/Linux/macOS), giải quyết triệt để lỗi xung đột tiến trình và tự động hóa toàn bộ việc thiết lập:

* **Tự động nhận diện môi trường ảo Python:** Tự tìm và kích hoạt `venv` hoặc `.venv`.
* **Tự động kiểm tra & cài đặt thư viện Frontend (`node_modules`):** Nếu bạn mới clone dự án về mà chưa chạy `npm install`, script sẽ **tự động phát hiện thư mục `node_modules` bị thiếu và tự chạy `npm install`** giúp bạn.

#### Các bước thực hiện:
1. Mở Terminal tại thư mục gốc dự án (`Traffic-Law-Chatbot`).
2. Chạy lệnh:
   ```bash
   python scripts/run.py
   ```
3. Menu tương tác sẽ hiển thị:
   ```text
   ================================================================================
             🚦 CHATBOT AI TƯ VẤN PHÁP LUẬT AN TOÀN GIAO THÔNG 🚦
   ================================================================================
     [!] Môi trường Python: [venv]
   ================================================================================

     [1] Khởi chạy TOÀN BỘ hệ thống (FastAPI Backend :8000 + Next.js UI :3000)
     [2] Chỉ chạy GIAO DIỆN WEB (Next.js Frontend trên port 3000)
     [3] Chỉ chạy MÁY CHỦ API (FastAPI Backend trên port 8000)
     [0] Thoát
   ================================================================================
   ```
4. **Nhập phím `1`** và bấm Enter:
   * Cửa sổ FastAPI Backend sẽ tự động bật trên cổng **`8000`** (Tài liệu API: `http://localhost:8000/docs`).
   * Giao diện Web Next.js sẽ tự động khởi động trên cổng **`3000`** (Truy cập: `http://localhost:3000`).

---

### 🛠️ CÁCH 2: CÀI ĐẶT & KHỞI CHẠY THỦ CÔNG TỪNG PHÂN HỆ

Dành cho nhà phát triển muốn debug riêng lẻ từng terminal:

#### Bước 1: Thiết lập môi trường Python & Cài đặt thư viện Backend
1. Tạo môi trường ảo tại thư mục gốc dự án:
   ```bash
   python -m venv venv
   ```
2. Kích hoạt môi trường ảo:
   * **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
3. Cài đặt thư viện Python:
   ```bash
   pip install -r requirements.txt
   ```

#### Bước 2: Cài đặt thư viện Frontend (Next.js)
Mở terminal và di chuyển vào thư mục `frontend`:
```bash
cd frontend
npm install
```
*(Cấu hình kết nối API mặc định đã được thiết lập sẵn trong file `.env.local` trỏ đến `http://127.0.0.1:8000`)*.

#### Bước 3: Chạy kiểm thử tự động bộ khung Backend
```bash
$env:PYTHONPATH="."
python backend/tests/test_rag.py
```

#### Bước 4: Khởi chạy máy chủ FastAPI Backend
```bash
uvicorn backend.src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
*Tài liệu Swagger API trực quan tại:* `http://localhost:8000/docs`

#### Bước 5: Khởi chạy giao diện Web Next.js Frontend
Mở một cửa sổ Terminal mới:
```bash
cd frontend
npm run dev
```
*Truy cập giao diện Web chính thức tại:* `http://localhost:3000`
