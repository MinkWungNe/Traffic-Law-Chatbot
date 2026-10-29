"""
Module: auth_schema.py
Mục đích: Định nghĩa Pydantic Models cho các yêu cầu và phản hồi về Xác thực & Quản trị User.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload đăng ký tài khoản mới."""
    email: EmailStr = Field(..., description="Địa chỉ email hợp lệ của người dùng")
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")


class UserLoginRequest(BaseModel):
    """Payload đăng nhập hệ thống."""
    email: EmailStr = Field(..., description="Địa chỉ email đăng nhập")
    password: str = Field(..., description="Mật khẩu tài khoản")


class UserProfile(BaseModel):
    """Thông tin công khai của người dùng."""
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Phản hồi sau khi đăng nhập thành công."""
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class ChangePasswordRequest(BaseModel):
    """Yêu cầu đổi mật khẩu cá nhân."""
    old_password: str = Field(..., description="Mật khẩu hiện tại")
    new_password: str = Field(..., min_length=6, description="Mật khẩu mới tối thiểu 6 ký tự")


class AdminResetPasswordRequest(BaseModel):
    """Admin đặt lại mật khẩu cho tài khoản người dùng."""
    new_password: str = Field(..., min_length=6, description="Mật khẩu mới được thiết lập bởi Admin")


class AdminUpdateStatusRequest(BaseModel):
    """Admin cập nhật trạng thái khóa/mở khóa tài khoản."""
    is_active: bool = Field(..., description="Trạng thái hoạt động: True (Mở khóa) / False (Khóa)")
    reason: Optional[str] = Field(None, description="Lý do khóa hoặc mở khóa tài khoản")


class UserListResponse(BaseModel):
    """Danh sách người dùng trả về cho trang Admin."""
    users: List[UserProfile]
    total: int


class AuditLogItem(BaseModel):
    """Bản ghi nhật ký kiểm toán đơn lẻ."""
    id: str
    actor_id: Optional[str] = None
    actor_email: str
    action: str
    target_id: Optional[str] = None
    target_email: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Danh sách nhật ký kiểm toán phục vụ phân trang trên giao diện Admin."""
    logs: List[AuditLogItem]
    total: int
