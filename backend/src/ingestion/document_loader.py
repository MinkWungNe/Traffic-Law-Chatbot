"""
Module: document_loader.py
Mục đích: Đọc và trích xuất nội dung văn bản từ các tệp thô trong data/raw/ (.docx, .pdf, .xlsx).
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead)
"""

from typing import List, Dict, Any
import os

class DocumentLoader:
    """
    Lớp chịu trách nhiệm tải và đọc nội dung văn bản pháp luật từ thư mục lưu trữ dữ liệu thô.
    """

    def __init__(self, raw_data_dir: str = "data/raw"):
        """
        Khởi tạo DocumentLoader.
        Args:
            raw_data_dir (str): Đường dẫn tới thư mục chứa dữ liệu thô.
        """
        self.raw_data_dir = raw_data_dir

    def load_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Đọc nội dung từ tệp Word (.docx).
        Args:
            file_path (str): Đường dẫn tệp .docx cần đọc.
        Returns:
            Dict[str, Any]: Gồm 'file_name', 'content', 'metadata'.
        """
        # TODO [Cơ bản]: Sử dụng thư viện docx (python-docx) để đọc toàn bộ paragraphs
        return {
            "file_name": os.path.basename(file_path),
            "content": "",
            "metadata": {"type": "docx", "path": file_path}
        }

    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Đọc nội dung từ tệp PDF (.pdf).
        Args:
            file_path (str): Đường dẫn tệp .pdf cần đọc.
        Returns:
            Dict[str, Any]: Gồm 'file_name', 'content', 'metadata'.
        """
        # TODO [Cơ bản]: Sử dụng pypdf hoặc pdfplumber để trích xuất văn bản từng trang
        return {
            "file_name": os.path.basename(file_path),
            "content": "",
            "metadata": {"type": "pdf", "path": file_path}
        }

    def load_all_raw_documents(self) -> List[Dict[str, Any]]:
        """
        Quét và đọc tất cả văn bản có trong thư mục data/raw/.
        Returns:
            List[Dict[str, Any]]: Danh sách toàn bộ tài liệu đã trích xuất.
        """
        documents = []
        # TODO [Cơ bản]: Duyệt qua self.raw_data_dir và gọi load_docx/load_pdf tương ứng
        return documents
