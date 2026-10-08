"""
Package: routes
Chứa các bộ định tuyến API Endpoints của FastAPI.
"""
from .chat_routes import router as chat_router

__all__ = ["chat_router"]
