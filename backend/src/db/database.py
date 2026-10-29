"""
Module: database.py
Mục đích: Thiết lập kết nối CSDL bất đồng bộ (Async SQLAlchemy 2.0), quản lý Session Pool
Mặc định sử dụng SQLite cục bộ (data/traffic_law.db) gọn nhẹ, không cần cài đặt phần mềm ngoài.
"""

import os
import logging
from pathlib import Path
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from .models import Base

logger = logging.getLogger("db.database")

load_dotenv()

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_normalized_database_url(raw_url: str) -> str:
    """
    Chuẩn hóa chuỗi kết nối CSDL để tương thích với SQLAlchemy Async Engine.
    Mặc định sử dụng SQLite cục bộ tại thư mục data/traffic_law.db.
    """
    # Nếu để trống hoặc vô tình dán URL web https:// của Supabase
    if not raw_url or raw_url.startswith("http://") or raw_url.startswith("https://"):
        db_dir = Path("data")
        db_dir.mkdir(parents=True, exist_ok=True)
        sqlite_path = db_dir / "traffic_law.db"
        logger.info(f"Sử dụng CSDL SQLite cục bộ: sqlite+aiosqlite:///{sqlite_path.as_posix()}")
        return f"sqlite+aiosqlite:///{sqlite_path.as_posix()}"

    # Supabase PostgreSQL URI
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return raw_url


DATABASE_URL = get_normalized_database_url(RAW_DATABASE_URL)

connect_args = {}
if "postgresql+asyncpg" in DATABASE_URL:
    connect_args["ssl"] = "require"

# Khởi tạo Async Engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args
)

# Kích hoạt ràng buộc khóa ngoại (Foreign Keys ON) cho SQLite
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db() -> None:
    """
    Khởi tạo cấu trúc các bảng trong CSDL nếu chưa tồn tại.
    """
    try:
        async with engine.begin() as conn:
            logger.info("Đang kiểm tra và khởi tạo bảng CSDL...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Khởi tạo cấu trúc bảng CSDL thành công.")
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo CSDL: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency: Cung cấp AsyncSession cho từng HTTP Request và tự động đóng kết nối.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
