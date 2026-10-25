"""
Module: chat_routes.py
Mục đích: Định nghĩa các Endpoints API xử lý yêu cầu hỏi đáp RAG, tra cứu trích dẫn và kiểm tra sức khỏe hệ thống.
Người phụ trách chính: Thành viên 3 (Backend API Lead)
"""

import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from fastapi import APIRouter, HTTPException
from ..schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SourceDocument,
    SearchRequest,
    SearchResponse,
    LegalDocItem,
    LegalDocsListResponse,
)
from ...rag.rag_pipeline import LegalRAGPipeline

logger = logging.getLogger("api.chat_routes")
router = APIRouter(prefix="/api", tags=["Chat & Search"])

# Khởi tạo instance RAG Pipeline
rag_pipeline = LegalRAGPipeline()
SERVER_START_TIME = time.time()

# In-Memory Cache cho các câu hỏi phổ biến (Nhiệm vụ nâng cao Phân hệ 3)
_CACHE_TTL_SECONDS = 600  # Thời gian tồn tại bộ nhớ đệm: 10 phút
_MAX_CACHE_ENTRIES = 200
_query_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

# Danh mục văn bản pháp luật giao thông cốt lõi
CORE_LEGAL_DOCUMENTS: List[LegalDocItem] = [
    LegalDocItem(
        id="doc-ttatgt-36-2024",
        category="luat",
        type_label="Luật",
        title="Luật Trật tự, an toàn giao thông đường bộ 2024",
        number="Số 36/2024/QH15",
        date="27/06/2024",
        status="Có hiệu lực từ 01/01/2025",
        desc="Quy định toàn diện về quy tắc giao thông, điều kiện phương tiện, người điều khiển và giải quyết tai nạn giao thông."
    ),
    LegalDocItem(
        id="doc-nd-100-2019",
        category="nghi-dinh",
        type_label="Nghị định",
        title="Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường bộ và đường sắt",
        number="Số 100/2019/NĐ-CP",
        date="30/12/2019",
        status="Đang có hiệu lực thi hành",
        desc="Quy định chi tiết khung phạt tiền, tước GPLX, tạm giữ phương tiện đối với các hành vi vi phạm trật tự ATGT."
    ),
    LegalDocItem(
        id="doc-nd-123-2021",
        category="nghi-dinh",
        type_label="Nghị định",
        title="Nghị định sửa đổi, bổ sung một số điều của các Nghị định xử phạt vi phạm hành chính giao thông",
        number="Số 123/2021/NĐ-CP",
        date="28/12/2021",
        status="Đang có hiệu lực thi hành",
        desc="Tăng nặng mức xử phạt đối với các lỗi nguy cơ tai nạn cao: vượt đèn đỏ, chạy quá tốc độ, đi ngược chiều trên cao tốc."
    ),
    LegalDocItem(
        id="doc-qcvn-41-2019",
        category="quy-chuan",
        type_label="Quy chuẩn",
        title="Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ (QCVN 41:2019/BGTVT)",
        number="Thông tư 54/2019/TT-BGTVT",
        date="31/12/2019",
        status="Đang có hiệu lực thi hành",
        desc="Quy định quy chuẩn hình dáng, kích thước, màu sắc và ý nghĩa hệ thống biển báo, vạch kẻ đường, đèn tín hiệu."
    ),
    LegalDocItem(
        id="doc-luat-duong-bo-35-2024",
        category="luat",
        type_label="Luật",
        title="Luật Đường bộ 2024",
        number="Số 35/2024/QH15",
        date="27/06/2024",
        status="Có hiệu lực từ 01/01/2025",
        desc="Quy định về kết cấu hạ tầng đường bộ, phương tiện giao thông đường bộ, vận tải đường bộ và quản lý nhà nước."
    ),
    LegalDocItem(
        id="doc-nd-168-2024",
        category="nghi-dinh",
        type_label="Nghị định",
        title="Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực bảo đảm trật tự, an toàn giao thông đường bộ",
        number="Số 168/2024/NĐ-CP",
        date="2024",
        status="Văn bản hướng dẫn mới nhất",
        desc="Cập nhật khung xử phạt đồng bộ với Luật Trật tự, an toàn giao thông đường bộ 2024."
    )
]

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
        version="1.0.0",
        uptime_seconds=uptime,
        timestamp=now
    )

@router.post("/chat", response_model=ChatResponse)
def handle_chat_query(req: ChatRequest):
    """
    Tiếp nhận câu hỏi từ giao diện, thực thi RAG và trả về câu trả lời chuẩn luật.
    Có tích hợp Cache thông minh (LRU/TTL) cho các câu hỏi phổ biến nhằm tối ưu độ trễ < 0.1s.
    """
    start_time = time.perf_counter()
    cache_key = _get_cache_key(req.query, req.top_k or 3, req.temperature or 0.2)
    current_time = time.time()

    # 1. Kiểm tra Cache
    if cache_key in _query_cache:
        cached_timestamp, cached_data = _query_cache[cache_key]
        if current_time - cached_timestamp < _CACHE_TTL_SECONDS:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(f"Cache HIT for query: '{req.query}' in {elapsed_ms}ms")
            return ChatResponse(
                query=cached_data["query"],
                answer=cached_data["answer"],
                sources=[SourceDocument(**s) for s in cached_data["sources"]],
                session_id=req.session_id,
                cached=True,
                execution_time_ms=elapsed_ms
            )

    # 2. Xử lý qua RAG Pipeline
    try:
        result = rag_pipeline.answer_question(
            query=req.query,
            top_k=req.top_k,
            temperature=req.temperature
        )

        sources = [
            SourceDocument(
                title=s["title"],
                snippet=s["snippet"],
                score=s.get("score")
            )
            for s in result.get("sources", [])
        ]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 3. Lưu vào Cache
        if len(_query_cache) >= _MAX_CACHE_ENTRIES:
            # Xóa mục cũ nhất nếu vượt quá giới hạn
            oldest_key = min(_query_cache, key=lambda k: _query_cache[k][0])
            _query_cache.pop(oldest_key, None)

        _query_cache[cache_key] = (
            current_time,
            {
                "query": result["query"],
                "answer": result["answer"],
                "sources": [s.model_dump() for s in sources]
            }
        )

        logger.info(f"RAG processed query: '{req.query}' in {elapsed_ms}ms")

        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            sources=sources,
            session_id=req.session_id,
            cached=False,
            execution_time_ms=elapsed_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý nội bộ: {str(e)}")

@router.post("/search", response_model=SearchResponse)
def search_legal_sources(req: SearchRequest):
    """
    Truy xuất nhanh các điều khoản và căn cứ pháp lý liên quan từ cơ sở tri thức (không sinh câu trả lời LLM).
    Phù hợp cho các tính năng tra cứu văn bản tức thì.
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
    Trả về danh mục toàn bộ văn bản quy phạm pháp luật giao thông đang được tích hợp trong hệ thống.
    """
    return LegalDocsListResponse(
        total=len(CORE_LEGAL_DOCUMENTS),
        documents=CORE_LEGAL_DOCUMENTS
    )
