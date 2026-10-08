"""
Module: main.py
Mục đích: Điểm khởi chạy chính của máy chủ FastAPI, cấu hình CORS và nạp các router.
Người phụ trách chính: Thành viên 3 (Backend API Lead)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.chat_routes import router as chat_router

app = FastAPI(
    title="API Chatbot AI Tư Vấn Luật An Toàn Giao Thông",
    description="Hệ thống cung cấp dịch vụ hỏi đáp RAG trên nền tảng pháp luật giao thông Việt Nam.",
    version="1.0.0"
)

# Cấu hình CORS để Streamlit Frontend kết nối thông suốt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "message": "Chào mừng đến với API Chatbot AI An toàn Giao thông",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)
