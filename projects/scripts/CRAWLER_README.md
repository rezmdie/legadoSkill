# Legado订阅源爬虫使用说明

## 功能介绍

这个爬虫会定期从"源仓库"订阅源自动下载书源和订阅源文件，并按照以下规则自动分类存储：

### ✨ 核心功能

1. **自动分类存储** - 智能识别并分类书源、订阅源等不同类型文件
2. **智能更新检测** - 通过哈希比对，仅在有更新时才下载新书源
3. **参考学习模块** - 自动将新书源导入知识库，生成结构化文档供AI学习
4. **定时调度** - 支持定时任务，默认每天凌晨2点自动运行
5. **元数据管理** - 记录已处理的书源，避免重复下载

### 🤖 参考学习模块

参考学习模块是爬虫的核心功能之一，它会自动将下载的书源解析并生成结构化文档，导入到知识库供AI学习：

- **自动解析书源** - 提取书源名称、URL、规则等关键信息
- **生成学习文档** - 为每个书源生成易读的Markdown文档
- **分类整理** - 按照分类自动组织学习材料
- **学习摘要** - 生成学习进度和统计信息

学习文档示例：
```markdown
# 书源名称

## 基本信息
- 名称：示例书源
- 类型：书源
- 更新时间：2024-02-01

## 书源配置
- 网址：https://example.com
- 规则数量：5
- 启用状态：已启用

## 使用说明
[自动生成的使用说明]
```

### 📁 目录结构

```
assets/
├── book_source_database/          # 数据库目录（主存储）
│   ├── book_sources/             # 书源文件
│   ├── book_source_collections/  # 书源合集
│   ├── rss_sources/              # 订阅源文件
│   └── rss_source_collections/   # 订阅源合集
├── book_source_reference/        # 参考目录（特殊文件）
│   ├── book_count_refs/          # 书源数量参考文件 ⭐
│   └── other_refs/               # 其他参考文件
└── book_source_learning/         # 学习目录（参考学习模块）🆕
    ├── 书源/                     # 书源学习文档
    ├── 书源合集/                 # 书源合集学习文档
    ├── 订阅源/                   # 订阅源学习文档
    ├── 订阅源合集/               # 订阅源合集学习文档
    └── learning_summary.md       # 学习摘要

scripts/
├── legado_source_crawler.py      # 爬虫主程序
├── reference_learning_module.py  # 参考学习模块 🆕
├── crawler_requirements.txt      # 依赖包
├── crawler_config.json           # 配置文件
└── crawler.log                   # 运行日志
```

### 🎯 自动分类规则

爬虫会自动识别以下类型的文件：

1. **书源数量参考文件** - 自动保存到 `assets/book_source_reference/book_count_refs/`
   - 标题包含：数量、统计、排行、count、number、rank
   - 包含统计字段：count、total、number、weight、respondTime

2. **普通书源文件** - 保存到对应的数据库子目录
   - 书源 → `book_sources/`
   - 书源合集 → `book_source_collections/`
   - 订阅源 → `rss_sources/`
   - 订阅源合集 → `rss_source_collections/`

3. **学习文档** - 自动生成并保存到 `assets/book_source_learning/`
   - 按照分类自动组织
   - 包含书源详细说明和使用指南

## 安装依赖

```bash
cd /workspace/projects
pip install -r scripts/crawler_requirements.txt
```

## 使用方法

### 1. 立即执行一次爬取（智能模式）

智能模式会先检查是否有更新，仅在有新书源时才下载：

```bash
# 智能模式（默认）
python scripts/legado_source_crawler.py --once

# 只执行一次，不启动定时任务
python scripts/legado_source_crawler.py --once
```

### 2. 强制更新所有书源

忽略更新检测，重新下载所有书源：

```bash
python scripts/legado_source_crawler.py --force --once
```

### 3. 只爬取指定分类

```bash
python scripts/legado_source_crawler.py --category 书源 --once
python scripts/legado_source_crawler.py --category 订阅源 --once
```

### 4. 禁用智能模式（完整爬取）

```bash
python scripts/legado_source_crawler.py --no-smart --once
```

### 5. 启动定时任务

启动后会保持运行，每天凌晨2点自动执行：

```bash
# 启动定时任务（智能模式）
python scripts/legado_source_crawler.py

# 启动定时任务（完整模式）
python scripts/legado_source_crawler.py --no-smart
```

### 6. 使用启动脚本

#### Linux/Mac:
```bash
chmod +x scripts/run_crawler.sh
./scripts/run_crawler.sh
```

#### Windows:
```bash
scripts\run_crawler.bat
```

## 命令行参数说明

| 参数 | 说明 |
|------|------|
| `--force` | 强制更新所有书源（忽略更新检测） |
| `--no-smart` | 禁用智能模式（完整爬取） |
| `--category <name>` | 只爬取指定分类 |
| `--once` | 只执行一次，不启动定时任务 |

爬虫默认设置为每天凌晨2点自动执行。你可以修改 `legado_source_crawler.py` 中的定时时间：

```python
# 修改这里的时间
schedule.every().day.at("02:00").do(crawler.run_daily)

# 示例：改为每天早上8点
schedule.every().day.at("08:00").do(crawler.run_daily)

# 示例：改为每6小时执行一次
schedule.every(6).hours.do(crawler.run_daily)
```

### 3. 手动添加定时任务（Linux）

如果你想使用系统的cron任务来定时执行：

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点执行的命令
0 2 * * * cd /workspace/projects && python scripts/legado_source_crawler.py >> scripts/cron.log 2>&1
```

## 配置说明

### 1. 修改爬取的订阅源URL

编辑 `scripts/legado_source_crawler.py`，修改以下配置：

```python
# 修改基础URL
BASE_URL = "https://www.yck2026.top"

# 修改分类配置
CATEGORIES = {
    "书源": {
        "url": "/yuedu/shuyuan/index.html",
        "subdir": "book_sources"
    },
    # 添加或修改其他分类...
}
```

### 2. 修改存储目录

```python
# 修改数据库目录
DATABASE_DIR = "assets/book_source_database"

# 修改参考目录
REFERENCE_DIR = "assets/book_source_reference"

# 修改学习目录
LEARNING_DIR = "assets/book_source_learning"
```

### 3. 启用/禁用参考学习模块

编辑 `scripts/legado_source_crawler.py`，修改以下配置：

```python
# 是否启用参考学习模块（默认启用）
ENABLE_LEARNING = True

# 是否生成学习摘要（默认启用）
ENABLE_LEARNING_SUMMARY = True
```

### 4. 调整智能更新检测

编辑 `scripts/legado_source_crawler.py`，修改以下配置：

```python
# 是否启用智能更新检测（默认启用）
ENABLE_UPDATE_CHECK = True

# 更新检测超时时间（秒）
UPDATE_CHECK_TIMEOUT = 30
```

### 5. 修改定时任务时间

```python
# 修改这里的时间
schedule.every().day.at("02:00").do(crawler.run_daily, use_smart_mode=True)

# 示例：改为每天早上8点
schedule.every().day.at("08:00").do(crawler.run_daily, use_smart_mode=True)

# 示例：改为每6小时执行一次
schedule.every(6).hours.do(crawler.run_daily, use_smart_mode=True)

# 示例：改为每周一早上9点执行
schedule.every().monday.at("09:00").do(crawler.run_daily, use_smart_mode=True)
```

### 6. 系统定时任务（Linux cron）

如果你想使用系统的cron任务来定时执行：

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点执行的命令（智能模式）
0 2 * * * cd /workspace/projects && python scripts/legado_source_crawler.py --once >> scripts/cron.log 2>&1

# 添加每天凌晨2点执行的命令（完整模式）
0 2 * * * cd /workspace/projects && python scripts/legado_source_crawler.py --once --no-smart >> scripts/cron.log 2>&1
```

## 日志查看

### 查看运行日志

```bash
tail -f scripts/crawler.log
```

### 查看最近的日志

```bash
tail -100 scripts/crawler.log
```

## 元数据说明

爬虫会在 `assets/metadata.json` 中记录已处理的书源，避免重复下载：

```json
{
  "processed_hashes": {
    "abc123...": {
      "timestamp": "2024-02-01T10:30:00",
      "title": "示例书源",
      "json_url": "https://..."
    }
  }
}
```

如果需要重新下载所有书源，删除这个文件即可：

```bash
rm assets/metadata.json
```

## 性能优化建议

### 1. 调整请求间隔

在 `crawl_category` 方法中修改：

```python
time.sleep(1)  # 修改这里，避免请求过快
```

### 2. 调整分类间隔

在 `crawl_all_categories` 方法中修改：

```python
time.sleep(2)  # 修改这里，分类之间间隔
```

### 3. 使用代理

如果需要使用代理，在 `_init_directories` 方法中添加：

```python
self.session.proxies = {
    'http': 'http://your-proxy:port',
    'https': 'https://your-proxy:port'
}
```

## 常见问题

### 1. 爬虫运行失败

**问题**：无法获取页面内容

**解决方案**：
- 检查网络连接
- 检查BASE_URL是否正确
- 查看日志文件 `scripts/crawler.log`

### 2. 文件保存失败

**问题**：目录权限不足

**解决方案**：
```bash
chmod -R 755 assets/
```

### 3. 重复下载

**问题**：每次都重新下载所有书源

**解决方案**：
- 检查 `assets/metadata.json` 是否存在
- 检查哈希计算是否正确

### 4. 智能更新检测不工作

**问题**：智能模式下仍然下载所有书源

**解决方案**：
- 检查 `ENABLE_UPDATE_CHECK` 配置是否为 `True`
- 检查 `assets/update_history.json` 是否存在且可写
- 使用 `--no-smart` 参数禁用智能模式进行对比测试

### 5. 参考学习模块不工作

**问题**：没有生成学习文档

**解决方案**：
- 检查 `ENABLE_LEARNING` 配置是否为 `True`
- 检查 `assets/book_source_learning/` 目录是否可写
- 查看日志中是否有学习模块的错误信息
- 确认书源数据格式正确

### 6. 定时任务不执行

**问题**：设置了定时任务但没有执行

**解决方案**：
- 检查程序是否正在运行（保持运行状态）
- 检查系统时间是否正确
- 查看日志文件确认是否有执行记录
- 使用 cron 任务替代内置定时任务

## 高级功能

### 1. 自定义分类规则

在 `_is_count_reference` 方法中添加更多关键词：

```python
count_keywords = ['数量', '统计', '排行', 'count', 'number', 'rank', '你的关键词']
```

### 2. 自定义文件名格式

在 `_generate_filename` 方法中修改：

```python
if is_count_ref:
    return f"{title}_统计_{timestamp}.json"  # 修改这里
else:
    return f"{title}_{timestamp}.json"  # 修改这里
```

### 3. 添加通知功能

在 `_save_source` 方法中添加：

```python
# 保存成功后发送通知
import requests
requests.get("https://your-notification-url")
```

## 维护建议

1. **定期检查日志**：查看 `scripts/crawler.log` 确保正常运行
2. **定期清理旧文件**：可以添加清理脚本删除过期的书源
3. **监控磁盘空间**：确保有足够的存储空间
4. **更新规则**：如果源网站结构变化，及时更新解析规则

## 联系支持

如果遇到问题，请查看日志文件或提交Issue。

---

**版本**: 1.0
**最后更新**: 2024-02-01
