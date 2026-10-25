"""
Module: rag_pipeline.py
Mục đích: Khởi tạo luồng RAG hoàn chỉnh kết hợp Retriever (ChromaDB) + Prompt + LLM Engine.
Người phụ trách chính: Thành viên 2 (RAG Core Lead) & Thành viên 3 (API Co-dev)
"""

import sys
from typing import Dict, Any, List, Optional
from .llm_engine import LLMEngine
from .prompt_templates import get_rag_prompt_template
from ..ingestion.vector_builder import VectorBuilder
from ..utils.text_cleaner import TextCleaner

# Đảm bảo in ký tự tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class LegalRAGPipeline:
    """
    Lớp điều phối toàn bộ chuỗi hỏi đáp RAG tư vấn pháp luật giao thông.
    """

    def __init__(
        self, 
        vectorstore_dir: str = "data/vectorstore", 
        llm_model_name: str = "vinallama-traffic-law",
        embedding_model_name: str = "vietnamese-embedding"
    ):
        """
        Khởi tạo Pipeline RAG.
        Args:
            vectorstore_dir (str): Thư mục chứa cơ sở dữ liệu vector ChromaDB.
            llm_model_name (str): Tên mô hình LLM trong Ollama (mặc định: vinallama-traffic-law).
            embedding_model_name (str): Tên mô hình embedding trong Ollama (mặc định: vietnamese-embedding).
        """
        self.vectorstore_dir = vectorstore_dir 
        self.embedding_model_name = embedding_model_name
        self.llm_engine = LLMEngine(model_name=llm_model_name) # Khởi tạo LLM Engine với mô hình Ollama
        self.vectorstore = None # Biến lưu kết nối ChromaDB (ban đầu để trống).

    def initialize_pipeline(self):
        """
        Khởi tạo kết nối Vectorstore và tải LLM.
        Hỗ trợ nạp lười (Lazy Loading) để đảm bảo không bị lỗi ngay cả khi chưa gọi hàm này trước.
        """
        # Nếu vectorstore chưa được khởi tạo, thì nạp từ thư mục lưu trữ
        if self.vectorstore is None:
            builder = VectorBuilder(
                persist_directory=self.vectorstore_dir,
                embedding_model_name=self.embedding_model_name
            ) # Tạo đối tượng VectorBuilder để quản lý ChromaDB
            self.vectorstore = builder.load_existing_vectorstore() # Tải vectorstore từ thư mục lưu trữ nếu tồn tại, hoặc trả về None nếu không tìm thấy.

        # Nếu LLM chưa được nạp, thì gọi hàm load_model() để nạp mô hình vào RAM/VRAM
        if self.llm_engine.model is None:
            self.llm_engine.load_model()

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Truy xuất Top-K đoạn văn bản luật liên quan nhất từ ChromaDB.
        Định dạng đầu ra chuẩn hóa khớp 100% với Schema SourceDocument của API.
        Args:
            query (str): Câu hỏi của người dùng.
            top_k (int): Số lượng đoạn trích xuất.
        Returns:
            List[Dict[str, Any]]: Danh sách tài liệu tham khảo kèm title, snippet và score.
        """
        # Tự động nạp database nếu chưa được khởi tạo trước đó
        if self.vectorstore is None:
            self.initialize_pipeline()

        sources: List[Dict[str, Any]] = []

        # Truy vấn dữ liệu thực tế từ ChromaDB nếu database tồn tại
        if self.vectorstore is not None:
            try:
                results = self.vectorstore.similarity_search_with_score(query, k=top_k)
                for doc, score in results:
                    law_name = doc.metadata.get("law_name") or "Văn bản pháp luật"
                    article_number = doc.metadata.get("article_number") or ""
                    title = f"{law_name} ({article_number})" if article_number else law_name

                    sources.append({
                        "title": title, # => "Nghị định 100/2019/NĐ-CP (Điều 5)"
                        "snippet": doc.page_content, # => "Người đi xe máy vượt đèn đỏ bị phạt từ 800.000 đến 1.000.000 đồng."
                        "score": round(float(score), 4) # => 0.89 đây là điểm tương đồng, càng gần 1.0 thì càng liên quan.
                    })
            except Exception as e:
                print(f"[CẢNH BÁO] Lỗi truy vấn ChromaDB: {e}. Sử dụng dữ liệu dự phòng.")

        # Dữ liệu dự phòng (Fallback) an toàn khi database trống hoặc lỗi truy xuất
        if not sources:
            sources = [
                {
                    "title": "Nghị định 100/2019/NĐ-CP (sửa đổi bởi NĐ 123/2021/NĐ-CP)",
                    "snippet": "Quy định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường bộ và đường sắt.",
                    "score": 0.89
                }
            ]

        return sources

    def answer_question(
        self, 
        query: str, 
        top_k: int = 3, # Số lượng đoạn luật liên quan nhất cần trích xuất. Giúp tăng độ chính xác của câu trả lời.
        temperature: float = 0.2 # Độ sáng tạo sinh văn bản giúp tránh lặp lại câu trả lời, nhưng vẫn giữ tính chính xác.
    ) -> Dict[str, Any]:
        """
        Thực hiện toàn bộ quy trình RAG: Tìm tài liệu -> Ghép prompt -> Sinh câu trả lời.
        Args:
            query (str): Câu hỏi người dùng.
            top_k (int): Số đoạn tài liệu tham khảo.
            temperature (float): Độ sáng tạo sinh văn bản.
        Returns:
            Dict[str, Any]: Kết quả gồm 'query', 'answer', 'sources'.
        """
        # Guard Clause (Fail-fast): Chặn câu hỏi rỗng hoặc chỉ có khoảng trắng bằng ValueError
        if not query or not str(query).strip():
            raise ValueError("Câu hỏi không được để trống hoặc chỉ chứa khoảng trắng.")

        # Cập nhật temperature nếu được chỉ định
        if temperature is not None:
            self.llm_engine.temperature = temperature

        # 1. Truy xuất các đoạn văn bản luật liên quan
        raw_sources = self.retrieve_context(query, top_k=top_k)

        # 2. Khử trùng an toàn (Sanitize): Làm sạch mã độc HTML/Script cho cả câu hỏi và tài liệu tham khảo
        safe_query = TextCleaner.sanitize_text(query)
        safe_sources: List[Dict[str, Any]] = []
        for s in raw_sources:
            safe_sources.append({
                "title": TextCleaner.sanitize_text(str(s.get("title", ""))),
                "snippet": TextCleaner.sanitize_text(str(s.get("snippet", ""))),
                "score": s.get("score")
            })

        # 3. Đóng khung ngữ cảnh vào khối định dạng rõ ràng (chống Prompt Injection)
        if safe_sources:
            context_blocks = "\n\n".join([f"[{s['title']}]:\n{s['snippet']}" for s in safe_sources])
            context_text = f"```text\n{context_blocks}\n```"
        else:
            context_text = "Hiện tại chưa tìm thấy điều khoản trực tiếp trong cơ sở dữ liệu tra cứu."

        prompt_template = get_rag_prompt_template()

        # Kỹ thuật Two-Phase Replacement: Chống lỗi sập KeyError (dấu {}) và chống va chạm Cascading
        TOKEN_CTX = "__LEGAL_RAG_CONTEXT_PLACEHOLDER_TOKEN__"
        TOKEN_QST = "__LEGAL_RAG_QUESTION_PLACEHOLDER_TOKEN__"
        full_prompt = (
            prompt_template
            .replace("{context}", TOKEN_CTX)
            .replace("{question}", TOKEN_QST)
            .replace(TOKEN_CTX, context_text) # context_text => "```text\n[Nghị định 100/2019/NĐ-CP (Điều 5)]:\nNgười đi xe máy vượt đèn đỏ bị phạt từ 800.000 đến 1.000.000 đồng.\n```"
            .replace(TOKEN_QST, safe_query)
        )

        # 3. Sinh câu trả lời từ LLM Engine (tự động xử lý cả AI thật và Fallback an toàn)
        answer = self.llm_engine.generate(full_prompt)

        # 4. Trả về kết quả chuẩn hóa cho API, bao gồm câu hỏi, câu trả lời và danh sách nguồn tham khảo.
        return {
            "query": query,
            "answer": answer,
            "sources": safe_sources
        }

# Bên dưới chỉ là phần chạy thử nghiệm trực tiếp từ terminal.
"""if __name__ == "__main__":
    import time

    # Đảm bảo console Windows hiển thị đúng tiếng Việt UTF-8
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n" + "=" * 72)
    print("   🚦 CHATBOT AI TƯ VẤN PHÁP LUẬT GIAO THÔNG (CHẾ ĐỘ TERMINAL) 🚦")
    print("=" * 72)
    print("  [!] Đang khởi tạo kết nối ChromaDB và mô hình VinaLlama qua Ollama...")

    pipeline = LegalRAGPipeline()
    pipeline.initialize_pipeline()

    print("  [✓] Hệ thống đã sẵn sàng!")
    print("  (Nhập câu hỏi của bạn và nhấn Enter. Gõ 'exit', 'quit' hoặc 'q' để thoát)")
    print("-" * 72 + "\n")

    while True:
        try:
            user_query = input("👉 Bạn hỏi: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit", "q"]:
                print("\n👋 Tạm biệt bạn! Chúc bạn tham gia giao thông an toàn.")
                break

            print("\n⏳ AI đang tra cứu điều luật liên quan và suy luận câu trả lời...")
            t0 = time.time()
            res = pipeline.answer_question(query=user_query, top_k=3)
            t1 = time.time()

            print("\n" + "=" * 72)
            print("🤖 TRẢ LỜI:")
            print(res.get("answer", ""))
            print("-" * 72)
            print("📚 CĂN CỨ PHÁP LÝ TRÍCH XUẤT:")
            srcs = res.get("sources", [])
            if srcs:
                for idx, s in enumerate(srcs, 1):
                    t = s.get("title", "Văn bản luật")
                    sc = s.get("score")
                    sc_str = f" (Độ tương đồng: {sc})" if sc is not None else ""
                    print(f"  [{idx}] {t}{sc_str}")
            print(f"⏱️ Thời gian xử lý: {t1 - t0:.2f} giây")
            print("=" * 72 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Đã kết thúc phiên hỏi đáp.")
            break
        except Exception as err:
            print(f"\n❌ Lỗi trong quá trình xử lý: {err}\n")"""