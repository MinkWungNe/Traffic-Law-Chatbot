"""
Module: dependencies.py
Mục đích: Cung cấp các Dependency Injection cho FastAPI:
- Trích xuất và xác thực người dùng từ Bearer Token
- Kiểm tra phân quyền RBAC (Role: Admin / User)
- Hỗ trợ người dùng vãng lai (Guest Mode) qua get_optional_current_user
"""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.database import get_db
from ..db.models import User
from ..services.crypto_service import decode_access_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency bắt buộc người dùng phải đăng nhập và gửi Token hợp lệ.
    Kiểm tra tài khoản không bị xóa mềm và không bị khóa.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực danh tính. Vui lòng đăng nhập để tiếp tục.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa định danh người dùng.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Định danh người dùng trong Token không hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị xóa khỏi hệ thống.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này hiện đang bị tạm khóa bởi Quản trị viên.",
        )

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency tùy chọn: Nếu có token hợp lệ thì trả về User, nếu là khách (Guest) thì trả về None.
    Dành riêng cho endpoint /api/chat để phục vụ cả Khách lẫn Thành viên.
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_uuid = uuid.UUID(user_id_str)
        result = await db.execute(
            select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency kiểm tra quyền Quản trị viên (Admin).
    Chỉ cho phép tài khoản có role='admin' truy cập các endpoint /api/admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Từ chối truy cập: Bạn không có quyền hạn Quản trị viên (Admin) đối với tác vụ này.",
        )
    return current_user


def get_client_ip(request: Request) -> str:
    """
    Trích xuất IP của client từ request headers (x-forwarded-for hoặc client.host).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    Trích xuất chuỗi User-Agent từ request headers.
    """
    return request.headers.get("user-agent", "unknown")
