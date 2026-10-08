"""
Module: text_cleaner.py
Mục đích: Cung cấp các hàm làm sạch ký tự, chuẩn hóa tiếng Việt và trích xuất số hiệu văn bản pháp lý.
Người phụ trách chính: Thành viên 1 & Thành viên 3
"""

import re
from typing import Optional, List

class TextCleaner:
    """
    Lớp tiện ích xử lý chuỗi văn bản pháp luật tiếng Việt.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Làm sạch ký tự thừa, khoảng trắng thừa, chuẩn hóa dấu xuống dòng.
        Args:
            text (str): Đoạn văn bản thô.
        Returns:
            str: Đoạn văn bản đã làm sạch.
        """
        if not text:
            return ""
        # Xóa nhiều khoảng trắng liên tiếp
        text = re.sub(r"[ \t]+", " ", text)
        # Xóa các dòng trống liên tiếp
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()

    @staticmethod
    def extract_article_number(text: str) -> Optional[int]:
        """
        Trích xuất số thứ tự của Điều luật (ví dụ: 'Điều 15. Quy tắc...' -> 15).
        Args:
            text (str): Chuỗi tiêu đề điều luật.
        Returns:
            Optional[int]: Số thứ tự điều luật nếu tìm thấy.
        """
        match = re.search(r"Điều\s+(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def extract_law_citations(text: str) -> List[str]:
        """
        Tìm kiếm các số hiệu văn bản pháp luật được nhắc đến trong đoạn (ví dụ: 100/2019/NĐ-CP).
        Args:
            text (str): Văn bản cần quét.
        Returns:
            List[str]: Danh sách số hiệu văn bản tìm thấy.
        """
        pattern = r"\b\d+/\d+/(?:NĐ-CP|TT-BCA|QH\d+|VBHN-[A-Z]+)\b"
        return re.findall(pattern, text)
