"""Tiện ích nạp và mã hóa Base64 an toàn cho tệp hình ảnh từ frontend/assets/."""

import base64
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
    ".ico": "image/x-icon",
}


def load_image(filename: str, as_data_url: bool = True) -> str:
    """Nạp tệp hình ảnh từ assets và mã hóa Base64 Data URL.

    Args:
        filename: Tên tệp đầy đủ kèm phần mở rộng (vd: 'LoginBackGround.jpg').
        as_data_url: Trả về dạng Data URL 'data:...;base64,...' nếu True, ngược lại chỉ trả Base64.

    Returns:
        Chuỗi Base64 Data URL, hoặc chuỗi rỗng "" nếu tệp không tồn tại hoặc không an toàn.
    """
    if not filename or not isinstance(filename, str):
        return ""

    filename_clean = filename.strip()
    target_file = (ASSETS_DIR / filename_clean).resolve()

    # 1. Kiểm tra an toàn: Chống lỗ hổng Path Traversal (Directory Traversal - ví dụ '../../evil.png')
    try:
        if not target_file.is_relative_to(ASSETS_DIR.resolve()):
            return ""
    except AttributeError:
        if ASSETS_DIR.resolve() not in target_file.parents and target_file != ASSETS_DIR.resolve():
            return ""

    # 2. Kiểm tra tệp có thực sự tồn tại và là tệp tin hợp lệ không
    if not target_file.is_file():
        return ""

    # 3. Kiểm tra phần mở rộng có nằm trong danh sách định dạng được phép không
    ext = target_file.suffix.lower()
    if ext not in MIME_TYPES:
        return ""

    mime_type = MIME_TYPES[ext]

    # 4. Đọc dữ liệu nhị phân và mã hóa sang Base64
    try:
        with open(target_file, "rb") as f:
            file_bytes = f.read()

        b64_str = base64.b64encode(file_bytes).decode("utf-8")
        if as_data_url:
            return f"data:{mime_type};base64,{b64_str}"
        return b64_str
    except Exception:
        return ""
