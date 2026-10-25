"""
Module: text_cleaner.py
Mục đích: Cung cấp các hàm làm sạch ký tự, chuẩn hóa tiếng Việt và trích xuất số hiệu văn bản pháp lý.
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead) & Thành viên 3 (Backend API Lead)
"""

import re
import unicodedata
from typing import Optional, List


class TextCleaner:
    """
    Lớp tiện ích xử lý chuỗi văn bản pháp luật tiếng Việt.
    Cung cấp các hàm tĩnh (static methods) độc lập, an toàn khi xử lý đa luồng.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Làm sạch ký tự thừa, chuẩn hóa Unicode NFC tiếng Việt, chuẩn hóa dấu xuống dòng.
        Bảo toàn nguyên vẹn các ký hiệu toán học (<, >) và đơn vị đo lường trong luật.
        Args:
            text (str): Đoạn văn bản thô.
        Returns:
            str: Đoạn văn bản đã làm sạch.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Chuẩn hóa bảng mã Unicode tiếng Việt về chuẩn NFC (Dựng sẵn)
        text = unicodedata.normalize("NFC", text)

        # 2. Thay thế khoảng trắng không ngắt (\xa0) và ký tự ẩn (\u200b) thành dấu cách thường
        text = text.replace("\xa0", " ").replace("\u200b", " ")

        # 3. Chuẩn hóa dấu xuống dòng Windows/Mac cũ về \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 4. Thu gọn nhiều khoảng trắng liên tiếp trên cùng một dòng thành 1 dấu cách
        text = re.sub(r"[ \t]+", " ", text)

        # 5. Thu gọn các dòng trống liên tiếp thành tối đa 2 dấu xuống dòng
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text.strip()

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Khử trùng an toàn chuỗi văn bản đầu vào:
        - Loại bỏ mã script độc hại và các thẻ HTML chuẩn (<script>, <div>, <b>...).
        - Bảo toàn nguyên vẹn các biểu thức toán học (< 40 km/h, > 0.25 mg/l...).
        - Loại bỏ ký tự điều khiển nguy hiểm (null byte \x00).
        - Gọi clean_text để chuẩn hóa câu từ.
        Args:
            text (str): Chuỗi văn bản cần khử trùng.
        Returns:
            str: Chuỗi văn bản an toàn.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Loại bỏ toàn bộ khối script/style cùng nội dung bên trong nếu có
        text = re.sub(r"(?is)<script.*?>.*?</script>", "", text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", "", text)

        # 2. Xóa các thẻ HTML thực sự (bắt đầu bằng ký tự chữ cái), không xóa toán tử so sánh số học (< 40, > 20)
        text = re.sub(r"<\s*/?\s*[a-zA-Z][a-zA-Z0-9]*\b[^>]*>", "", text)

        # 3. Xóa ký tự null byte
        text = text.replace("\x00", "")

        # 4. Chuẩn hóa văn bản cuối cùng qua clean_text
        return TextCleaner.clean_text(text)

    @staticmethod
    def extract_article_number(text: str) -> Optional[int]:
        """
        Trích xuất số thứ tự của Điều luật (ví dụ: 'Điều 15. Quy tắc...' -> 15, 'Điều 43a...' -> 43).
        Hỗ trợ cả các điều luật sửa đổi bổ sung có hậu tố chữ cái.
        Args:
            text (str): Chuỗi tiêu đề hoặc nội dung điều luật.
        Returns:
            Optional[int]: Số thứ tự điều luật nếu tìm thấy, ngược lại trả về None.
        """
        if not text or not isinstance(text, str):
            return None

        # Bỏ \b phía sau (\d+) để nhận diện được các điều luật có hậu tố chữ cái (ví dụ: Điều 43a, Điều 12b)
        match = re.search(r"(?i)\bĐiều\s+(\d+)", text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_law_citations(text: str) -> List[str]:
        """
        Tìm kiếm các số hiệu văn bản pháp luật được nhắc đến trong đoạn (ví dụ: 168/2024/NĐ-CP, 36/2024/QH15).
        Bao quát: Nghị định (có dấu và không dấu), Thông tư mọi bộ ngành, Luật/Nghị quyết Quốc hội, VBHN.
        Loại bỏ trùng lặp và bảo toàn thứ tự xuất hiện.
        Args:
            text (str): Văn bản cần quét.
        Returns:
            List[str]: Danh sách số hiệu văn bản tìm thấy.
        """
        if not text or not isinstance(text, str):
            return []

        pattern = r"\b\d+/\d+/(?:N[ĐD]-CP|TT-[A-Z]+|QH\d+|VBHN-[A-Z]+)\b"
        matches = re.findall(pattern, text)

        # Loại bỏ trùng lặp nhưng giữ nguyên thứ tự xuất hiện
        return list(dict.fromkeys(matches))


if __name__ == "__main__":
    import sys

    # Cấu hình encoding UTF-8 để hiển thị tiếng Việt trên Terminal Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=== KIỂM THỬ THỰC TẾ MODULE TextCleaner ===")

    # 1. Thử nghiệm sanitize_text bảo vệ toán tử so sánh
    sample_text = (
        "Xử phạt nồng độ cồn < 0.25 mg/l hoặc vận tốc > 50 km/h. "
        "<b>Lưu ý:</b> Tra cứu theo Điều 15. <script>alert('hack');</script>"
    )
    sanitized = TextCleaner.sanitize_text(sample_text)
    print("1. Sanitize text kết quả:")
    print("  ->", repr(sanitized))

    # 2. Thử nghiệm extract_article_number
    art_num = TextCleaner.extract_article_number("Theo quy định tại Điều 30 Nghị định 168")
    print("2. Extract article number:")
    print("  ->", art_num)

    # 3. Thử nghiệm extract_law_citations
    sample_citation = (
        "Căn cứ Nghị định 168/2024/ND-CP, Thông tư 38/2024/TT-BGTVT và Luật 36/2024/QH15."
    )
    citations = TextCleaner.extract_law_citations(sample_citation)
    print("3. Extract law citations:")
    print("  ->", citations)
