"""
Script: run.py
Mục đích: Bộ khởi chạy hệ thống Chatbot AI Tư Vấn Pháp Luật An Toàn Giao Thông.
Hỗ trợ kiểm thử và tương tác trực tiếp trên Terminal bằng Node.js thay thế Streamlit cũ.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Kích hoạt hỗ trợ ANSI màu sắc trên Windows Console
os.system("")

# Đường dẫn thư mục gốc của dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Định nghĩa bảng màu trực quan
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def find_python_interpreter() -> tuple[Path, str]:
    """
    Tự động phát hiện môi trường ảo (venv hoặc .venv).
    Trả về đường dẫn tới python executable và tên môi trường ảo.
    """
    # 1. Kiểm tra môi trường ảo đang được kích hoạt sẵn
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        name = "venv" if "venv" in sys.prefix.lower() else "active-env"
        return Path(sys.executable), name

    # 2. Kiểm tra thư mục venv hoặc .venv cục bộ
    candidates = [
        (PROJECT_ROOT / "venv" / "Scripts" / "python.exe", "venv"),
        (PROJECT_ROOT / ".venv" / "Scripts" / "python.exe", ".venv"),
        (PROJECT_ROOT / "venv" / "bin" / "python", "venv"),
        (PROJECT_ROOT / ".venv" / "bin" / "python", ".venv"),
    ]

    for py_path, env_name in candidates:
        if py_path.exists():
            return py_path, env_name

    # 3. Fallback dùng Python hệ thống hiện hành
    return Path(sys.executable), "System Python"


def print_banner(venv_name: str):
    """In giao diện tiêu đề và menu lựa chọn."""
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{YELLOW}          🚦 CHATBOT AI TƯ VẤN PHÁP LUẬT AN TOÀN GIAO THÔNG 🚦{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{GREEN}  [!] Môi trường ảo Python:{RESET} {BOLD}[{venv_name}]{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")
    print(f"  {BOLD}[1]{RESET} {GREEN}Khởi chạy TOÀN BỘ hệ thống{RESET} (FastAPI Backend + Node.js Terminal Chat)")
    print(f"  {BOLD}[2]{RESET} Chạy {CYAN}TERMINAL CHATBOT{RESET} (Giao diện dòng lệnh Node.js CLI)")
    print(f"  {BOLD}[3]{RESET} Chạy {BLUE}MÁY CHỦ API{RESET} (FastAPI Backend trên port 8000)")
    print(f"  {BOLD}[4]{RESET} Chạy {YELLOW}KIỂM THỬ ĐÁNH GIÁ BENCHMARK{RESET} (683 câu trên Terminal)")
    print(f"  {BOLD}[5]{RESET} Chạy {CYAN}BỘ UNIT TEST TỰ ĐỘNG{RESET} (Kiểm tra toàn diện trên Terminal)")
    print(f"  {BOLD}[0]{RESET} {GRAY}Thoát{RESET}\n")
    print(f"{CYAN}{'='*80}{RESET}")


def run_fullstack(py_exe: Path):
    """Khởi chạy cả FastAPI Backend và Node.js Terminal Chat."""
    print(f"\n{YELLOW}{'='*80}{RESET}")
    print(f"{BOLD}Đang khởi động FastAPI Backend trên port 8000...{RESET}")
    print(f"{YELLOW}{'='*80}{RESET}")

    # Trên Windows, khởi chạy Backend ở một cửa sổ console riêng biệt
    creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    backend_proc = subprocess.Popen(
        [str(py_exe), "-m", "uvicorn", "backend.src.api.main:app", "--reload", "--port", "8000"],
        cwd=str(PROJECT_ROOT),
        creationflags=creation_flags
    )

    print(f"{GRAY}Đang chờ Backend khởi tạo trong 2 giây...{RESET}")
    time.sleep(2)

    try:
        subprocess.run(["node", "evaluation/terminal_chat.js"], cwd=str(PROJECT_ROOT))
    except KeyboardInterrupt:
        pass
    finally:
        # Tự động dọn dẹp và tắt luôn tiến trình Backend khi tắt ứng dụng
        print(f"\n{YELLOW}Đang đóng toàn bộ hệ thống...{RESET}")
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
        print(f"{GREEN}Hệ thống đã dừng an toàn.{RESET}")


def run_terminal_chat():
    """Khởi chạy giao diện Terminal Chatbot bằng Node.js."""
    try:
        subprocess.run(["node", "evaluation/terminal_chat.js"], cwd=str(PROJECT_ROOT))
    except KeyboardInterrupt:
        pass


def run_backend(py_exe: Path):
    """Chỉ khởi chạy máy chủ FastAPI Backend."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}Đang khởi chạy FastAPI Backend trên cổng 8000...{RESET}")
    print(f"{CYAN}Tài liệu Swagger UI: http://localhost:8000/docs{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    try:
        subprocess.run(
            [str(py_exe), "-m", "uvicorn", "backend.src.api.main:app", "--reload", "--port", "8000"],
            cwd=str(PROJECT_ROOT)
        )
    except KeyboardInterrupt:
        pass
    print(f"\n{GREEN}Máy chủ Backend đã dừng.{RESET}")


def run_benchmark():
    """Chạy chương trình đo lường benchmark trên terminal."""
    try:
        subprocess.run(["node", "evaluation/benchmark.js"], cwd=str(PROJECT_ROOT))
    except KeyboardInterrupt:
        pass


def run_tests():
    """Chạy bộ kiểm thử tự động trên terminal."""
    try:
        subprocess.run(["node", "evaluation/test_terminal.js"], cwd=str(PROJECT_ROOT))
    except KeyboardInterrupt:
        pass


def main():
    py_exe, venv_name = find_python_interpreter()

    # Nếu đang chạy bằng python hệ thống nhưng có venv, tự động chuyển sang chạy bằng venv python
    current_exe = Path(sys.executable).resolve()
    if py_exe.exists() and current_exe != py_exe.resolve():
        os.execv(str(py_exe), [str(py_exe)] + sys.argv)

    while True:
        try:
            print_banner(venv_name)
            choice = input("Nhập lựa chọn của bạn [1/2/3/4/5 hoặc 0]: ").strip()

            if choice == "1":
                run_fullstack(py_exe)
                break
            elif choice == "2":
                run_terminal_chat()
                break
            elif choice == "3":
                run_backend(py_exe)
                break
            elif choice == "4":
                run_benchmark()
                input("\nNhấn Enter để quay lại menu...")
            elif choice == "5":
                run_tests()
                input("\nNhấn Enter để quay lại menu...")
            elif choice == "0":
                print(f"\n{GRAY}Tạm biệt!{RESET}")
                break
            else:
                print(f"\n{RED}[!] Lựa chọn không hợp lệ, vui lòng thử lại!{RESET}")
                time.sleep(1.5)
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{GRAY}Đã thoát launcher.{RESET}")
            break


if __name__ == "__main__":
    main()
