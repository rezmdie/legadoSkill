@echo off
REM Legado订阅源爬虫启动脚本 (Windows)

echo =========================================
echo Legado订阅源爬虫启动脚本
echo =========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    pause
    exit /b 1
)

echo 检查依赖包...
pip install -q -r scripts\crawler_requirements.txt

if %errorlevel% equ 0 (
    echo 依赖包安装完成
) else (
    echo 警告: 依赖包安装可能存在问题
)

echo.
echo 开始运行爬虫...
echo.

REM 运行爬虫
python scripts\legado_source_crawler.py

pause
