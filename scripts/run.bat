@echo off
title Chatbot AI Tu Van Luat Giao Thong

:: 1. Chuyen ve thu muc goc cua du an (parent folder cua scripts)
cd /d "%~dp0\.."
set "PROJECT_ROOT=%CD%"

:: 2. Tu dong phat hien thu muc moi truong ao: venv hoac .venv
set "PYTHON_EXE="
set "VENV_NAME="

if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
    set "VENV_NAME=venv"
) else if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
    set "VENV_NAME=.venv"
) else (
    echo ================================================================================
    echo [ERROR] Khong tim thay moi truong ao - venv hoac .venv - tai thu muc du an!
    echo ================================================================================
    echo Vui long tao moi truong ao bang mot trong hai lenh sau:
    echo   python -m venv venv
    echo hoac:
    echo   python -m venv .venv
    echo Sau do cai dat thu vien: .\venv\Scripts\pip install -r requirements.txt
    echo ================================================================================
    pause
    exit /b 1
)

:MENU
cls
echo ================================================================================
echo               CHATBOT AI TU VAN PHAP LUAT AN TOAN GIAO THONG
echo ================================================================================
echo   [!] Da phat hien moi truong ao: [%VENV_NAME%]
echo ================================================================================
echo.
echo   [1] Khoi chay TOAN BO he thong (FastAPI Backend + Streamlit Web UI)
echo   [2] Chi chay GIAO DIEN WEB (Streamlit Frontend)
echo   [3] Chi chay MAY CHU API (FastAPI Backend tren port 8000)
echo   [0] Thoat
echo.
echo ================================================================================
set choice=
set /p choice="Nhap lua chon cua ban [1/2/3 hoac 0]: "

if "%choice%"=="1" goto RUN_ALL
if "%choice%"=="2" goto RUN_FRONTEND
if "%choice%"=="3" goto RUN_BACKEND
if "%choice%"=="0" goto EXIT_SCRIPT

echo [!] Lua chon khong hop le, vui long thu lai!
ping 127.0.0.1 -n 3 >nul
goto MENU

:RUN_ALL
cls
echo ================================================================================
echo Dang khoi dong FastAPI Backend tren port 8000 (Cua so rieng)...
echo ================================================================================
start "FastAPI Backend - Chatbot AI" cmd /k "cd /d "%PROJECT_ROOT%" && "%PYTHON_EXE%" -m uvicorn backend.src.api.main:app --reload --port 8000 <nul"

echo Dang cho Backend on dinh trong 2 giay...
ping 127.0.0.1 -n 3 >nul

echo ================================================================================
echo Dang khoi dong Streamlit Web UI tren port 8501...
echo ================================================================================
"%PYTHON_EXE%" -m streamlit run frontend/app.py <nul
goto EXIT_SCRIPT

:RUN_FRONTEND
cls
echo ================================================================================
echo Dang khoi chay Streamlit Web UI (Che do doc lap)...
echo ================================================================================
"%PYTHON_EXE%" -m streamlit run frontend/app.py <nul
goto EXIT_SCRIPT

:RUN_BACKEND
cls
echo ================================================================================
echo Dang khoi chay FastAPI Backend tren port 8000...
echo Tai lieu Swagger UI: http://localhost:8000/docs
echo ================================================================================
"%PYTHON_EXE%" -m uvicorn backend.src.api.main:app --reload --port 8000 <nul
goto EXIT_SCRIPT

:EXIT_SCRIPT
exit /b 0
