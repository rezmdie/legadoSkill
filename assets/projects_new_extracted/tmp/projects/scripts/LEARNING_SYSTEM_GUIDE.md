# Legado订阅源爬虫和学习系统使用指南

## 系统概述

本系统包含以下核心组件：

1. **主爬虫** (`legado_source_crawler.py`) - 下载书源并自动学习
2. **学习爬虫** (`learning_crawler.py`) - 仅学习，不保存文件
3. **学习工具** (`book_source_learner.py`) - 支持多种输入方式学习书源
4. **学习调度器** (`learning_scheduler.py`) - 管理多个学习任务
5. **参考学习模块** (`reference_learning_module.py`) - 生成学习文档

## 功能说明

### 1. 主爬虫（推荐使用）

**功能**：
- 下载书源并保存到本地
- 自动学习到知识库
- 智能更新检测
- 定时调度

**使用方法**：

```bash
# 智能模式（仅在有更新时运行）
python scripts/legado_source_crawler.py --once

# 完整模式（下载所有书源）
python scripts/legado_source_crawler.py --once --no-smart

# 强制更新（忽略更新检测）
python scripts/legado_source_crawler.py --once --force

# 只爬取指定分类
python scripts/legado_source_crawler.py --once --category 书源

# 启动定时任务（每天凌晨2点自动运行）
python scripts/legado_source_crawler.py
```

**特点**：
- ✅ 自动保存书源文件
- ✅ 自动学习到知识库
- ✅ 智能更新检测
- ✅ 定时调度
- ✅ 支持强制更新

### 2. 学习爬虫

**功能**：
- 仅学习书源，不保存文件
- 适合只需要知识库的场景
- 定时调度

**使用方法**：

```bash
# 智能模式（仅在有更新时学习）
python scripts/learning_crawler.py --once

# 完整模式（学习所有书源）
python scripts/learning_crawler.py --once --no-smart

# 只学习指定分类
python scripts/learning_crawler.py --once --category 书源

# 启动定时任务（每天早上8点自动运行）
python scripts/learning_crawler.py
```

**特点**：
- ✅ 不保存书源文件（节省空间）
- ✅ 仅生成学习文档
- ✅ 智能更新检测
- ✅ 定时调度

### 3. 学习工具

**功能**：
- 支持多种输入方式学习书源
- 智能判断是否是书源
- 如果是书源则学习，否则返回处理结果

**使用方法**：

#### 3.1 从原始ID学习

```bash
# 使用默认分类（书源）
python scripts/book_source_learner.py id 6873

# 指定分类
python scripts/book_source_learner.py id 6873 --category 订阅源
```

#### 3.2 从URL学习

```bash
# 从URL学习
python scripts/book_source_learner.py url "https://www.example.com/source.json"

# 指定分类
python scripts/book_source_learner.py url "https://www.example.com/source.json" --category 书源合集
```

#### 3.3 从JSON字符串学习

```bash
# 从JSON字符串学习
python scripts/book_source_learner.py json '{"bookSourceName":"示例书源","bookSourceUrl":"https://example.com"}'

# 指定原始ID
python scripts/book_source_learner.py json '{"bookSourceName":"示例书源"}' --source-id 1234
```

#### 3.4 从JSON文件学习

```bash
# 从文件学习
python scripts/book_source_learner.py json /path/to/source.json --file

# 指定分类
python scripts/book_source_learner.py json /path/to/source.json --file --category 书源
```

#### 3.5 检查数据类型

```bash
# 检查JSON字符串
python scripts/book_source_learner.py check '{"bookSourceName":"示例书源"}'

# 检查文件
python scripts/book_source_learner.py check /path/to/data.json --file
```

**智能判断逻辑**：

系统会自动判断提供的数据是否是书源：
- ✅ **是书源** → 自动学习到知识库
- ❌ **不是书源** → 当作用户要处理的数据返回（如API请求返回的数据）

**判断标准**：
- 包含书源特征字段（`bookSourceName`、`bookSourceUrl`等）
- 包含有效规则字段（`ruleSearch`、`ruleBookInfo`等）

### 4. 学习调度器

**功能**：
- 管理多个学习任务
- 支持优先级队列
- 任务重试机制
- 定时调度

**使用方法**：

```bash
# 启动调度器（带定时任务）
python scripts/learning_scheduler.py --start

# 停止调度器
python scripts/learning_scheduler.py --stop

# 查看状态
python scripts/learning_scheduler.py --status

# 添加ID学习任务
python scripts/learning_scheduler.py --add-id 6873

# 添加URL学习任务
python scripts/learning_scheduler.py --add-url "https://example.com/source.json"

# 添加文件学习任务
python scripts/learning_scheduler.py --add-file /path/to/source.json

# 添加爬取学习任务
python scripts/learning_scheduler.py --add-crawl

# 指定优先级
python scripts/learning_scheduler.py --add-id 6873 --priority URGENT
```

**优先级**：
- `URGENT` - 紧急任务（优先级最高）
- `HIGH` - 高优先级
- `NORMAL` - 普通优先级（默认）
- `LOW` - 低优先级

**特点**：
- ✅ 支持多任务并发
- ✅ 任务失败自动重试
- ✅ 优先级队列管理
- ✅ 任务历史记录

## 目录结构

```
assets/
├── book_source_database/          # 书源文件存储
│   ├── book_sources/             # 书源文件（ID_标题_时间戳.json）
│   ├── book_source_collections/  # 书源合集
│   ├── rss_sources/              # 订阅源文件
│   └── rss_source_collections/   # 订阅源合集
├── book_source_reference/        # 参考文件
│   └── book_count_refs/          # 统计参考文件
└── knowledge_base/               # 知识库（学习文档）
    ├── book_sources/             # 书源学习文档（ID_标题_书源_时间戳.md）
    ├── book_source_collections/  # 书源合集学习文档
    ├── rss_sources/              # 订阅源学习文档
    ├── rss_source_collections/   # 订阅源合集学习文档
    ├── learning_stats/           # 学习统计
    └── learning_summary.md       # 学习摘要

scripts/
├── legado_source_crawler.py      # 主爬虫（下载+学习）
├── learning_crawler.py           # 学习爬虫（仅学习）
├── book_source_learner.py        # 学习工具
├── learning_scheduler.py         # 学习调度器
├── reference_learning_module.py  # 参考学习模块
├── start.sh                      # 启动脚本
├── crawler.log                   # 爬虫日志
├── learning.log                  # 学习日志
├── scheduler.log                 # 调度器日志
├── update_check.json             # 更新检测数据
├── learning_log.json             # 学习日志
└── scheduler_history.json       # 调度器历史
```

## 使用场景

### 场景1：完整爬取和学习（推荐）

```bash
# 启动主爬虫，自动下载书源并学习
python scripts/legado_source_crawler.py
```

**适用**：
- 需要保存书源文件
- 需要生成学习文档
- 需要定时更新

### 场景2：仅学习（节省空间）

```bash
# 启动学习爬虫，仅生成学习文档
python scripts/learning_crawler.py
```

**适用**：
- 只需要知识库
- 不需要保存书源文件
- 磁盘空间有限

### 场景3：学习指定书源

```bash
# 从ID学习
python scripts/book_source_learner.py id 6873

# 从URL学习
python scripts/book_source_learner.py url "https://example.com/source.json"

# 从文件学习
python scripts/book_source_learner.py json /path/to/source.json --file
```

**适用**：
- 学习指定的书源
- 测试学习功能
- 手动管理书源

### 场景4：批量学习任务

```bash
# 启动调度器，管理多个学习任务
python scripts/learning_scheduler.py --start
```

**适用**：
- 需要管理多个学习任务
- 需要优先级控制
- 需要任务重试

### 场景5：智能判断

```bash
# 检查数据是否是书源
python scripts/book_source_learner.py check '{"data":"test"}'
# 输出：✗ 不是书源: 不包含书源特征字段
#       当作用户要处理的数据
```

**适用**：
- 不确定数据类型
- 需要智能判断
- 区分书源和普通数据

## 智能判断示例

### 示例1：书源数据

```json
{
  "bookSourceName": "示例书源",
  "bookSourceUrl": "https://example.com",
  "ruleSearch": {
    "bookList": "div.item",
    "name": "h3@text"
  }
}
```

**判断结果**：✓ 是书源 → 自动学习

### 示例2：普通数据

```json
{
  "status": "success",
  "data": [
    {"id": 1, "name": "item1"},
    {"id": 2, "name": "item2"}
  ]
}
```

**判断结果**：✗ 不是书源 → 当作用户要处理的数据

## 定时任务配置

### 主爬虫定时任务

默认时间：每天凌晨2点

修改方法：编辑 `scripts/legado_source_crawler.py`

```python
# 修改这里的时间
schedule.every().day.at("02:00").do(crawler.run_daily, use_smart_mode=True)

# 示例：改为每天早上8点
schedule.every().day.at("08:00").do(crawler.run_daily, use_smart_mode=True)
```

### 学习爬虫定时任务

默认时间：每天早上8点

修改方法：编辑 `scripts/learning_crawler.py`

```python
# 修改这里的时间
schedule.every().day.at("08:00").do(crawler.run_daily, use_smart_mode=True)
```

### 学习调度器定时任务

默认时间：每天8:00和20:00

修改方法：编辑 `scripts/learning_scheduler.py`

```python
# 修改这里的时间
schedule.every().day.at("08:00").do(morning_crawl)
schedule.every().day.at("20:00").do(evening_crawl)
```

## 日志查看

```bash
# 查看爬虫日志
tail -f scripts/crawler.log

# 查看学习日志
tail -f scripts/learning.log

# 查看调度器日志
tail -f scripts/scheduler.log

# 查看最近的日志
tail -100 scripts/crawler.log
```

## 故障排除

### 1. 学习失败

**问题**：书源下载成功但学习失败

**解决方案**：
- 检查日志文件确认错误原因
- 检查 `assets/knowledge_base/` 目录权限
- 检查参考学习模块是否正常

### 2. 智能判断错误

**问题**：将普通数据误判为书源

**解决方案**：
- 使用 `check` 命令检查数据类型
- 查看判断标准和原因
- 如有问题，手动指定数据类型

### 3. 任务卡住

**问题**：学习任务长时间不响应

**解决方案**：
- 查看调度器状态
- 停止调度器并重启
- 检查网络连接

### 4. 内存不足

**问题**：批量学习时内存不足

**解决方案**：
- 减少并发任务数
- 分批学习书源
- 使用学习爬虫（不保存文件）

## 最佳实践

1. **首次运行**：使用主爬虫完整爬取所有书源
2. **日常更新**：使用智能模式（`--once`）
3. **定时任务**：设置合适的定时时间（避开高峰期）
4. **批量学习**：使用调度器管理多个任务
5. **测试学习**：先测试单个书源，再批量学习
6. **定期清理**：使用 `source_cleaner.py` 清理过期文件

## 总结

本系统提供了完整的书源学习解决方案：

- ✅ 主爬虫：下载+学习
- ✅ 学习爬虫：仅学习
- ✅ 学习工具：多种输入方式
- ✅ 学习调度器：任务管理
- ✅ 智能判断：自动识别书源

根据实际需求选择合适的工具，提高效率！
