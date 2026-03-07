#!/bin/bash

# Legado订阅源爬虫启动脚本

echo "========================================="
echo "Legado订阅源爬虫启动脚本"
echo "========================================="
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python环境"
    exit 1
fi

echo "检查依赖包..."
pip install -q -r scripts/crawler_requirements.txt

if [ $? -eq 0 ]; then
    echo "依赖包安装完成"
else
    echo "警告: 依赖包安装可能存在问题"
fi

echo ""
echo "开始运行爬虫..."
echo ""

# 运行爬虫
python scripts/legado_source_crawler.py
