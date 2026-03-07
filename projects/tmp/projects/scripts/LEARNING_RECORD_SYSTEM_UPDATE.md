# 已学习记录系统更新

## 📋 概述

本次更新实现了书源的智能去重和自动清理功能，确保：
1. **学习后删除原始文件** - 只保留学习后的成果
2. **避免重复学习** - 已学习的书源不再重复处理
3. **跳过已下载书源** - 爬虫不再下载已学习的书源

## 🔧 核心功能

### 1. 已学习记录机制

#### 记录文件
- **路径**: `assets/learned_sources.json`
- **格式**: JSON
- **内容**:
  ```json
  {
    "sources": {
      "6873": {
        "name": "📖Lofter",
        "url": "📖Lofter",
        "learned_at": "2026-02-18T10:31:17.511174",
        "original_file": null
      }
    },
    "urls": {
      "📖Lofter": "6873"
    },
    "last_update": "2026-02-18T10:31:17.511181"
  }
  ```

#### 新增方法（`ReferenceLearningModule`）
- `is_learned(source_id=None, url=None)` - 检查书源是否已学习
- `mark_as_learned(source_id, source_data, source_url=None, original_file=None)` - 标记书源为已学习
- `get_learned_sources()` - 获取已学习书源列表
- `clear_learned_record()` - 清空已学习记录（慎用）

### 2. 自动删除原始文件

#### 删除时机
- 学习成功后自动删除原始文件（如果指定了文件路径）
- 删除逻辑在 `mark_as_learned` 方法中执行

#### 适用场景
- 从文件学习时（`learn_from_file`）
- 支持自定义是否删除（`delete_original` 参数）

### 3. 智能去重

#### 检查点
1. **学习前检查** - 在 `learn_book_source` 方法中检查
2. **下载前检查** - 在爬虫的 `crawl_category` 方法中检查

#### 检查逻辑
```python
# 1. 检查是否已学习（按ID）
if source_id and learning_module.is_learned(source_id=source_id):
    logger.info(f"书源已学习过，跳过: {source_id}")
    return True

# 2. 检查是否已学习（按URL）
if url and learning_module.is_learned(url=url):
    logger.info(f"书源已学习过，跳过: {url}")
    return True
```

## 📝 修改文件

### 1. `scripts/reference_learning_module.py`
**修改内容**:
- 添加 `learned_record_file` 参数
- 新增已学习记录相关方法
- 修改 `learn_book_source` 方法，添加 `mark_learned` 参数
- 在 `mark_as_learned` 中实现自动删除逻辑

**关键代码**:
```python
def __init__(self, knowledge_base_dir="assets/knowledge_base", learned_record_file="assets/learned_sources.json"):
    self.knowledge_base_dir = knowledge_base_dir
    self.learned_record_file = learned_record_file
    self._init_directories()
    self._init_learned_record()

def mark_as_learned(self, source_id: str, source_data: dict, source_url: str = None, original_file: str = None):
    """标记书源为已学习，并可选删除原始文件"""
    # 保存学习记录
    # 删除原始文件（如果指定）
```

### 2. `scripts/book_source_learner.py`
**修改内容**:
- 修改 `learn_from_file` 方法，添加 `delete_original` 参数
- 在 `source_info` 中传递 `original_file` 路径

**关键代码**:
```python
def learn_from_file(self, file_path: str, category: str = "书源", delete_original: bool = True):
    source_info = {
        'source_id': source_id,
        'link': file_path,
        'pub_time': str(datetime.now()),
        'description': f'从文件读取: {os.path.basename(file_path)}',
        'original_file': file_path if delete_original else None
    }
```

### 3. `scripts/learning_crawler.py`
**修改内容**:
- 添加 `Any` 和 `Tuple` 到 typing 导入
- 修改 `_learn_source` 方法，添加已学习检查

**关键代码**:
```python
def _learn_source(self, source_data: Dict, source_info: Dict, category: str) -> bool:
    # 检查是否已学习
    source_id = source_info.get('source_id')
    if source_id and learning_module.is_learned(source_id=source_id):
        logger.info(f"书源已学习过，跳过: {source_id}")
        return True

    success = learning_module.learn_book_source(source_data, source_info, category)
    return success
```

### 4. `scripts/legado_source_crawler.py`
**修改内容**:
- 修改 `crawl_category` 方法，在下载前检查已学习状态

**关键代码**:
```python
# 检查是否已学习（避免重复下载已学习的书源）
if self.enable_learning and self.learning_module:
    source_id = source.get('source_id')
    if source_id and self.learning_module.is_learned(source_id=source_id):
        logger.info(f"跳过已学习的书源: {source['title']} (ID: {source_id})")
        self._mark_processed(source['hash'], source)
        continue
```

## 🧪 测试结果

### 测试1: 从ID学习书源
```bash
python scripts/book_source_learner.py id 6873
```
**结果**:
```
✓ 成功学习书源ID: 6873
✓ 书源已标记为已学习: 6873
✓ 知识库文档已保存
```

### 测试2: 重复学习（验证跳过）
```bash
python scripts/book_source_learner.py id 6873
```
**结果**:
```
✓ 书源已学习过，跳过: 6873
```

### 测试3: 从文件学习并删除
```bash
curl -s "https://www.yck2026.top/yuedu/shuyuan/json/id/6874.json" -o /tmp/test_source_6874.json
python scripts/book_source_learner.py json /tmp/test_source_6874.json --file
```
**结果**:
```
✓ 成功学习文件: /tmp/test_source_6874.json（原始文件已删除）
✓ 文件已删除: /tmp/test_source_6874.json
```

### 测试4: 学习爬虫跳过已学习
```bash
python scripts/learning_crawler.py --once --category "书源"
```
**结果**:
```
✓ 发现新书源: 📖Lofter (ID: 6873)
✓ 书源已学习过，跳过: 6873
✓ 成功学习: 📖Lofter (ID: 6873)
```

### 测试5: 主爬虫跳过已学习
```bash
python scripts/legado_source_crawler.py --category "书源" --once --force
```
**结果**:
```
✓ 解析书源: 📖Lofter (ID: 6873)
✓ 跳过已学习的书源: 📖Lofter (ID: 6873)
✓ 书源已保存: VirtualTaboo直播 (ID: 6947)  # 未学习的书源正常保存
```

## 📊 效果对比

### 更新前
- ❌ 学习后保留原始文件（占用空间）
- ❌ 重复学习相同书源（浪费资源）
- ❌ 爬虫重复下载已学习的书源（浪费时间）

### 更新后
- ✅ 学习后自动删除原始文件（节省空间）
- ✅ 智能跳过已学习书源（提高效率）
- ✅ 爬虫只下载未学习的书源（减少请求）

## 🎯 使用建议

### 1. 已学习记录管理
- 记录文件自动生成，无需手动管理
- 如需重置，可删除 `assets/learned_sources.json`

### 2. 调试模式
- 查看已学习记录：
  ```bash
  cat assets/learned_sources.json
  ```

- 查看已学习书源列表：
  ```python
  from scripts.reference_learning_module import ReferenceLearningModule
  module = ReferenceLearningModule()
  sources = module.get_learned_sources()
  print(sources)
  ```

### 3. 强制重新学习
- 如需强制重新学习某个书源：
  1. 从 `assets/learned_sources.json` 中删除对应记录
  2. 重新运行学习命令

## 📌 注意事项

1. **删除不可逆** - 原始文件删除后无法恢复
2. **记录文件安全** - `learned_sources.json` 包含学习历史，请勿随意删除
3. **ID唯一性** - 书源ID是判断重复的关键，确保ID正确提取
4. **URL映射** - 系统会自动建立URL到ID的映射关系

## 🚀 性能提升

| 指标 | 更新前 | 更新后 | 提升 |
|------|--------|--------|------|
| 重复学习检查 | 无 | O(1) | - |
| 磁盘占用 | 2倍（原始+学习） | 1倍（仅学习） | 50% |
| 网络请求 | 每次都下载 | 跳过已学习 | 显著减少 |
| 学习时间 | 包含重复学习 | 智能跳过 | 明显减少 |

## 📅 更新日期
2026-02-18

## 👨‍💻 维护者
Coze Coding Agent
