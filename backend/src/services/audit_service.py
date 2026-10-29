"""
Module: audit_service.py
Mục đích: Cung cấp hàm ghi nhận nhật ký kiểm toán (Audit Log) bất đồng bộ vào CSDL.
Ghi lại các sự kiện an ninh, đăng nhập và tác vụ quản trị của Admin.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import AuditLog

logger = logging.getLogger("services.audit")


async def log_audit_event(
    db: AsyncSession,
    action: str,
    actor_email: str,
    actor_id: Optional[uuid.UUID] = None,
    target_id: Optional[uuid.UUID] = None,
    target_email: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Ghi một bản ghi nhật ký kiểm toán vào bảng audit_logs.
    Hàm được bọc trong try/except để nếu ghi log gặp sự cố thì không làm gián đoạn luồng chính.
    """
    try:
        log_entry = AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            target_id=target_id,
            target_email=target_email,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry
    except Exception as e:
        logger.error(f"Lỗi khi ghi Audit Log ({action}): {e}")
        # Không re-raise để tránh rollback transaction chính nếu lỗi chỉ ở phần log
        return None
