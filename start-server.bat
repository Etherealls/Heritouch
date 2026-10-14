@echo off
chcp 65001 >nul
title 指尖非遗 - 后端服务 (端口 5757)

echo ============================================
echo   指尖非遗 - 后端服务启动器
echo ============================================
echo.

rem 切换到后端目录（批处理文件位于项目根目录）
cd /d "%~dp0server"

rem 优先使用系统 Python（后端依赖装在此环境）
set "PYTHON_EXE=D:\Language_environment\Python\python.exe"

rem 若系统 Python 不存在，回退到 PATH 中的 python
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

rem 检查 Python 是否可用
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到可用的 Python 环境。
    echo        请确认已安装 Python，或修改本脚本中的 PYTHON_EXE 路径。
    pause
    exit /b 1
)

echo [信息] 使用 Python: %PYTHON_EXE%
echo [信息] 正在启动后端服务...
echo [信息] 本机访问:   http://localhost:5757
echo [信息] 局域网访问: http://本机IP:5757 （手机需连同一 WiFi）
echo [信息] API 文档:   http://localhost:5757/docs
echo [信息] 按 Ctrl+C 停止服务
echo.

rem 启动 uvicorn（监听所有网卡，端口 5757，支持热重载）
"%PYTHON_EXE%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5757

echo.
echo [信息] 后端服务已停止。
pause
