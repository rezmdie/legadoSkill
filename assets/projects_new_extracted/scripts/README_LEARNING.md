# Legado订阅源爬虫和学习系统

## 🎯 系统简介

这是一个完整的Legado书源爬虫和学习系统，包含以下核心功能：

1. **书源爬虫** - 自动下载书源并保存
2. **智能学习** - 自动解析书源并生成学习文档
3. **智能判断** - 自动识别书源和普通数据
4. **任务调度** - 管理多个学习任务
5. **定时更新** - 支持定时爬取和学习

## ✨ 核心特性

### 1. 主爬虫（推荐）
- ✅ 自动下载书源并保存
- ✅ 自动学习到知识库
- ✅ 智能更新检测
- ✅ 定时调度
- ✅ 基于原始ID命名

### 2. 学习爬虫
- ✅ 仅学习，不保存文件
- ✅ 节省磁盘空间
- ✅ 智能更新检测
- ✅ 定时调度

### 3. 学习工具
- ✅ 支持从ID学习
- ✅ 支持从URL学习
- ✅ 支持从JSON学习
- ✅ 支持从文件学习
- ✅ 智能判断书源

### 4. 学习调度器
- ✅ 任务优先级管理
- ✅ 任务失败重试
- ✅ 多任务并发
- ✅ 任务历史记录

### 5. 智能判断
- ✅ 自动识别书源
- ✅ 区分书源和普通数据
- ✅ 提供判断原因

## 📁 目录结构

```
scripts/
├── legado_source_crawler.py      # 主爬虫（下载+学习）
├── learning_crawler.py           # 学习爬虫（仅学习）
├── book_source_learner.py        # 学习工具
├── learning_scheduler.py         # 学习调度器
├── reference_learning_module.py  # 参考学习模块
├── start.sh                      # 启动脚本
├── LEARNING_SYSTEM_GUIDE.md      # 详细使用指南
└── README_LEARNING.md            # 本文件

assets/
├── book_source_database/          # 书源文件
├── book_source_reference/        # 参考文件
└── knowledge_base/               # 知识库（学习文档）
```

## 🚀 快速开始

### 方式1：使用启动脚本（推荐）

```bash
cd scripts
chmod +x start.sh
./start.sh
```

### 方式2：直接运行

#### 启动主爬虫

```bash
# 智能模式（仅在有更新时运行）
python scripts/legado_source_crawler.py --once

# 完整模式（下载所有书源）
python scripts/legado_source_crawler.py --once --no-smart

# 启动定时任务（每天凌晨2点自动运行）
python scripts/legado_source_crawler.py
```

#### 启动学习爬虫

```bash
# 智能模式（仅在有更新时学习）
python scripts/learning_crawler.py --once

# 启动定时任务（每天早上8点自动运行）
python scripts/learning_crawler.py
```

#### 使用学习工具

```bash
# 从ID学习
python scripts/book_source_learner.py id 6873

# 从URL学习
python scripts/book_source_learner.py url "https://example.com/source.json"

# 从文件学习
python scripts/book_source_learner.py json /path/to/source.json --file

# 检查数据类型
python scripts/book_source_learner.py check '{"data":"test"}'
```

#### 使用学习调度器

```bash
# 启动调度器
python scripts/learning_scheduler.py --start

# 查看状态
python scripts/learning_scheduler.py --status

# 添加任务
python scripts/learning_scheduler.py --add-id 6873
python scripts/learning_scheduler.py --add-url "https://example.com/source.json"
```

## 📊 使用场景

### 场景1：完整爬取和学习（推荐）

使用主爬虫，自动下载书源并学习到知识库。

```bash
python scripts/legado_source_crawler.py
```

### 场景2：仅学习（节省空间）

使用学习爬虫，仅生成学习文档，不保存书源文件。

```bash
python scripts/learning_crawler.py
```

### 场景3：学习指定书源

使用学习工具，学习指定的书源。

```bash
python scripts/book_source_learner.py id 6873
```

### 场景4：批量学习任务

使用学习调度器，管理多个学习任务。

```bash
python scripts/learning_scheduler.py --start
```

### 场景5：智能判断

检查数据是否是书源，自动识别。

```bash
python scripts/book_source_learner.py check '{"bookSourceName":"示例书源"}'
```

## 🎯 智能判断示例

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
    {"id": 1, "name": "item1"}
  ]
}
```

**判断结果**：✗ 不是书源 → 当作用户要处理的数据

## 📝 命令行参数

### 主爬虫

```bash
python scripts/legado_source_crawler.py [选项]

选项:
  --once          只执行一次，不启动定时任务
  --force         强制更新所有书源
  --no-smart      禁用智能模式
  --category <名> 只爬取指定分类
```

### 学习爬虫

```bash
python scripts/learning_crawler.py [选项]

选项:
  --once          只执行一次，不启动定时任务
  --force         强制更新所有书源
  --no-smart      禁用智能模式
  --category <名> 只学习指定分类
```

### 学习工具

```bash
python scripts/book_source_learner.py <命令> [参数]

命令:
  id <ID>              从原始ID学习
  url <URL>            从URL学习
  json <数据>          从JSON学习
  check <数据>         检查数据类型

参数:
  --category <名>      分类（默认：书源）
  --source-id <ID>     原始ID
  --file               将参数作为文件路径处理
```

### 学习调度器

```bash
python scripts/learning_scheduler.py [选项]

选项:
  --start              启动调度器
  --stop               停止调度器
  --status             查看状态
  --add-id <ID>        添加ID任务
  --add-url <URL>      添加URL任务
  --add-file <路径>    添加文件任务
  --add-crawl          添加爬取任务
  --category <名>      分类
  --priority <级别>    优先级（LOW/NORMAL/HIGH/URGENT）
```

## 🔧 配置文件

### 定时任务配置

编辑对应的Python文件，修改定时时间：

```python
# 主爬虫（默认：凌晨2点）
schedule.every().day.at("02:00").do(crawler.run_daily)

# 学习爬虫（默认：早上8点）
schedule.every().day.at("08:00").do(crawler.run_daily)

# 学习调度器（默认：8:00和20:00）
schedule.every().day.at("08:00").do(morning_crawl)
schedule.every().day.at("20:00").do(evening_crawl)
```

## 📖 详细文档

- [完整使用指南](LEARNING_SYSTEM_GUIDE.md) - 详细的系统使用指南
- [爬虫使用说明](CRAWLER_README.md) - 爬虫详细说明
- [快速开始指南](QUICK_START.md) - 快速开始指南

## 🔍 日志查看

```bash
# 查看爬虫日志
tail -f scripts/crawler.log

# 查看学习日志
tail -f scripts/learning.log

# 查看调度器日志
tail -f scripts/scheduler.log
```

## 🎨 文件命名规则

### 书源文件
```
原始ID_标题_时间戳.json
示例: 6873_📖Lofter_20260218_101954.json
```

### 学习文档
```
原始ID_标题_书源_时间戳.md
示例: 6873_📖Lofter_书源_20260218_101954.md
```

### 统计参考文件
```
原始ID_标题_统计_时间戳.json
示例: 6873_统计参考_统计_20260218_101954.json
```

## ⚙️ 最佳实践

1. **首次运行**：使用主爬虫完整爬取所有书源
2. **日常更新**：使用智能模式（`--once`）
3. **定时任务**：设置合适的定时时间
4. **批量学习**：使用调度器管理多个任务
5. **测试学习**：先测试单个书源，再批量学习
6. **定期清理**：清理过期文件和日志

## 🐛 故障排除

### 学习失败
- 检查日志文件确认错误原因
- 检查目录权限
- 检查网络连接

### 智能判断错误
- 使用 `check` 命令检查数据类型
- 查看判断标准和原因

### 任务卡住
- 查看调度器状态
- 停止调度器并重启

## 📈 系统特性

### 主爬虫
- ✅ 自动下载书源
- ✅ 自动学习到知识库
- ✅ 智能更新检测
- ✅ 定时调度
- ✅ 原始ID命名
- ✅ 元数据管理

### 学习爬虫
- ✅ 仅学习，不保存
- ✅ 节省磁盘空间
- ✅ 智能更新检测
- ✅ 定时调度

### 学习工具
- ✅ 多种输入方式
- ✅ 智能判断
- ✅ 自动识别
- ✅ 灵活使用

### 学习调度器
- ✅ 优先级管理
- ✅ 任务重试
- ✅ 多任务并发
- ✅ 历史记录

## 🎉 总结

本系统提供了完整的书源爬虫和学习解决方案：

1. **主爬虫** - 下载+学习（推荐）
2. **学习爬虫** - 仅学习（节省空间）
3. **学习工具** - 多种输入方式
4. **学习调度器** - 任务管理
5. **智能判断** - 自动识别

根据实际需求选择合适的工具，提高效率！

## 📞 支持

如有问题，请查看：
- [完整使用指南](LEARNING_SYSTEM_GUIDE.md)
- [爬虫使用说明](CRAWLER_README.md)
- [快速开始指南](QUICK_START.md)

---

**版本**: 1.0.0  
**更新时间**: 2026-02-18
