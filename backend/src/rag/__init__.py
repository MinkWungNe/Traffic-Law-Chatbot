"""
Package: rag
Phân hệ RAG Core: Định nghĩa Prompt, nạp mô hình VinaLlama, tiền xử lý và luồng suy luận hỏi đáp.
"""
from .prompt_templates import get_rag_prompt_template, LEGAL_QA_SYSTEM_PROMPT, LEGAL_COT_SYSTEM_PROMPT
from .llm_engine import LLMEngine
from .rag_pipeline import LegalRAGPipeline
from .query_normalizer import QueryNormalizer
from .hybrid_retriever import HybridRetriever

__all__ = [
    "get_rag_prompt_template", 
    "LEGAL_QA_SYSTEM_PROMPT", 
    "LEGAL_COT_SYSTEM_PROMPT",
    "LLMEngine", 
    "LegalRAGPipeline",
    "QueryNormalizer",
    "HybridRetriever"
]
