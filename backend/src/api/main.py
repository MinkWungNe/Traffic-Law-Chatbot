"""
Module: main.py
Mục đích: Điểm khởi chạy chính của máy chủ FastAPI, cấu hình CORS, xử lý ngoại lệ,
quản lý Lifespan (khởi tạo CSDL và gieo mầm Super Admin) và nạp toàn bộ các Router.
"""

import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select

from ..db.database import init_db, AsyncSessionLocal
from ..db.models import User
from ..services.crypto_service import hash_password
from .routes.chat_routes import router as chat_router
from .routes.auth_routes import router as auth_router
from .routes.session_routes import router as session_router
from .routes.admin_routes import router as admin_router

load_dotenv()

# Thiết lập hệ thống ghi nhật ký (Logging) chuẩn hóa
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api.main")


async def seed_super_admin():
    """
    Tự động kiểm tra và khởi tạo tài khoản Super Admin từ .env nếu chưa có admin nào trong CSDL.
    """
    admin_email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@vinalaw.vn").strip().lower()
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin@2026").strip()

    if not admin_email or not admin_password:
        return

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.role == "admin", User.deleted_at.is_(None))
            )
            admin_user = result.scalar_one_or_none()
            if not admin_user:
                logger.info(f"Chưa có tài khoản Quản trị viên. Đang tự động khởi tạo Super Admin: {admin_email}...")
                new_admin = User(
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    role="admin",
                    is_active=True
                )
                session.add(new_admin)
                await session.commit()
                logger.info(f"Đã khởi tạo thành công tài khoản Super Admin: {admin_email}")
            else:
                logger.info("Tài khoản Quản trị viên đã tồn tại, bỏ qua bước khởi tạo.")
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra/khởi tạo Super Admin: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời máy chủ FastAPI: Tự động khởi tạo bảng CSDL và seed tài khoản Admin.
    """
    logger.info("=== Đang khởi động hệ thống Backend FastAPI ===")
    try:
        await init_db()
        await seed_super_admin()
    except Exception as e:
        logger.error(f"Lỗi trong quá trình khởi tạo ứng dụng: {e}", exc_info=True)
    yield
    logger.info("=== Đang tắt máy chủ Backend FastAPI ===")


app = FastAPI(
    title="API Chatbot AI Tư Vấn Luật An Toàn Giao Thông",
    description="Hệ thống cung cấp dịch vụ hỏi đáp RAG, quản lý tài khoản, phân quyền Admin và lưu trữ lịch sử mã hóa AES-256-GCM.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Cấu hình CORS cho Next.js Frontend và các client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Bắt lỗi dữ liệu đầu vào và định dạng phản hồi tiếng Việt."""
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": exc.errors(),
            "message": "Dữ liệu yêu cầu gửi lên không hợp lệ. Vui lòng kiểm tra lại cấu trúc tham số."
        }
    )


# Đăng ký các Router phân hệ
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(admin_router)
app.include_router(chat_router)


@app.get("/", tags=["General"])
def root():
    """
    Điểm truy cập gốc (Root Endpoint) cung cấp danh mục endpoints.
    """
    return {
        "title": "API Chatbot AI An Toàn Giao Thông",
        "version": "2.0.0",
        "message": "Hệ thống API VinaLaw-Traffic v2.0 sẵn sàng phục vụ.",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "me": "/api/auth/me",
                "change_password": "/api/auth/change-password"
            },
            "sessions": {
                "list": "/api/sessions",
                "create": "/api/sessions",
                "detail": "/api/sessions/{session_id}",
                "update": "/api/sessions/{session_id}",
                "delete": "/api/sessions/{session_id}"
            },
            "admin": {
                "users": "/api/admin/users",
                "status": "/api/admin/users/{user_id}/status",
                "reset_password": "/api/admin/users/{user_id}/reset-password",
                "delete_user": "/api/admin/users/{user_id}",
                "audit_logs": "/api/admin/audit-logs"
            },
            "chat": {
                "chat": "/api/chat",
                "health": "/api/health",
                "search": "/api/search",
                "documents": "/api/documents"
            },
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)
