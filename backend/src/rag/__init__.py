"""
Package: rag
Phân hệ RAG Core: Định nghĩa Prompt, nạp mô hình VinaLlama và luồng suy luận hỏi đáp.
"""
from .prompt_templates import get_rag_prompt_template, LEGAL_QA_SYSTEM_PROMPT
from .llm_engine import LLMEngine
from .rag_pipeline import LegalRAGPipeline

__all__ = ["get_rag_prompt_template", "LEGAL_QA_SYSTEM_PROMPT", "LLMEngine", "LegalRAGPipeline"]
