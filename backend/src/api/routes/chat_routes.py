"""
Module: chat_routes.py
Mục đích: Định nghĩa các Endpoints API xử lý yêu cầu hỏi đáp RAG, tra cứu trích dẫn và kiểm tra sức khỏe hệ thống.
Hỗ trợ lưu trữ lịch sử mã hóa AES-256-GCM khi người dùng đã đăng nhập (Multi-Session).
"""

import time
import json
import uuid
import csv
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SourceDocument,
    SearchRequest,
    SearchResponse,
    RelatedDocItem,
    LegalDocItem,
    LegalDocsListResponse,
)
from ...rag.rag_pipeline import LegalRAGPipeline
from ...db.database import get_db
from ...db.models import User, ChatSession, ChatMessage
from ...services.crypto_service import encrypt_text
from ..dependencies import get_optional_current_user

logger = logging.getLogger("api.chat_routes")
router = APIRouter(prefix="/api", tags=["Chat & Search"])

# Khởi tạo instance RAG Pipeline
rag_pipeline = LegalRAGPipeline()
SERVER_START_TIME = time.time()

# In-Memory Cache cho các câu hỏi phổ biến
_CACHE_TTL_SECONDS = 600  # 10 phút
_MAX_CACHE_ENTRIES = 200
_query_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

LEGAL_DOCS_JSON_PATH = Path("data/legal_documents.json")


def load_legal_documents() -> List[LegalDocItem]:
    """
    Đọc danh mục văn bản quy phạm pháp luật và quan hệ văn bản hợp nhất từ tệp JSON cấu trúc.
    """
    if not LEGAL_DOCS_JSON_PATH.exists():
        logger.warning(f"Không tìm thấy file {LEGAL_DOCS_JSON_PATH}. Trả về danh sách rỗng.")
        return []

    try:
        with open(LEGAL_DOCS_JSON_PATH, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            return [LegalDocItem(**item) for item in data]
    except Exception as e:
        logger.error(f"Lỗi khi đọc file JSON văn bản pháp luật: {e}")
        return []


def _get_cache_key(query: str, top_k: int, temperature: float) -> str:
    """Tạo khóa chuẩn hóa cho bộ nhớ đệm Cache."""
    return f"{query.strip().lower()}:{top_k}:{temperature:.2f}"


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Kiểm tra trạng thái máy chủ Backend.
    """
    now = datetime.now(timezone.utc).isoformat()
    uptime = round(time.time() - SERVER_START_TIME, 2)
    return HealthResponse(
        status="ok",
        message="Hệ thống AI Chatbot An toàn Giao thông đang hoạt động ổn định",
        version="2.0.0",
        uptime_seconds=uptime,
        timestamp=now
    )


@router.post("/chat", response_model=ChatResponse)
async def handle_chat_query(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tiếp nhận câu hỏi từ giao diện, thực thi RAG và trả về câu trả lời chuẩn luật.
    - Nếu là Khách (Guest): Trả về câu trả lời tức thì, không lưu DB.
    - Nếu là Thành viên đăng nhập: Tự động mã hóa AES-256-GCM câu hỏi và câu trả lời, lưu vào phiên hội thoại tương ứng.
    """
    start_time = time.perf_counter()
    cache_key = _get_cache_key(req.query, req.top_k or 3, req.temperature or 0.2)
    current_time = time.time()

    answer_text = ""
    sources: List[SourceDocument] = []
    is_cached = False

    # 1. Kiểm tra Cache
    if cache_key in _query_cache:
        cached_timestamp, cached_data = _query_cache[cache_key]
        if current_time - cached_timestamp < _CACHE_TTL_SECONDS:
            answer_text = cached_data["answer"]
            sources = [SourceDocument(**s) for s in cached_data["sources"]]
            is_cached = True
            logger.info(f"Cache HIT for query: '{req.query}'")

    # 2. Xử lý qua RAG Pipeline nếu chưa có cache
    if not is_cached:
        try:
            result = rag_pipeline.answer_question(
                query=req.query,
                top_k=req.top_k,
                temperature=req.temperature
            )

            answer_text = result["answer"]
            sources = [
                SourceDocument(
                    title=s["title"],
                    snippet=s["snippet"],
                    score=s.get("score")
                )
                for s in result.get("sources", [])
            ]

            # Lưu vào Cache
            if len(_query_cache) >= _MAX_CACHE_ENTRIES:
                oldest_key = min(_query_cache, key=lambda k: _query_cache[k][0])
                _query_cache.pop(oldest_key, None)

            _query_cache[cache_key] = (
                current_time,
                {
                    "query": req.query,
                    "answer": answer_text,
                    "sources": [s.model_dump() for s in sources]
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Internal processing error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Lỗi xử lý nội bộ: {str(e)}")

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    final_session_id = req.session_id

    # 3. Lưu trữ tin nhắn mã hóa nếu người dùng đã đăng nhập
    if current_user:
        target_session: Optional[ChatSession] = None
        if req.session_id:
            try:
                s_uuid = uuid.UUID(req.session_id)
                res = await db.execute(
                    select(ChatSession).where(
                        ChatSession.id == s_uuid,
                        ChatSession.user_id == current_user.id
                    )
                )
                target_session = res.scalar_one_or_none()
            except ValueError:
                target_session = None

        if not target_session:
            # Tự động tạo phiên mới nếu chưa có hoặc id không khớp
            title_text = req.query.strip()
            title_snippet = title_text[:35] + ("..." if len(title_text) > 35 else "")
            target_session = ChatSession(
                user_id=current_user.id,
                title=title_snippet,
                is_pinned=False
            )
            db.add(target_session)
            await db.commit()
            await db.refresh(target_session)

        final_session_id = str(target_session.id)

        # Lưu tin nhắn của User (Mã hóa AES-256-GCM)
        user_msg = ChatMessage(
            session_id=target_session.id,
            role="user",
            content_encrypted=encrypt_text(req.query),
            sources_encrypted=None
        )
        db.add(user_msg)

        # Lưu tin nhắn phản hồi của Bot (Mã hóa AES-256-GCM)
        sources_payload = json.dumps([s.model_dump() for s in sources], ensure_ascii=False)
        bot_msg = ChatMessage(
            session_id=target_session.id,
            role="bot",
            content_encrypted=encrypt_text(answer_text),
            sources_encrypted=encrypt_text(sources_payload)
        )
        db.add(bot_msg)

        # Cập nhật thời gian phiên
        target_session.updated_at = datetime.now(timezone.utc)
        await db.commit()

    return ChatResponse(
        query=req.query,
        answer=answer_text,
        sources=sources,
        session_id=final_session_id,
        cached=is_cached,
        execution_time_ms=elapsed_ms
    )


@router.post("/search", response_model=SearchResponse)
def search_legal_sources(req: SearchRequest):
    """
    Truy xuất nhanh các điều khoản và căn cứ pháp lý liên quan từ cơ sở tri thức (không sinh câu trả lời LLM).
    """
    try:
        raw_sources = rag_pipeline.retrieve_context(query=req.query, top_k=req.top_k or 3)
        sources = [
            SourceDocument(
                title=s["title"],
                snippet=s["snippet"],
                score=s.get("score")
            )
            for s in raw_sources
        ]
        return SearchResponse(
            query=req.query,
            total=len(sources),
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi truy xuất căn cứ pháp lý: {str(e)}")


@router.get("/documents", response_model=LegalDocsListResponse)
def get_legal_documents():
    """
    Trả về danh mục toàn bộ văn bản quy phạm pháp luật giao thông được nạp từ tệp CSV tập trung.
    """
    docs = load_legal_documents()
    return LegalDocsListResponse(
        total=len(docs),
        documents=docs
    )
