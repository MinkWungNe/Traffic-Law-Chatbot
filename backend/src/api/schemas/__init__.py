"""
Package: schemas
Chứa các Pydantic Models định chuẩn Request và Response cho API.
"""
from .chat_schema import (
    ChatRequest,
    ChatResponse,
    SourceDocument,
    HealthResponse,
    SearchRequest,
    SearchResponse,
    LegalDocItem,
    LegalDocsListResponse,
)

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "SourceDocument",
    "HealthResponse",
    "SearchRequest",
    "SearchResponse",
    "LegalDocItem",
    "LegalDocsListResponse",
]
