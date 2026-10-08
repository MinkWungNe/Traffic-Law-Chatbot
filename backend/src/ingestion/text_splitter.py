"""
Module: text_splitter.py
Mục đích: Phân chia văn bản pháp luật thành các đoạn nhỏ (chunks) theo cấu trúc Điều/Khoản.
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead)
"""

from typing import List, Dict, Any

class LegalTextSplitter:
    """
    Lớp chia nhỏ văn bản pháp luật thành các đoạn thông tin phục vụ vector hóa.
    Đặc thù văn bản luật: Nên ưu tiên cắt theo 'Điều ...' hoặc 'Khoản ...' để giữ trọn vẹn ngữ nghĩa.
    """

    # Nghiên cứu chọn ra chunk-size phù hợp hơn
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        """
        Khởi tạo bộ chia văn bản.
        Args:
            chunk_size (int): Độ dài ký tự tối đa cho mỗi đoạn văn bản.
            chunk_overlap (int): Độ dài ký tự gối đầu giữa các đoạn liền kề.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_by_article(self, text: str, doc_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Cắt văn bản theo ranh giới từng 'Điều' (Ví dụ: Điều 1, Điều 2...).
        Args:
            text (str): Toàn bộ nội dung văn bản luật.
            doc_metadata (Dict[str, Any]): Thông tin về văn bản (tên luật, số hiệu).
        Returns:
            List[Dict[str, Any]]: Danh sách các chunks kèm metadata điều khoản.
        """
        chunks = []
        # TODO [Cơ bản]: Sử dụng regex nhận diện pattern r"Điều \d+\." để tách từng điều
        # Gán metadata gồm: 'article_number', 'law_name', 'chunk_text'
        return chunks

    def split_into_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Nhận danh sách tài liệu từ document_loader và phân mảnh toàn bộ.
        Args:
            documents (List[Dict[str, Any]]): Danh sách tài liệu thô.
        Returns:
            List[Dict[str, Any]]: Toàn bộ danh sách chunks đã chuẩn hóa.
        """
        all_chunks = []
        # TODO [Cơ bản]: Lặp qua từng tài liệu và gọi split_by_article
        return all_chunks
