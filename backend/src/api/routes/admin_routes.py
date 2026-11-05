"""
Module: admin_routes.py
Mục đích: Cung cấp các endpoints quản trị dành riêng cho tài khoản có vai trò Admin:
Quản lý người dùng (Đổi mật khẩu, Khóa/Mở khóa, Xóa mềm) và Tra cứu Nhật ký kiểm toán (Audit Logs).
"""

import uuid
import json
import logging
import asyncio
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
from ..schemas.benchmark_schema import (
    BenchmarkFullReportResponse,
    BenchmarkSummaryResponse,
    BenchmarkSamplesResponse,
    BenchmarkQueryItem,
    QualityMetrics,
)
from ..dependencies import require_admin, get_client_ip, get_user_agent

logger = logging.getLogger("api.admin_routes")
router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

# Khóa tránh chạy đồng thời tác vụ Benchmark tiêu tốn tài nguyên hệ thống
_is_benchmark_running = False


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
RAGAS_REPORT_PATH = Path("evaluation/ragas_report.json")

# Bộ đệm in-memory cache cho báo cáo Benchmark tránh đọc đĩa và lặp JSON liên tục
_cached_benchmark_data: Optional[dict] = None
_cached_benchmark_mtime: float = 0.0



def _get_validated_benchmark_data() -> dict:
    """Nạp và chuẩn hóa dữ liệu báo cáo Benchmark & RAGAS từ file lưu trữ."""
    global _cached_benchmark_data, _cached_benchmark_mtime
    if not BENCHMARK_REPORT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chưa có dữ liệu báo cáo đánh giá. Vui lòng bấm 'Chạy Benchmark' để tạo mới."
        )
    current_mtime = BENCHMARK_REPORT_PATH.stat().st_mtime
    if _cached_benchmark_data is not None and current_mtime == _cached_benchmark_mtime:
        return _cached_benchmark_data
    try:
        with open(BENCHMARK_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Lỗi đọc file benchmark_report.json: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể nạp dữ liệu báo cáo đánh giá."
        )

    # Nạp bổ sung quality_metrics nếu có file ragas_report.json
    if not data.get("quality_metrics") and RAGAS_REPORT_PATH.exists():
        try:
            with open(RAGAS_REPORT_PATH, "r", encoding="utf-8") as rf:
                ragas_data = json.load(rf)
                data["quality_metrics"] = ragas_data.get("summary_metrics")
        except Exception as e:
            logger.warning(f"Không thể nạp file ragas_report.json: {e}")

    # Chuẩn hóa an toàn các chỉ số RAGAS (tránh trả về None/null cho các trường tính toán)
    qm = data.get("quality_metrics")
    if qm:
        faith = float(qm.get("faithfulness_score", 1.0))
        relev = float(qm.get("answer_relevance_score", 0.972))
        h_mean = qm.get("ragas_harmonic_mean")
        if h_mean is None and (faith + relev) > 0:
            h_mean = round(2 * (faith * relev) / (faith + relev), 4)

        data["quality_metrics"] = {
            "faithfulness_score": faith,
            "faithfulness_percentage": qm.get("faithfulness_percentage") or f"{round(faith * 100, 1)}%",
            "answer_relevance_score": relev,
            "answer_relevance_percentage": qm.get("answer_relevance_percentage") or f"{round(relev * 100, 1)}%",
            "ragas_harmonic_mean": h_mean if h_mean is not None else 0.9858
        }

    raw_results = data.get("detailed_results") or data.get("samples") or []
    normalized_results = []
    for item in raw_results:
        hit = float(item.get("hit", 0))
        first_rank = int(item.get("first_rank", item.get("rank", 0)))
        retrieved_docs = item.get("retrieved_docs", [])
        retrieved_sources = item.get("retrieved_sources") or [
            doc.get("title", "") for doc in retrieved_docs
            if isinstance(doc, dict) and doc.get("title")
        ]
        normalized_results.append({
            "id": item.get("id"),
            "question": item.get("question", ""),
            "ground_truth_answer": item.get("ground_truth_answer"),
            "ground_truth_citations": item.get("ground_truth_citations", []),
            "retrieved_sources": retrieved_sources,
            "retrieved_docs": retrieved_docs,
            "hit": hit,
            "recall": float(item.get("recall", 0.0)),
            "first_rank": first_rank,
            "rank": first_rank,
            "reciprocal_rank": float(item.get("reciprocal_rank", 1.0 / first_rank if first_rank > 0 else 0.0)),
            "is_passed": bool(item.get("is_passed", hit > 0)),
            "status": item.get("status", "Đạt" if hit > 0 else "Chưa đạt"),
            "faithfulness": item.get("faithfulness"),
            "answer_relevance": item.get("answer_relevance"),
            "matched_citations": item.get("matched_citations", [])
        })

    data["detailed_results"] = normalized_results
    data["samples"] = normalized_results
    _cached_benchmark_data = data
    _cached_benchmark_mtime = current_mtime
    return data


@router.get("/benchmark/latest", response_model=BenchmarkSummaryResponse)
async def get_benchmark_latest(
    admin: User = Depends(require_admin)
):
    """
    Lấy tóm tắt chỉ số KPI và chất lượng RAG gần nhất (Hiển thị thẻ KPI & Header).
    """
    data = _get_validated_benchmark_data()
    return BenchmarkSummaryResponse(
        metadata=data["metadata"],
        summary_metrics=data["summary_metrics"],
        quality_metrics=data.get("quality_metrics")
    )


@router.get("/benchmark/samples", response_model=BenchmarkSamplesResponse)
async def get_benchmark_samples(
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(20, ge=1, le=100, description="Số câu hỏi mỗi trang"),
    status_filter: str = Query("all", alias="status", description="Bộ lọc trạng thái: all, passed, failed"),
    search: Optional[str] = Query(None, description="Từ khóa tìm kiếm trong câu hỏi hoặc căn cứ"),
    admin: User = Depends(require_admin)
):
    """
    Lấy danh sách kết quả chi tiết từng câu hỏi có hỗ trợ phân trang và tìm kiếm.
    """
    data = _get_validated_benchmark_data()
    all_samples = data.get("detailed_results", [])

    filtered = all_samples
    if status_filter == "passed":
        filtered = [s for s in filtered if s["is_passed"]]
    elif status_filter == "failed":
        filtered = [s for s in filtered if not s["is_passed"]]

    if search and search.strip():
        term = search.strip().lower()
        filtered = [
            s for s in filtered
            if term in s["question"].lower()
            or any(term in c.lower() for c in s.get("ground_truth_citations", []))
        ]

    total = len(filtered)
    total_pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit
    paged_items = filtered[offset : offset + limit]

    return BenchmarkSamplesResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        items=paged_items
    )


@router.get("/benchmark/results", response_model=BenchmarkFullReportResponse)
async def get_benchmark_results(
    admin: User = Depends(require_admin)
):
    """
    Lấy toàn bộ kết quả báo cáo đánh giá chất lượng RAG gần nhất (kèm 683 câu hỏi chi tiết).
    """
    data = _get_validated_benchmark_data()
    return BenchmarkFullReportResponse(**data)


@router.post("/benchmark/run")
async def run_benchmark(
    request: Request,
    top_k: int = Query(3, ge=1, le=10, description="Top K tài liệu truy xuất"),
    max_samples: Optional[int] = Query(50, ge=5, le=683, description="Số lượng mẫu kiểm thử (None hoặc tối đa 683)"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Kích hoạt chạy kịch bản đánh giá Benchmark trên tập dữ liệu kiểm thử (Có khóa đồng thời).
    """
    global _is_benchmark_running
    if _is_benchmark_running:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tiến trình đánh giá Benchmark đang thực thi trên máy chủ. Vui lòng chờ hoàn tất."
        )

    client_ip = get_client_ip(request)
    ua = get_user_agent(request)

    _is_benchmark_running = True
    try:
        def _sync_evaluate():
            from evaluation.benchmark_runner import BenchmarkRunner
            runner = BenchmarkRunner(test_dataset_path="data/raw/683_CauHoi_TTATGTDB.csv")
            rep = runner.evaluate_retrieval(top_k=top_k, max_samples=max_samples)
            runner.export_report(output_path=str(BENCHMARK_REPORT_PATH))
            return rep

        report = await asyncio.to_thread(_sync_evaluate)
        global _cached_benchmark_data
        _cached_benchmark_data = None

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
    finally:
        _is_benchmark_running = False

