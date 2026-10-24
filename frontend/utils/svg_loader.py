"""Tiện ích nạp và tùy biến mã nguồn tệp SVG từ thư mục frontend/assets/."""

import re
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
DEFAULT_COLOR = "#000000"


def load_svg(filename: str, color: str | None = None, class_name: str = "") -> str:
    """Nạp tệp SVG từ assets và đè màu fill (mặc định đen tuyền).

    Args:
        filename: Tên tệp SVG (vd: 'Chatbot_Logo.svg', 'CarCrash.svg').
        color: Mã màu fill hex (vd: '#FFFFFF'). Mặc định '#000000' nếu để trống.
        class_name: Class CSS bổ sung cho thẻ <svg>.

    Returns:
        Chuỗi SVG hoàn chỉnh, hoặc chuỗi rỗng "" nếu không tìm thấy tệp.
    """
    if not filename or not isinstance(filename, str):
        return ""

    name_clean = filename.strip()
    if not name_clean.endswith(".svg"):
        name_clean = f"{name_clean}.svg"

    target_file = (ASSETS_DIR / name_clean).resolve()

    # 1. Chống Path Traversal & Kiểm tra tệp tồn tại
    try:
        if not target_file.is_relative_to(ASSETS_DIR.resolve()) or not target_file.is_file():
            return ""
    except AttributeError:
        if ASSETS_DIR.resolve() not in target_file.parents or not target_file.is_file():
            return ""

    # 2. Đọc tệp SVG
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            svg_content = f.read()
    except Exception:
        return ""

    # 3. Bỏ header XML
    svg_content = re.sub(r'<\?xml[^>]*\?>', '', svg_content).strip()

    # 4. Gán màu fill (mặc định đen tuyền nếu không truyền hoặc rỗng)
    fill_color = color.strip() if color and color.strip() else DEFAULT_COLOR
    svg_content = re.sub(r'fill:\s*[^;]+;', f'fill: {fill_color};', svg_content)
    svg_content = re.sub(r'fill="[^"]+"', f'fill="{fill_color}"', svg_content)

    # 5. Co giãn 100% theo container bọc ngoài
    if '<svg' in svg_content:
        if 'width=' not in svg_content:
            svg_content = re.sub(r'<svg\b', '<svg width="100%"', svg_content, count=1)
        if 'height=' not in svg_content:
            svg_content = re.sub(r'<svg\b', '<svg height="100%"', svg_content, count=1)
        if class_name:
            svg_content = re.sub(r'<svg\b', f'<svg class="{class_name}"', svg_content, count=1)

    return svg_content
