@echo off
chcp 65001 >nul
echo ========================================
echo Legado书源驯兽师 MCP服务器停止
echo ========================================
echo.

REM 查找占用5000端口的进程
netstat -ano | findstr :5000 >nul
if %errorlevel% neq 0 (
    echo [信息] 端口5000未被占用，无需停止
    echo.
    pause
    exit /b 0
)

echo [信息] 正在查找占用端口5000的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    set PID=%%a
    goto :found
)

:found
if defined PID (
    echo [信息] 找到进程 PID: %PID%
    echo [信息] 正在停止进程...
    taskkill /F /PID %PID% >nul 2>&1
    
    if %errorlevel% == 0 (
        echo [成功] 进程已停止
    ) else (
        echo [错误] 停止进程失败，可能需要管理员权限
    )
) else (
    echo [错误] 未找到占用端口的进程
)

echo.
echo ========================================
echo [完成] 操作完成
echo ========================================
echo.
pause
