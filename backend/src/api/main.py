"""
Module: main.py
Mục đích: Điểm khởi chạy chính của máy chủ FastAPI, cấu hình CORS, xử lý ngoại lệ và nạp các router.
Người phụ trách chính: Thành viên 3 (Backend API Lead)
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .routes.chat_routes import router as chat_router

# Thiết lập hệ thống ghi nhật ký (Logging) chuẩn hóa
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api.main")

app = FastAPI(
    title="API Chatbot AI Tư Vấn Luật An Toàn Giao Thông",
    description="Hệ thống cung cấp dịch vụ hỏi đáp RAG và tra cứu căn cứ pháp lý trên nền tảng pháp luật giao thông Việt Nam.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS để Web Frontend (Next.js) và các dịch vụ bên ngoài kết nối thông suốt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bắt lỗi dữ liệu đầu vào (Validation Error) và chuẩn hóa thông báo tiếng Việt
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": exc.errors(),
            "message": "Dữ liệu yêu cầu gửi lên không hợp lệ. Vui lòng kiểm tra lại cấu trúc tham số."
        }
    )

# Đăng ký các Router
app.include_router(chat_router)

@app.get("/", tags=["General"])
def root():
    """
    Điểm truy cập gốc (Root Endpoint) cung cấp thông tin hệ thống và tài liệu API.
    """
    return {
        "title": "API Chatbot AI An Toàn Giao Thông",
        "version": "1.0.0",
        "message": "Chào mừng bạn đến với hệ thống API Tư vấn Pháp luật Giao thông Đường bộ Việt Nam.",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "search": "/api/search",
            "documents": "/api/documents",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)
