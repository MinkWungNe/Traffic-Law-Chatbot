"""
Module: chat_routes.py
Mục đích: Định nghĩa các Endpoints API xử lý yêu cầu hỏi đáp RAG và kiểm tra sức khỏe hệ thống.
Người phụ trách chính: Thành viên 3 (Backend API Lead)
"""

from fastapi import APIRouter, HTTPException
from ..schemas.chat_schema import ChatRequest, ChatResponse, HealthResponse, SourceDocument
from ...rag.rag_pipeline import LegalRAGPipeline

router = APIRouter(prefix="/api", tags=["Chat & Search"])

# Khởi tạo instance RAG Pipeline
rag_pipeline = LegalRAGPipeline()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Kiểm tra trạng thái máy chủ Backend.
    """
    return HealthResponse()

@router.post("/chat", response_model=ChatResponse)
def handle_chat_query(req: ChatRequest):
    """
    Tiếp nhận câu hỏi từ giao diện, thực thi RAG và trả về câu trả lời chuẩn luật.
    """
    try:
        result = rag_pipeline.answer_question(
            query=req.query,
            top_k=req.top_k,
            temperature=req.temperature
        )
        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            sources=[
                SourceDocument(
                    title=s["title"],
                    snippet=s["snippet"],
                    score=s.get("score")
                )
                for s in result.get("sources", [])
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý nội bộ: {str(e)}")
