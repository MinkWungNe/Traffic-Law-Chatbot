"""
Package: ingestion
Phân hệ nạp dữ liệu: Đọc file, cắt đoạn, nhúng vector và lưu vào ChromaDB.
"""
from .document_loader import DocumentLoader
from .text_splitter import LegalTextSplitter
from .vector_builder import VectorBuilder

__all__ = ["DocumentLoader", "LegalTextSplitter", "VectorBuilder"]
