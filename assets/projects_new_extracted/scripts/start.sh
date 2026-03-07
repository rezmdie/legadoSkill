#!/bin/bash
# Legado订阅源爬虫和学习系统启动脚本

# 设置工作目录
cd "$(dirname "$0")"

echo "======================================"
echo "Legado订阅源爬虫和学习系统"
echo "======================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 启动爬虫（下载书源并自动学习）"
echo "2. 启动学习爬虫（仅学习，不保存文件）"
echo "3. 启动学习调度器（管理多个学习任务）"
echo "4. 从ID学习书源"
echo "5. 从URL学习书源"
echo "6. 从文件学习书源"
echo "7. 查看学习状态"
echo "8. 退出"
echo ""
read -p "请输入选项 (1-8): " choice

case $choice in
    1)
        echo "启动爬虫..."
        python3 legado_source_crawler.py
        ;;
    2)
        echo "启动学习爬虫..."
        python3 learning_crawler.py
        ;;
    3)
        echo "启动学习调度器..."
        python3 learning_scheduler.py --start
        ;;
    4)
        read -p "请输入书源ID: " source_id
        read -p "请输入分类 (默认: 书源): " category
        category=${category:-书源}
        python3 book_source_learner.py id "$source_id" --category "$category"
        ;;
    5)
        read -p "请输入书源URL: " url
        read -p "请输入分类 (默认: 书源): " category
        category=${category:-书源}
        python3 book_source_learner.py url "$url" --category "$category"
        ;;
    6)
        read -p "请输入JSON文件路径: " file_path
        read -p "请输入分类 (默认: 书源): " category
        category=${category:-书源}
        python3 book_source_learner.py json "$file_path" --file --category "$category"
        ;;
    7)
        python3 learning_scheduler.py --status
        ;;
    8)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
