"""
Module: session_schema.py
Mục đích: Định nghĩa Pydantic Models cho các yêu cầu và phản hồi quản lý Phiên và Tin nhắn đa phiên.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    """Payload tạo phiên hội thoại mới."""
    title: Optional[str] = Field("Cuộc trò chuyện mới", description="Tiêu đề gợi nhớ của phiên")


class SessionUpdateRequest(BaseModel):
    """Payload cập nhật thông tin phiên hội thoại."""
    title: Optional[str] = Field(None, description="Tiêu đề mới của phiên")
    is_pinned: Optional[bool] = Field(None, description="Trạng thái ghim phiên lên đầu danh sách")


class SessionItem(BaseModel):
    """Thông tin tóm tắt của một phiên hiển thị trên Sidebar."""
    id: str
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class SessionListResponse(BaseModel):
    """Danh sách các phiên hội thoại của người dùng."""
    sessions: List[SessionItem]


class ChatMessageItem(BaseModel):
    """Thông tin chi tiết một tin nhắn (đã giải mã nội dung) trả về cho UI."""
    id: str
    role: str
    content: str
    sources: Optional[List[Any]] = None
    created_at: datetime
    timestamp: str


class SessionDetailResponse(BaseModel):
    """Chi tiết đầy đủ của một phiên kèm danh sách toàn bộ tin nhắn đã giải mã."""
    id: str
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageItem]
