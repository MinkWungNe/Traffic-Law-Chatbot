"""
Module: admin_routes.py
Mục đích: Cung cấp các endpoints quản trị dành riêng cho tài khoản có vai trò Admin:
Quản lý người dùng (Đổi mật khẩu, Khóa/Mở khóa, Xóa mềm) và Tra cứu Nhật ký kiểm toán (Audit Logs).
"""

import uuid
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from ...db.database import get_db
from ...db.models import User, AuditLog
from ...services.crypto_service import hash_password
from ...services.audit_service import log_audit_event
from ..schemas.auth_schema import (
    UserProfile,
    UserListResponse,
    AdminResetPasswordRequest,
    AdminUpdateStatusRequest,
    AuditLogItem,
    AuditLogListResponse,
)
from ..dependencies import require_admin, get_client_ip, get_user_agent

logger = logging.getLogger("api.admin_routes")
router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng bản ghi mỗi trang"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo email"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách tài khoản người dùng có phân trang và tìm kiếm (Chỉ Admin).
    """
    offset = (page - 1) * limit
    stmt = select(User).where(User.deleted_at.is_(None))

    if search:
        search_pattern = f"%{search.strip().lower()}%"
        stmt = stmt.where(User.email.ilike(search_pattern))

    # Đếm tổng số lượng bản ghi
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one() or 0

    # Lấy danh sách sắp xếp theo ngày tạo mới nhất
    stmt = stmt.order_by(desc(User.created_at)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    user_profiles = [
        UserProfile(
            id=str(u.id),
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]

    return UserListResponse(users=user_profiles, total=total)


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    request: Request,
    req_data: AdminUpdateStatusRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Khóa hoặc Mở khóa tài khoản người dùng (Chỉ Admin).
    Không cho phép Admin tự khóa tài khoản của chính mình.
    """
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    try:
        target_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ.")

    if target_uuid == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể tự khóa tài khoản Quản trị viên của chính mình."
        )

    result = await db.execute(
        select(User).where(User.id == target_uuid, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    user.is_active = req_data.is_active
    await db.commit()

    action_name = "ADMIN_UNLOCK_USER" if req_data.is_active else "ADMIN_LOCK_USER"
    await log_audit_event(
        db=db,
        action=action_name,
        actor_id=admin.id,
        actor_email=admin.email,
        target_id=user.id,
        target_email=user.email,
        details={"reason": req_data.reason, "new_active_status": req_data.is_active},
        ip_address=client_ip,
        user_agent=ua
    )

    action_text = "Mở khóa" if req_data.is_active else "Khóa"
    return {"message": f"{action_text} tài khoản thành công."}


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: str,
    request: Request,
    req_data: AdminResetPasswordRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin đặt lại mật khẩu mới cho tài khoản người dùng.
    """
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    try:
        target_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ.")

    result = await db.execute(
        select(User).where(User.id == target_uuid, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    user.password_hash = hash_password(req_data.new_password)
    await db.commit()

    await log_audit_event(
        db=db,
        action="ADMIN_RESET_PASSWORD",
        actor_id=admin.id,
        actor_email=admin.email,
        target_id=user.id,
        target_email=user.email,
        details={"reset_by_admin": admin.email},
        ip_address=client_ip,
        user_agent=ua
    )

    return {"message": f"Đặt lại mật khẩu cho tài khoản {user.email} thành công."}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa mềm (Soft Delete) tài khoản người dùng: Đánh dấu thời gian xóa và vô hiệu hóa tài khoản.
    Không cho phép Admin tự xóa chính mình.
    """
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    try:
        target_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ.")

    if target_uuid == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn không thể tự xóa tài khoản của chính mình."
        )

    result = await db.execute(
        select(User).where(User.id == target_uuid, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    await db.commit()

    await log_audit_event(
        db=db,
        action="ADMIN_DELETE_USER",
        actor_id=admin.id,
        actor_email=admin.email,
        target_id=user.id,
        target_email=user.email,
        details={"soft_deleted_at": user.deleted_at.isoformat()},
        ip_address=client_ip,
        user_agent=ua
    )

    return {"message": f"Đã xóa tài khoản {user.email} thành công (Xóa mềm)."}


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(30, ge=1, le=100, description="Số lượng bản ghi mỗi trang"),
    action: Optional[str] = Query(None, description="Bộ lọc theo hành động kiểm toán"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách nhật ký kiểm toán hệ thống (Chỉ Admin).
    """
    offset = (page - 1) * limit
    stmt = select(AuditLog)

    if action:
        stmt = stmt.where(AuditLog.action == action.strip())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one() or 0

    stmt = stmt.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    log_items = [
        AuditLogItem(
            id=str(log.id),
            actor_id=str(log.actor_id) if log.actor_id else None,
            actor_email=log.actor_email,
            action=log.action,
            target_id=str(log.target_id) if log.target_id else None,
            target_email=log.target_email,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at
        )
        for log in logs
    ]

    return AuditLogListResponse(logs=log_items, total=total)


BENCHMARK_REPORT_PATH = Path("evaluation/benchmark_report.json")


@router.get("/benchmark/results")
async def get_benchmark_results(
    admin: User = Depends(require_admin)
):
    """
    Lấy kết quả báo cáo đánh giá chất lượng RAG gần nhất.
    """
    if not BENCHMARK_REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu báo cáo đánh giá. Vui lòng bấm 'Chạy Benchmark' để tạo mới."
        )
    try:
        with open(BENCHMARK_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Lỗi đọc file benchmark_report.json: {e}")
        raise HTTPException(status_code=500, detail="Không thể nạp dữ liệu báo cáo đánh giá.")


@router.post("/benchmark/run")
async def run_benchmark(
    request: Request,
    top_k: int = Query(3, ge=1, le=10, description="Top K tài liệu truy xuất"),
    max_samples: Optional[int] = Query(50, ge=5, le=683, description="Số lượng mẫu kiểm thử (None hoặc tối đa 683)"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Kích hoạt chạy kịch bản đánh giá Benchmark trên tập dữ liệu kiểm thử.
    """
    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    try:
        from evaluation.benchmark_runner import BenchmarkRunner
        runner = BenchmarkRunner(test_dataset_path="data/raw/683_CauHoi_TTATGTDB.csv")
        report = runner.evaluate_retrieval(top_k=top_k, max_samples=max_samples)
        runner.export_report(output_path=str(BENCHMARK_REPORT_PATH))

        await log_audit_event(
            db=db,
            action="BENCHMARK_EXECUTE",
            actor_id=admin.id,
            actor_email=admin.email,
            target_id=None,
            target_email=None,
            details={
                "top_k": top_k,
                "samples_evaluated": report.get("metadata", {}).get("evaluated_samples", max_samples),
                "hit_rate": report.get("summary_metrics", {}).get("hit_rate_percentage"),
                "mrr": report.get("summary_metrics", {}).get("mrr")
            },
            ip_address=client_ip,
            user_agent=ua
        )

        return report
    except Exception as e:
        logger.error(f"Lỗi khi thực thi benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi thực thi benchmark: {str(e)}")

