@echo off
chcp 65001 >nul
echo ========================================
echo Legado书源驯兽师 MCP服务器启动
echo ========================================
echo.

REM 检查端口是否被占用
netstat -ano | findstr :5000 >nul
if %errorlevel% == 0 (
    echo [错误] 端口5000已被占用！
    echo 请先运行 stop_mcp.bat 停止现有服务
    echo.
    pause
    exit /b 1
)

echo [信息] 正在启动MCP服务器...
echo [信息] 端口: 5000
echo [信息] 地址: http://localhost:5000
echo.
echo [提示] 按 Ctrl+C 停止服务器
echo ========================================
echo.

python -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --log-level critical --no-access-log

if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务器启动失败！
    echo 请检查Python环境和依赖是否正确安装
    echo.
    pause
)
