"""
Module: chat_schema.py
Mục đích: Định nghĩa cấu trúc dữ liệu đầu vào và đầu ra cho API bằng Pydantic.
Người phụ trách chính: Thành viên 3 (Backend API Lead)
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """
    Cấu trúc dữ liệu yêu cầu gửi câu hỏi từ Frontend.
    """
    query: str = Field(..., description="Câu hỏi của người dùng về luật an toàn giao thông", min_length=2)
    top_k: Optional[int] = Field(default=3, description="Số lượng đoạn văn bản trích xuất", ge=1, le=10)
    temperature: Optional[float] = Field(default=0.2, description="Độ sáng tạo của mô hình", ge=0.0, le=1.0)
    session_id: Optional[str] = Field(default=None, description="Mã định danh phiên hội thoại (nếu có)")

class SourceDocument(BaseModel):
    """
    Cấu trúc thông tin một đoạn trích dẫn căn cứ pháp lý.
    """
    title: str = Field(..., description="Tên hoặc số hiệu văn bản luật")
    snippet: str = Field(..., description="Đoạn trích nội dung điều khoản liên quan")
    score: Optional[float] = Field(default=None, description="Điểm tương đồng ngữ nghĩa")
    article: Optional[str] = Field(default=None, description="Điều/Khoản cụ thể nếu có trích xuất")

class ChatResponse(BaseModel):
    """
    Cấu trúc dữ liệu trả về cho Frontend.
    """
    query: str = Field(..., description="Câu hỏi gốc")
    answer: str = Field(..., description="Câu trả lời đã được tổng hợp từ RAG")
    sources: List[SourceDocument] = Field(default=[], description="Danh sách các căn cứ pháp lý được trích dẫn")
    session_id: Optional[str] = Field(default=None, description="Mã phiên hội thoại")
    cached: Optional[bool] = Field(default=False, description="Đánh dấu câu trả lời từ bộ nhớ đệm Cache")
    execution_time_ms: Optional[float] = Field(default=None, description="Thời gian xử lý tính bằng mili-giây")

class HealthResponse(BaseModel):
    """
    Cấu trúc kiểm tra trạng thái hoạt động của hệ thống.
    """
    status: str = Field(default="ok", description="Trạng thái hệ thống")
    message: str = Field(default="Hệ thống AI Chatbot An toàn Giao thông đang hoạt động ổn định")
    version: Optional[str] = Field(default="2.0.0", description="Phiên bản API hiện tại")
    uptime_seconds: Optional[float] = Field(default=None, description="Thời gian máy chủ đã chạy (giây)")
    timestamp: Optional[str] = Field(default=None, description="Thời điểm phản hồi theo chuẩn ISO")
