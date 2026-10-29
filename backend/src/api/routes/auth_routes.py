"""
Module: auth_routes.py
Mục đích: Cung cấp các endpoints xác thực tài khoản: Đăng ký, Đăng nhập, Xem hồ sơ cá nhân và Đổi mật khẩu.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.database import get_db
from ...db.models import User
from ...services.crypto_service import hash_password, verify_password, create_access_token
from ...services.audit_service import log_audit_event
from ..schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfile,
    ChangePasswordRequest,
)
from ..dependencies import get_current_user, get_client_ip, get_user_agent

logger = logging.getLogger("api.auth_routes")
router = APIRouter(prefix="/api/auth", tags=["Authentication & Profile"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    req_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Đăng ký tài khoản người dùng mới.
    Mật khẩu được băm bằng thuật toán Argon2id trước khi lưu vào CSDL.
    """
    email_clean = req_data.email.lower().strip()
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    # Kiểm tra email đã tồn tại hay chưa
    result = await db.execute(
        select(User).where(User.email == email_clean)
    )
    existing_user = result.scalar_one_or_none()

    # Băm mật khẩu Argon2id
    hashed_pwd = hash_password(req_data.password)

    if existing_user:
        if existing_user.deleted_at is not None:
            # Tái kích hoạt tài khoản đã xóa mềm trước đó
            existing_user.deleted_at = None
            existing_user.is_active = True
            existing_user.password_hash = hashed_pwd
            await db.commit()
            await db.refresh(existing_user)
            new_user = existing_user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Địa chỉ email này đã được đăng ký trên hệ thống."
            )
    else:
        new_user = User(
            email=email_clean,
            password_hash=hashed_pwd,
            role="user",
            is_active=True
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    # Ghi nhận sự kiện kiểm toán
    await log_audit_event(
        db=db,
        action="REGISTER_SUCCESS",
        actor_id=new_user.id,
        actor_email=new_user.email,
        details={"role": new_user.role},
        ip_address=client_ip,
        user_agent=ua
    )

    # Tạo Access Token JWT
    token = create_access_token({
        "sub": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=str(new_user.id),
            email=new_user.email,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    req_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Đăng nhập hệ thống bằng Email và Mật khẩu.
    Xác minh mật khẩu bằng Argon2id và cấp phát JWT Token.
    """
    email_clean = req_data.email.lower().strip()
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    result = await db.execute(
        select(User).where(User.email == email_clean, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req_data.password, user.password_hash):
        # Ghi log đăng nhập thất bại để phát hiện brute force
        await log_audit_event(
            db=db,
            action="LOGIN_FAILED",
            actor_email=email_clean,
            details={"attempted_email": email_clean},
            ip_address=client_ip,
            user_agent=ua
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Địa chỉ email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        # Ghi log tài khoản bị khóa cố đăng nhập
        await log_audit_event(
            db=db,
            action="LOGIN_BLOCKED_LOCKED_ACCOUNT",
            actor_id=user.id,
            actor_email=user.email,
            ip_address=client_ip,
            user_agent=ua
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa bởi Quản trị viên. Vui lòng liên hệ để được hỗ trợ.",
        )

    # Ghi log đăng nhập thành công
    await log_audit_event(
        db=db,
        action="LOGIN_SUCCESS",
        actor_id=user.id,
        actor_email=user.email,
        details={"role": user.role},
        ip_address=client_ip,
        user_agent=ua
    )

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=str(user.id),
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin hồ sơ của người dùng hiện tại đang đăng nhập.
    """
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/change-password")
async def change_password(
    request: Request,
    req_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Người dùng tự đổi mật khẩu cá nhân.
    """
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    if not verify_password(req_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác."
        )

    current_user.password_hash = hash_password(req_data.new_password)
    await db.commit()

    await log_audit_event(
        db=db,
        action="PASSWORD_CHANGE",
        actor_id=current_user.id,
        actor_email=current_user.email,
        ip_address=client_ip,
        user_agent=ua
    )

    return {"message": "Đổi mật khẩu thành công."}
