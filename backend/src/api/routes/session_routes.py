"""
Module: session_routes.py
Mục đích: Cung cấp các endpoints quản trị đa phiên (Multi-Session):
Tạo phiên, liệt kê phiên, cập nhật (đổi tên/ghim), xóa phiên và tải tin nhắn đã giải mã.
"""

import uuid
import json
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from ...db.database import get_db
from ...db.models import User, ChatSession, ChatMessage
from ...services.crypto_service import decrypt_text
from ..schemas.session_schema import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionItem,
    SessionListResponse,
    ChatMessageItem,
    SessionDetailResponse,
)
from ..dependencies import get_current_user

logger = logging.getLogger("api.session_routes")
router = APIRouter(prefix="/api/sessions", tags=["Chat Sessions"])


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách toàn bộ các phiên trò chuyện của người dùng hiện tại.
    Sắp xếp: Các phiên được Ghim (is_pinned=True) lên đầu, tiếp theo là theo thời gian cập nhật mới nhất.
    """
    stmt = (
        select(
            ChatSession,
            func.count(ChatMessage.id).label("message_count")
        )
        .outerjoin(ChatMessage, ChatMessage.session_id == ChatSession.id)
        .where(ChatSession.user_id == current_user.id)
        .group_by(ChatSession.id)
        .order_by(desc(ChatSession.is_pinned), desc(ChatSession.updated_at))
    )
    result = await db.execute(stmt)
    rows = result.all()

    session_items: List[SessionItem] = []
    for s, count in rows:
        session_items.append(
            SessionItem(
                id=str(s.id),
                title=s.title,
                is_pinned=s.is_pinned,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count
            )
        )

    return SessionListResponse(sessions=session_items)


@router.post("", response_model=SessionItem, status_code=status.HTTP_201_CREATED)
async def create_session(
    req_data: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Khởi tạo một phiên trò chuyện mới.
    """
    new_session = ChatSession(
        user_id=current_user.id,
        title=req_data.title.strip() if req_data.title else "Cuộc trò chuyện mới",
        is_pinned=False
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return SessionItem(
        id=str(new_session.id),
        title=new_session.title,
        is_pinned=new_session.is_pinned,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        message_count=0
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy chi tiết một phiên hội thoại và tự động giải mã toàn bộ danh sách tin nhắn bằng AES-256-GCM.
    """
    try:
        s_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID phiên hội thoại không hợp lệ.")

    # Tải session kèm eager load danh sách messages
    stmt = (
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == s_uuid, ChatSession.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên trò chuyện.")

    # Giải mã từng tin nhắn
    decrypted_messages: List[ChatMessageItem] = []
    for m in session.messages:
        plain_content = decrypt_text(m.content_encrypted)
        sources_list = None
        if m.sources_encrypted:
            try:
                decrypted_sources_json = decrypt_text(m.sources_encrypted)
                sources_list = json.loads(decrypted_sources_json)
            except Exception as e:
                logger.warning(f"Không thể parse JSON sources: {e}")
                sources_list = None

        time_str = m.created_at.strftime("%H:%M")

        decrypted_messages.append(
            ChatMessageItem(
                id=str(m.id),
                role=m.role,
                content=plain_content,
                sources=sources_list,
                created_at=m.created_at,
                timestamp=time_str
            )
        )

    return SessionDetailResponse(
        id=str(session.id),
        title=session.title,
        is_pinned=session.is_pinned,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=decrypted_messages
    )


@router.patch("/{session_id}", response_model=SessionItem)
async def update_session(
    session_id: str,
    req_data: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật tiêu đề phiên hoặc ghim/bỏ ghim phiên hội thoại.
    """
    try:
        s_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID phiên hội thoại không hợp lệ.")

    result = await db.execute(
        select(ChatSession).where(ChatSession.id == s_uuid, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên trò chuyện.")

    if req_data.title is not None:
        session.title = req_data.title.strip()
    if req_data.is_pinned is not None:
        session.is_pinned = req_data.is_pinned

    await db.commit()
    await db.refresh(session)

    # Đếm số tin nhắn
    count_stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session.id)
    count_res = await db.execute(count_stmt)
    count = count_res.scalar_one() or 0

    return SessionItem(
        id=str(session.id),
        title=session.title,
        is_pinned=session.is_pinned,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=count
    )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa phiên hội thoại và toàn bộ tin nhắn bên trong (CASCADE).
    """
    try:
        s_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID phiên hội thoại không hợp lệ.")

    result = await db.execute(
        select(ChatSession).where(ChatSession.id == s_uuid, ChatSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên trò chuyện.")

    await db.delete(session)
    await db.commit()

    return {"message": "Đã xóa phiên trò chuyện thành công."}
