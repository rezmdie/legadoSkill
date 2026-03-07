# Legado订阅源爬虫 - 快速开始指南

## 30秒快速开始

### 1. 安装依赖

```bash
cd /workspace/projects
pip install -r scripts/crawler_requirements.txt
```

### 2. 立即运行一次

```bash
# 智能模式（推荐）
python scripts/legado_source_crawler.py --once
```

### 3. 查看结果

书源文件会自动保存到 `assets/book_source_database/` 目录下。

## 常用命令

### 🚀 立即执行

```bash
# 智能模式（仅在有更新时下载）⭐ 推荐
python scripts/legado_source_crawler.py --once

# 完整模式（下载所有书源）
python scripts/legado_source_crawler.py --once --no-smart

# 强制更新（忽略更新检测）
python scripts/legado_source_crawler.py --once --force

# 只爬取指定分类
python scripts/legado_source_crawler.py --once --category 书源
```

### ⏰ 启动定时任务

```bash
# 智能模式定时任务（默认每天凌晨2点）⭐ 推荐
python scripts/legado_source_crawler.py

# 完整模式定时任务
python scripts/legado_source_crawler.py --no-smart

# 使用启动脚本
./scripts/run_crawler.sh  # Linux/Mac
scripts\run_crawler.bat   # Windows
```

## 核心功能

### ✨ 智能更新检测

- **工作原理**：通过哈希比对检测新书源
- **优势**：避免无效请求，节省时间和带宽
- **使用方法**：默认启用，使用 `--no-smart` 禁用

### 🤖 参考学习模块

- **工作原理**：自动解析书源并生成学习文档
- **存储位置**：`assets/book_source_learning/`
- **使用方法**：默认启用，在配置文件中设置 `ENABLE_LEARNING`

### 📁 自动分类

爬虫会自动识别并分类：

| 文件类型 | 存储位置 |
|---------|---------|
| 书源 | `book_sources/` |
| 书源合集 | `book_source_collections/` |
| 订阅源 | `rss_sources/` |
| 订阅源合集 | `rss_source_collections/` |
| 统计参考 | `book_source_reference/book_count_refs/` |
| 学习文档 | `book_source_learning/` |

## 配置文件

### 快速配置

编辑 `scripts/legado_source_crawler.py`：

```python
# 是否启用智能更新检测
ENABLE_UPDATE_CHECK = True  # True = 仅在有更新时下载

# 是否启用参考学习模块
ENABLE_LEARNING = True  # True = 自动生成学习文档

# 定时任务时间
schedule.every().day.at("02:00").do(crawler.run_daily)  # 修改这里
```

## 日志查看

```bash
# 实时查看日志
tail -f scripts/crawler.log

# 查看最近100行
tail -100 scripts/crawler.log

# 搜索错误信息
grep "ERROR\|WARNING" scripts/crawler.log
```

## 常见问题速查

| 问题 | 解决方案 |
|-----|---------|
| 无法获取页面 | 检查网络和BASE_URL |
| 重复下载 | 删除 `assets/metadata.json` |
| 没有生成学习文档 | 检查 `ENABLE_LEARNING` 配置 |
| 定时任务不执行 | 保持程序运行或使用cron |
| 权限不足 | `chmod -R 755 assets/` |

## 系统定时任务（可选）

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点执行的命令
0 2 * * * cd /workspace/projects && python scripts/legado_source_crawler.py --once >> scripts/cron.log 2>&1
```

## 下一步

- 📖 阅读完整文档：`scripts/CRAWLER_README.md`
- 🔧 自定义配置：修改 `scripts/legado_source_crawler.py`
- 🧪 测试爬虫：运行 `scripts/test_crawler.py`
- 🧹 清理过期文件：运行 `scripts/source_cleaner.py`

## 获取帮助

```bash
# 查看帮助信息
python scripts/legado_source_crawler.py --help

# 查看详细文档
cat scripts/CRAWLER_README.md
```
