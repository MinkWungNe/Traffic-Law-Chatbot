"""
Module: rag_pipeline.py
Mục đích: Khởi tạo luồng RAG hoàn chỉnh kết hợp QueryNormalizer + HybridRetriever + 2-Tier Gate + Prompt CoT + LLM Engine + Output Cleaner.
Nhóm phụ trách: Nhóm 3 - Relevance Threshold Gate & Pipeline Coordinator
"""

import sys
import logging
from typing import Dict, Any, List, Optional
from .llm_engine import LLMEngine
from .prompt_templates import get_rag_prompt_template
from .query_normalizer import QueryNormalizer
from .hybrid_retriever import HybridRetriever
from ..ingestion.vector_builder import VectorBuilder
from ..utils.text_cleaner import TextCleaner

# Đảm bảo in ký tự tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("rag.rag_pipeline")

class LegalRAGPipeline:
    """
    Lớp điều phối toàn bộ chuỗi hỏi đáp RAG tư vấn pháp luật giao thông chuyên nghiệp.
    """

    # Ngưỡng tương đồng chuẩn hóa an toàn để vượt qua Cổng kiểm soát (Threshold Gate)
    RELEVANCE_THRESHOLD = 0.45

    # Danh mục từ khóa nhận diện câu hỏi ngoài luồng (Domain Guardrail)
    OUT_OF_DOMAIN_KEYWORDS = [
        
    ]

    # Danh mục từ khóa nghiệp vụ giao thông để tránh chặn nhầm (Compound Logic)
    TRAFFIC_DOMAIN_KEYWORDS = [
        "xe", "giao thông", "đường", "phạt", "bằng lái", "gplx", "tốc độ",
        "nồng độ cồn", "rượu bia", "đèn đỏ", "đèn tín hiệu", "tai nạn",
        "csgt", "công an", "vi phạm", "làn đường", "vỉa hè", "mũ bảo hiểm",
        "ngược chiều", "dừng xe", "đỗ xe", "chở quá"
    ]

    def __init__(
        self, 
        vectorstore_dir: str = "data/vectorstore", 
        llm_model_name: str = "vinallama-traffic-law",
        embedding_model_name: str = "vietnamese-embedding",
        relevance_threshold: float = 0.45
    ):
        self.vectorstore_dir = vectorstore_dir 
        self.embedding_model_name = embedding_model_name
        self.relevance_threshold = relevance_threshold
        
        self.query_normalizer = QueryNormalizer()
        self.llm_engine = LLMEngine(model_name=llm_model_name)
        self.vectorstore = None
        self.hybrid_retriever: Optional[HybridRetriever] = None

    def initialize_pipeline(self):
        """
        Khởi tạo kết nối Vectorstore, nạp HybridRetriever và tải LLM.
        """
        if self.vectorstore is None:
            builder = VectorBuilder(
                persist_directory=self.vectorstore_dir,
                embedding_model_name=self.embedding_model_name
            )
            self.vectorstore = builder.load_existing_vectorstore()

        if self.hybrid_retriever is None:
            self.hybrid_retriever = HybridRetriever(vectorstore=self.vectorstore)

        if self.llm_engine.model is None:
            self.llm_engine.load_model()

    def retrieve_context(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Truy xuất Top-K đoạn văn bản luật liên quan nhất thông qua Hybrid Search.
        """
        if self.hybrid_retriever is None:
            self.initialize_pipeline()

        # 1. Phân tích tiền xử lý truy vấn & từ điển pháp lý (Nhóm 1)
        query_info = self.query_normalizer.normalize_and_expand(query)

        # 2. Truy xuất lai Dense + BM25 + Re-ranking (Nhóm 2)
        if self.hybrid_retriever is not None:
            sources = self.hybrid_retriever.retrieve(
                query_info=query_info,
                top_k=top_k
            )
            return sources

        return []

    def answer_question(
        self, 
        query: str, 
        top_k: int = 4,
        temperature: float = 0.15
    ) -> Dict[str, Any]:
        """
        Thực hiện toàn bộ quy trình RAG:
        1. Guard Clause: Chặn câu hỏi rỗng.
        2. Tầng 1: Domain Intent Guardrail (Chặn câu hỏi thời tiết, nấu ăn... < 5ms).
        3. Query Normalizer (Nhóm 1).
        4. Hybrid Retrieval (Nhóm 2).
        5. Tầng 2: Relevance Threshold Gate & Fast-Exit (Nhóm 3).
        6. Dynamic Chunk Pruning (Nhóm 3).
        7. Ghép Prompt CoT (Nhóm 4).
        8. Sinh câu trả lời qua LLM Engine (Nhóm 5).
        9. Hậu xử lý làm sạch văn bản (Post-processing cleaner).
        """
        # Guard Clause (Fail-fast): Chặn câu hỏi rỗng hoặc chỉ có khoảng trắng
        if not query or not str(query).strip():
            raise ValueError("Câu hỏi không được để trống hoặc chỉ chứa khoảng trắng.")

        lower_q = str(query).lower()

        # TẦNG 1: DOMAIN INTENT GUARDRAIL (Chặn câu hỏi ngoài luồng rõ rệt mà không phụ thuộc similarity)
        # Sử dụng Compound Logic: Chỉ chặn khi có từ ngoài luồng VÀ KHÔNG chứa từ khóa giao thông
        is_matched_ood = any(ood in lower_q for ood in self.OUT_OF_DOMAIN_KEYWORDS)
        is_traffic_related = any(kw in lower_q for kw in self.TRAFFIC_DOMAIN_KEYWORDS)

        if is_matched_ood and not is_traffic_related:
            return {
                "query": query,
                "answer": (
                    "Chào bạn, tôi là Trợ lý AI Tư vấn Pháp luật Trật tự, An toàn Giao thông Đường bộ. "
                    "Hệ thống nhận thấy câu hỏi của bạn không nằm trong phạm vi quy định pháp luật giao thông. "
                    "Vui lòng đặt câu hỏi liên quan đến quy tắc giao thông, mức xử phạt vi phạm hành chính "
                    "hoặc giấy phép lái xe để được hỗ trợ chính xác."
                ),
                "sources": []
            }

        if temperature is not None:
            self.llm_engine.temperature = temperature

        # 1. Truy xuất các đoạn văn bản luật liên quan bằng Hybrid Search
        raw_sources = self.retrieve_context(query, top_k=top_k)

        # 2. TẦNG 2: RELEVANCE THRESHOLD GATE & FAST-EXIT
        top_score = raw_sources[0].get("score", 0.0) if raw_sources else 0.0
        
        if not raw_sources or top_score < self.relevance_threshold:
            return {
                "query": query,
                "answer": (
                    "Chào bạn, tôi là Trợ lý AI Tư vấn Pháp luật Trật tự, An toàn Giao thông Đường bộ. "
                    "Hệ thống nhận thấy câu hỏi của bạn không nằm trong phạm vi quy định pháp luật giao thông "
                    "hoặc dữ liệu tra cứu hiện tại chưa có thông tin phù hợp. "
                    "Vui lòng đặt câu hỏi liên quan đến quy tắc giao thông, mức xử phạt vi phạm hành chính "
                    "hoặc giấy phép lái xe để được hỗ trợ chính xác."
                ),
                "sources": []
            }

        # 3. Dynamic Chunk Pruning: Cắt tỉa các chunk ở đuôi bị loãng điểm
        pruned_sources = [
            s for s in raw_sources 
            if s.get("score", 0.0) >= 0.35 and s.get("score", 0.0) >= (top_score * 0.65)
        ]
        if not pruned_sources:
            pruned_sources = raw_sources[:1]

        # 4. Khử trùng an toàn (Sanitize): Làm sạch mã độc HTML/Script
        safe_query = TextCleaner.sanitize_text(query)
        safe_sources: List[Dict[str, Any]] = []
        for s in pruned_sources:
            safe_sources.append({
                "title": TextCleaner.sanitize_text(str(s.get("title", ""))),
                "snippet": TextCleaner.sanitize_text(str(s.get("snippet", ""))),
                "score": s.get("score"),
                "article": s.get("article")
            })

        # 5. Đóng gói ngữ cảnh vào khối định dạng rõ ràng (chống Prompt Injection)
        context_blocks = "\n\n".join([f"[{s['title']}]:\n{s['snippet']}" for s in safe_sources])
        context_text = f"```text\n{context_blocks}\n```"

        prompt_template = get_rag_prompt_template()

        # Kỹ thuật Two-Phase Replacement chống lỗi cú pháp
        TOKEN_CTX = "__LEGAL_RAG_CONTEXT_PLACEHOLDER_TOKEN__"
        TOKEN_QST = "__LEGAL_RAG_QUESTION_PLACEHOLDER_TOKEN__"
        full_prompt = (
            prompt_template
            .replace("{context}", TOKEN_CTX)
            .replace("{question}", TOKEN_QST)
            .replace(TOKEN_CTX, context_text)
            .replace(TOKEN_QST, safe_query)
        )

        # 6. Sinh câu trả lời từ LLM Engine
        raw_answer = self.llm_engine.generate(full_prompt)

        # 7. Hậu xử lý làm sạch văn bản (Post-processing cleaner)
        clean_answer = TextCleaner.clean_llm_output(raw_answer)

        return {
            "query": query,
            "answer": clean_answer,
            "sources": safe_sources
        }
