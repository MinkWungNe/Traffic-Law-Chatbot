"""
Script: run.py
Mục đích: Bộ khởi chạy hệ thống Chatbot AI Tư Vấn Pháp Luật An Toàn Giao Thông.
Khởi chạy đồng bộ FastAPI Backend (port 8000) và Next.js Frontend (port 3000).
Hỗ trợ đa nền tảng (Windows/Linux/macOS) với trải nghiệm mượt mà.
"""

import os
import sys
import time
import shutil
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


def get_frontend_dir() -> Path:
    """
    Tự động định vị thư mục frontend:
    Ưu tiên frontend, hỗ trợ cả trường hợp người dùng để tên frontend-next.
    """
    candidates = [
        PROJECT_ROOT / "frontend",
        PROJECT_ROOT / "frontend-next",
    ]
    for d in candidates:
        if (d / "package.json").exists():
            return d
    return PROJECT_ROOT / "frontend"


def find_npm_executable() -> str | None:
    """Tự động phát hiện npm executable trên Windows, Linux và macOS."""
    return shutil.which("npm.cmd") or shutil.which("npm")


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


def ensure_node_modules(npm_cmd: str, frontend_dir: Path):
    """Tự động cài đặt node_modules nếu người dùng chưa chạy npm install."""
    if not (frontend_dir / "node_modules").exists():
        print(f"\n{YELLOW}[!] Chưa tìm thấy 'node_modules'. Đang tự động cài đặt thư viện frontend...{RESET}")
        try:
            subprocess.run([npm_cmd, "install"], cwd=str(frontend_dir), check=True)
            print(f"{GREEN}[✓] Cài đặt dependencies frontend thành công.{RESET}\n")
        except Exception as e:
            print(f"{RED}[!] Lỗi khi chạy npm install: {e}{RESET}")


def print_banner(venv_name: str):
    """In giao diện tiêu đề và menu lựa chọn."""
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{YELLOW}          🚦 CHATBOT AI TƯ VẤN PHÁP LUẬT AN TOÀN GIAO THÔNG 🚦{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{GREEN}  [!] Môi trường Python:{RESET} {BOLD}[{venv_name}]{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")
    print(f"  {BOLD}[1]{RESET} {GREEN}Khởi chạy TOÀN BỘ hệ thống{RESET} (FastAPI Backend :8000 + Next.js UI :3000)")
    print(f"  {BOLD}[2]{RESET} Chỉ chạy {CYAN}GIAO DIỆN WEB{RESET} (Next.js Frontend trên port 3000)")
    print(f"  {BOLD}[3]{RESET} Chỉ chạy {BLUE}MÁY CHỦ API{RESET} (FastAPI Backend trên port 8000)")
    print(f"  {BOLD}[0]{RESET} {GRAY}Thoát{RESET}\n")
    print(f"{CYAN}{'='*80}{RESET}")


def run_fullstack(py_exe: Path, npm_cmd: str, frontend_dir: Path):
    """Khởi chạy cả FastAPI Backend và Next.js Frontend."""
    ensure_node_modules(npm_cmd, frontend_dir)

    print(f"\n{YELLOW}{'='*80}{RESET}")
    print(f"{BOLD}Đang khởi động FastAPI Backend trên port 8000...{RESET}")
    print(f"{CYAN}Tài liệu Swagger UI: http://localhost:8000/docs{RESET}")
    print(f"{YELLOW}{'='*80}{RESET}")

    # Trên Windows, khởi chạy Backend ở một cửa sổ console riêng biệt
    creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    backend_proc = subprocess.Popen(
        [str(py_exe), "-m", "uvicorn", "backend.src.api.main:app", "--reload", "--port", "8000"],
        cwd=str(PROJECT_ROOT),
        creationflags=creation_flags
    )

    print(f"{GRAY}Đang chờ Backend ổn định trong 2 giây...{RESET}")
    time.sleep(2)

    print(f"\n{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}Đang khởi động Next.js Web UI trên port 3000...{RESET}")
    print(f"{CYAN}Truy cập giao diện tại: http://localhost:3000{RESET}")
    print(f"{GREEN}{'='*80}{RESET}\n")

    try:
        subprocess.run(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir)
        )
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


def run_frontend(npm_cmd: str, frontend_dir: Path):
    """Chỉ khởi chạy giao diện Web Next.js."""
    ensure_node_modules(npm_cmd, frontend_dir)

    print(f"\n{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}Đang khởi chạy Next.js Web UI (Chế độ độc lập)...{RESET}")
    print(f"{CYAN}Truy cập giao diện tại: http://localhost:3000{RESET}")
    print(f"{GREEN}{'='*80}{RESET}\n")
    try:
        subprocess.run(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir)
        )
    except KeyboardInterrupt:
        pass
    print(f"\n{GREEN}Giao diện Web đã dừng.{RESET}")


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


def main():
    py_exe, venv_name = find_python_interpreter()
    npm_cmd = find_npm_executable()
    frontend_dir = get_frontend_dir()

    if not npm_cmd:
        print(f"\n{RED}[!] CẢNH BÁO: Không tìm thấy 'npm' trong biến môi trường PATH!{RESET}")
        print(f"{YELLOW}Vui lòng cài đặt Node.js (phiên bản khuyến nghị >= 18.x hoặc 20.x) để chạy giao diện Next.js.{RESET}")
        print(f"{GRAY}Bạn có thể tải Node.js tại: https://nodejs.org/{RESET}\n")
        input("Nhấn Enter để tiếp tục (chỉ có thể chọn chạy Backend)...")

    # Nếu đang chạy bằng python hệ thống nhưng có venv, tự động chuyển sang chạy bằng venv python
    current_exe = Path(sys.executable).resolve()
    if py_exe.exists() and current_exe != py_exe.resolve():
        os.execv(str(py_exe), [str(py_exe)] + sys.argv)

    while True:
        try:
            print_banner(venv_name)
            choice = input("Nhập lựa chọn của bạn [1/2/3 hoặc 0]: ").strip()

            if choice == "1":
                if not npm_cmd:
                    print(f"\n{RED}[!] Không thể khởi chạy giao diện vì thiếu npm/Node.js!{RESET}")
                    time.sleep(2)
                    continue
                run_fullstack(py_exe, npm_cmd, frontend_dir)
                break
            elif choice == "2":
                if not npm_cmd:
                    print(f"\n{RED}[!] Không thể khởi chạy giao diện vì thiếu npm/Node.js!{RESET}")
                    time.sleep(2)
                    continue
                run_frontend(npm_cmd, frontend_dir)
                break
            elif choice == "3":
                run_backend(py_exe)
                break
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
