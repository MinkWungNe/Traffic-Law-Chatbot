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
    version: Optional[str] = Field(default="1.0.0", description="Phiên bản API hiện tại")
    uptime_seconds: Optional[float] = Field(default=None, description="Thời gian máy chủ đã chạy (giây)")
    timestamp: Optional[str] = Field(default=None, description="Thời điểm phản hồi theo chuẩn ISO")

class SearchRequest(BaseModel):
    """
    Cấu trúc truy vấn tìm kiếm nhanh căn cứ pháp lý (chỉ trích xuất, không sinh câu trả lời).
    """
    query: str = Field(..., description="Từ khóa hoặc câu hỏi cần tra cứu trích dẫn", min_length=2)
    top_k: Optional[int] = Field(default=3, description="Số lượng trích dẫn", ge=1, le=10)

class SearchResponse(BaseModel):
    """
    Kết quả trả về danh sách căn cứ pháp lý liên quan.
    """
    query: str = Field(..., description="Từ khóa tìm kiếm")
    total: int = Field(default=0, description="Tổng số trích dẫn tìm thấy")
    sources: List[SourceDocument] = Field(default=[], description="Danh sách các đoạn luật trích xuất")

class RelatedDocItem(BaseModel):
    """
    Thông tin văn bản thành phần trong văn bản hợp nhất (văn bản gốc hoặc văn bản sửa đổi, bổ sung).
    """
    relation_type: str = Field(..., description="Loại quan hệ: 'goc' (Văn bản gốc) hoặc 'sua_doi' (Văn bản sửa đổi, bổ sung)")
    relation_label: str = Field(..., description="Nhãn hiển thị, ví dụ: 'Văn bản gốc', 'Văn bản sửa đổi, bổ sung'")
    title: str = Field(..., description="Tên văn bản")
    number: str = Field(..., description="Số hiệu văn bản")
    source_url: str = Field(..., description="Đường dẫn tra cứu trên vbpl.vn")

class LegalDocItem(BaseModel):
    """
    Cấu trúc mô tả một văn bản quy phạm pháp luật trong cơ sở dữ liệu.
    """
    id: str = Field(..., description="Mã định danh văn bản")
    category: str = Field(..., description="Phân loại: luat, nghi-dinh, thong-tu, quy-chuan")
    type_label: str = Field(..., description="Tên loại văn bản hiển thị")
    title: str = Field(..., description="Tiêu đề chính của văn bản")
    number: str = Field(..., description="Số hiệu văn bản")
    date: str = Field(..., description="Ngày ban hành hoặc có hiệu lực")
    status: str = Field(..., description="Tình trạng hiệu lực")
    desc: str = Field(..., description="Mô tả tóm tắt nội dung quy định")
    source_url: Optional[str] = Field(default="", description="Đường dẫn trực tiếp đến văn bản trên vbpl.vn")
    is_consolidated: bool = Field(default=False, description="Đánh dấu là văn bản hợp nhất")
    related_docs: List[RelatedDocItem] = Field(default=[], description="Danh sách văn bản gốc và văn bản sửa đổi, bổ sung")

class LegalDocsListResponse(BaseModel):
    """
    Danh mục toàn bộ văn bản pháp luật hiện có trong hệ thống.
    """
    total: int = Field(default=0, description="Tổng số văn bản")
    documents: List[LegalDocItem] = Field(default=[], description="Danh sách các văn bản luật")
