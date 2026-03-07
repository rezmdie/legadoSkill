@echo off
echo ========================================
echo 测试MCP服务器启动
echo ========================================
echo.

set MCP_MODE=true
set COZE_LOG_LEVEL=CRITICAL
set PYTHONIOENCODING=utf-8

echo 启动MCP服务器（5秒后自动停止）...
echo.

timeout /t 1 /nobreak >nul
start /b python src\mcp_server.py

timeout /t 5 /nobreak

echo.
echo 如果没有看到错误信息，说明服务器可以正常启动
echo.
echo 现在请在Kilo IDE中点击"刷新 MCP 服务器"
echo.
pause
