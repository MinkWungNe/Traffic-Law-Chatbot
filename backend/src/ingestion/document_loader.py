"""
Module: document_loader.py
Mục đích: Đọc và trích xuất nội dung văn bản từ các tệp thô trong data/raw/ (.docx, .pdf).
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead)
"""

from typing import List, Dict, Any
import logging
from pathlib import Path
import docx
from pypdf import PdfReader

try:
    from backend.src.utils.text_cleaner import TextCleaner
except ModuleNotFoundError:
    import sys
    project_root = str(Path(__file__).resolve().parents[3])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from backend.src.utils.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Lớp chịu trách nhiệm tải và đọc nội dung văn bản pháp luật từ thư mục lưu trữ dữ liệu thô.
    """

    def __init__(self, raw_data_dir: str = "data/raw"):
        """
        Khởi tạo DocumentLoader.
        Tự động fallback tìm theo thư mục gốc dự án nếu chạy từ các thư mục con khác nhau.
        Args:
            raw_data_dir (str): Đường dẫn tới thư mục chứa dữ liệu thô.
        """
        path = Path(raw_data_dir)
        if not path.exists():
            # Tự động dò tìm theo project root nếu relative path từ cwd không tồn tại
            project_root = Path(__file__).resolve().parents[3]
            candidate = project_root / raw_data_dir
            if candidate.exists():
                path = candidate
        self.raw_data_dir = path

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Chuẩn hóa nhẹ chuỗi ký tự thô bằng cách tái sử dụng TextCleaner.clean_text:
        - Chuẩn hóa Unicode NFC tiếng Việt.
        - Khử khoảng trắng không ngắt (\xa0) và ký tự ẩn (\u200b).
        - Chuẩn hóa xuống dòng và thu gọn khoảng trắng thừa.
        """
        return TextCleaner.clean_text(text)

    def load_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Đọc nội dung từ tệp Word (.docx).
        Args:
            file_path (str): Đường dẫn tệp .docx cần đọc.
        Returns:
            Dict[str, Any]: Gồm 'file_name', 'content', 'metadata'.
        """
        path_obj = Path(file_path)
        try:
            doc = docx.Document(str(path_obj))
            paragraphs = []
            for p in doc.paragraphs:
                cleaned = self._sanitize_text(p.text)
                if cleaned:
                    paragraphs.append(cleaned)

            content = "\n".join(paragraphs)
            return {
                "file_name": path_obj.name,
                "content": content,
                "metadata": {
                    "file_name": path_obj.name,
                    "file_type": "docx",
                    "file_path": str(path_obj.resolve())
                }
            }
        except Exception as e:
            logger.error(f"Lỗi khi đọc file docx '{file_path}': {e}")
            return {
                "file_name": path_obj.name,
                "content": "",
                "metadata": {
                    "file_name": path_obj.name,
                    "file_type": "docx",
                    "file_path": str(path_obj.resolve()),
                    "error": str(e)
                }
            }

    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Đọc nội dung từ tệp PDF (.pdf).
        Args:
            file_path (str): Đường dẫn tệp .pdf cần đọc.
        Returns:
            Dict[str, Any]: Gồm 'file_name', 'content', 'metadata'.
        """
        path_obj = Path(file_path)
        try:
            reader = PdfReader(str(path_obj))
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    cleaned = self._sanitize_text(text)
                    if cleaned:
                        pages_text.append(cleaned)

            content = "\n\n".join(pages_text)
            return {
                "file_name": path_obj.name,
                "content": content,
                "metadata": {
                    "file_name": path_obj.name,
                    "file_type": "pdf",
                    "file_path": str(path_obj.resolve()),
                    "total_pages": len(reader.pages)
                }
            }
        except Exception as e:
            logger.error(f"Lỗi khi đọc file pdf '{file_path}': {e}")
            return {
                "file_name": path_obj.name,
                "content": "",
                "metadata": {
                    "file_name": path_obj.name,
                    "file_type": "pdf",
                    "file_path": str(path_obj.resolve()),
                    "error": str(e)
                }
            }

    def load_all_raw_documents(self) -> List[Dict[str, Any]]:
        """
        Quét và đọc tất cả văn bản có trong thư mục data/raw/.
        Returns:
            List[Dict[str, Any]]: Danh sách toàn bộ tài liệu đã trích xuất.
        """
        documents = []
        if not self.raw_data_dir.exists():
            logger.warning(f"Thư mục dữ liệu thô không tồn tại: {self.raw_data_dir}")
            return documents

        supported_extensions = {".docx", ".pdf"}

        # Duyệt qua các file và sắp xếp theo tên để đảm bảo tính nhất quán
        file_paths = sorted(self.raw_data_dir.iterdir(), key=lambda p: p.name)

        for file_path in file_paths:
            # Bỏ qua thư mục con hoặc file tạm thời của MS Office (~$...)
            if not file_path.is_file() or file_path.name.startswith("~$"):
                continue

            # Bỏ qua các định dạng không nằm trong whitelist (.csv, .xlsx, .md...)
            suffix = file_path.suffix.lower()
            if suffix not in supported_extensions:
                continue

            doc_data = None
            if suffix == ".docx":
                doc_data = self.load_docx(str(file_path))
            elif suffix == ".pdf":
                doc_data = self.load_pdf(str(file_path))

            # Nguyên lý phòng thủ: Chỉ giữ lại tài liệu có nội dung hợp lệ
            if doc_data and doc_data.get("content", "").strip():
                documents.append(doc_data)
            else:
                logger.warning(f"Bỏ qua file rỗng hoặc đọc thất bại: {file_path.name}")

        logger.info(f"Đã nạp thành công {len(documents)} tài liệu từ '{self.raw_data_dir}'")
        return documents

"""
if __name__ == "__main__":
    import sys

    # Cấu hình encoding UTF-8 để hiển thị tiếng Việt mượt mà trên Terminal Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    loader = DocumentLoader("data/raw")
    sample_file = "data/raw/2.3_AnNinhTratTu_282.2025.ND.CP.docx"

    print(f"--- ĐANG CHẠY THỬ NGHIỆM ĐỌC FILE WORD: {sample_file} ---")
    doc_result = loader.load_docx(sample_file)

    print(f"✔ Tên file      : {doc_result['file_name']}")
    print(f"✔ Metadata      : {doc_result['metadata']}")
    print(f"✔ Tổng số ký tự : {len(doc_result['content']):,} ký tự")
    print(f"✔ Trích 200 ký tự đầu:")
    print("-" * 60)
    print(doc_result["content"][:200])
    print("-" * 60)
"""
