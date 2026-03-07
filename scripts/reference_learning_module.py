"""
参考学习模块
将爬取到的书源自动导入到知识库中，供AI学习
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ReferenceLearningModule:
    """参考学习模块"""

    def __init__(self, knowledge_base_dir="assets/knowledge_base", learned_record_file="assets/learned_sources.json"):
        """
        初始化参考学习模块

        Args:
            knowledge_base_dir: 知识库存储目录
            learned_record_file: 已学习记录文件路径
        """
        self.knowledge_base_dir = knowledge_base_dir
        self.learned_record_file = learned_record_file
        self._init_directories()
        self._init_learned_record()
    
    def _init_directories(self):
        """初始化目录结构"""
        directories = [
            self.knowledge_base_dir,
            os.path.join(self.knowledge_base_dir, "book_sources"),
            os.path.join(self.knowledge_base_dir, "book_source_collections"),
            os.path.join(self.knowledge_base_dir, "rss_sources"),
            os.path.join(self.knowledge_base_dir, "rss_source_collections"),
            os.path.join(self.knowledge_base_dir, "learning_stats"),
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        logger.info(f"参考学习目录已初始化: {self.knowledge_base_dir}")

    def _init_learned_record(self):
        """初始化已学习记录"""
        try:
            if not os.path.exists(self.learned_record_file):
                # 创建目录
                os.makedirs(os.path.dirname(self.learned_record_file), exist_ok=True)
                # 初始化空记录
                with open(self.learned_record_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "sources": {},  # source_id -> 学习信息
                        "urls": {},     # url -> source_id 映射
                        "last_update": None
                    }, f, indent=2, ensure_ascii=False)
                logger.info(f"已学习记录已初始化: {self.learned_record_file}")
        except Exception as e:
            logger.error(f"初始化已学习记录失败: {e}")

    def _load_learned_record(self) -> dict:
        """加载已学习记录"""
        try:
            if os.path.exists(self.learned_record_file):
                with open(self.learned_record_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"sources": {}, "urls": {}, "last_update": None}
        except Exception as e:
            logger.error(f"加载已学习记录失败: {e}")
            return {"sources": {}, "urls": {}, "last_update": None}

    def _save_learned_record(self, record: dict):
        """保存已学习记录"""
        try:
            os.makedirs(os.path.dirname(self.learned_record_file), exist_ok=True)
            with open(self.learned_record_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存已学习记录失败: {e}")

    def is_learned(self, source_id: str = None, url: str = None) -> bool:
        """
        检查书源是否已学习

        Args:
            source_id: 书源ID
            url: 书源URL

        Returns:
            是否已学习
        """
        record = self._load_learned_record()

        # 优先检查source_id
        if source_id and source_id in record.get("sources", {}):
            return True

        # 检查URL
        if url and url in record.get("urls", {}):
            return True

        return False

    def mark_as_learned(self, source_id: str, source_data: dict, source_url: str = None, original_file: str = None):
        """
        标记书源为已学习

        Args:
            source_id: 书源ID
            source_data: 书源数据
            source_url: 书源URL
            original_file: 原始文件路径（可选，用于删除）
        """
        try:
            record = self._load_learned_record()

            # 记录书源信息
            record["sources"][source_id] = {
                "name": source_data.get("bookSourceName", "未知"),
                "url": source_url,
                "learned_at": datetime.now().isoformat(),
                "original_file": original_file
            }

            # 记录URL映射
            if source_url:
                record["urls"][source_url] = source_id

            # 更新最后更新时间
            record["last_update"] = datetime.now().isoformat()

            # 保存记录
            self._save_learned_record(record)

            logger.info(f"书源已标记为已学习: {source_id}")

            # 删除原始文件（如果指定）
            if original_file and os.path.exists(original_file):
                try:
                    os.remove(original_file)
                    logger.info(f"已删除原始文件: {original_file}")
                except Exception as e:
                    logger.warning(f"删除原始文件失败: {e}")

        except Exception as e:
            logger.error(f"标记书源失败: {e}")

    def get_learned_sources(self) -> list:
        """
        获取已学习的书源列表

        Returns:
            已学习书源列表
        """
        record = self._load_learned_record()
        sources = []

        for source_id, info in record.get("sources", {}).items():
            sources.append({
                "id": source_id,
                "name": info.get("name"),
                "url": info.get("url"),
                "learned_at": info.get("learned_at")
            })

        return sources

    def clear_learned_record(self):
        """清空已学习记录（慎用）"""
        try:
            record = {
                "sources": {},
                "urls": {},
                "last_update": None
            }
            self._save_learned_record(record)
            logger.warning("已学习记录已清空")
        except Exception as e:
            logger.error(f"清空已学习记录失败: {e}")
    
    def _generate_knowledge_doc(self, source_data: dict, source_info: dict) -> str:
        """
        生成知识库文档内容
        
        Args:
            source_data: 书源数据
            source_info: 书源信息
        
        Returns:
            知识库文档内容
        """
        if isinstance(source_data, list) and len(source_data) > 0:
            first_source = source_data[0]
        elif isinstance(source_data, dict):
            first_source = source_data
        else:
            return None
        
        book_name = first_source.get('bookSourceName', '未知书源')
        book_url = first_source.get('bookSourceUrl', '')
        book_type = first_source.get('bookSourceType', 0)
        
        # 书源类型映射
        type_map = {0: "文本", 1: "音频", 2: "图片", 3: "文件", 4: "视频"}
        type_name = type_map.get(book_type, "未知")
        
        knowledge_content = f"""# {book_name}

## 基本信息
- **书源名称**: {book_name}
- **书源地址**: {book_url}
- **书源分组**: {first_source.get('bookSourceGroup', '未分类')}
- **书源类型**: {type_name} ({book_type})
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **来源**: {source_info.get('link', '未知')}
- **发布时间**: {source_info.get('pub_time', '未知')}
- **下载次数**: {source_info.get('download_count', '未知')}

## 书源描述
{source_info.get('description', '暂无描述')}

## 规则配置

### 搜索规则
```json
{json.dumps(first_source.get('ruleSearch', {}), indent=2, ensure_ascii=False)}
```

### 发现规则
```json
{json.dumps(first_source.get('ruleExplore', {}), indent=2, ensure_ascii=False)}
```

### 详情规则
```json
{json.dumps(first_source.get('ruleBookInfo', {}), indent=2, ensure_ascii=False)}
```

### 目录规则
```json
{json.dumps(first_source.get('ruleToc', {}), indent=2, ensure_ascii=False)}
```

### 正文规则
```json
{json.dumps(first_source.get('ruleContent', {}), indent=2, ensure_ascii=False)}
```

## 完整书源JSON
```json
{json.dumps(first_source, indent=2, ensure_ascii=False)}
```

## 学习要点

### 1. 选择器规则分析
- **搜索列表**: {first_source.get('ruleSearch', {}).get('bookList', '未配置')}
- **章节列表**: {first_source.get('ruleToc', {}).get('chapterList', '未配置')}
- **正文内容**: {first_source.get('ruleContent', {}).get('content', '未配置')}

### 2. 规则类型
- **CSS选择器**: 使用 `@text`、`@ownText`、`@html` 等提取类型
- **XPath规则**: 使用 `xpath:` 前缀
- **JSONPath规则**: 使用 `$` 符号
- **正则表达式**: 使用 `##pattern##replacement` 格式
- **JavaScript规则**: 使用 `@js:` 或 `java.` 前缀

### 3. 特殊配置
- **登录功能**: {'是' if first_source.get('loginUrl') else '否'}
- **Cookie管理**: {'是' if first_source.get('enabledCookieJar') else '否'}
- **并发控制**: {first_source.get('concurrentRate', '未配置')}
- **自定义请求头**: {'是' if first_source.get('header') else '否'}

### 4. 性能优化
- **响应时间**: {first_source.get('respondTime', 180000) / 1000:.0f} 秒
- **智能权重**: {first_source.get('weight', 0)}

## 适用场景
- 小说阅读
- 漫画浏览
- 有声书收听
- 其他资源获取

## 标签
#书源 #阅读 #Legado #{type_name}

---
*本文档由参考学习模块自动生成*
"""
        
        return knowledge_content
    
    def _generate_filename(self, source_id: str, book_name: str, category: str) -> str:
        """
        生成文件名
        
        Args:
            source_id: 原始书源ID
            book_name: 书源名称
            category: 分类
        
        Returns:
            文件名
        """
        # 清理文件名
        safe_name = book_name.replace('/', '_').replace('\\', '_')
        safe_name = safe_name.replace(':', '').replace('*', '')
        safe_name = safe_name.replace('?', '').replace('"', '')
        safe_name = safe_name.replace('<', '').replace('>', '').replace('|', '')
        
        # 添加时间戳和分类
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 使用原始ID作为文件名的主要部分
        return f"{source_id}_{safe_name}_{category}_{timestamp}.md"
    
    def _save_knowledge_doc(self, content: str, category: str, filename: str) -> str:
        """
        保存知识库文档
        
        Args:
            content: 文档内容
            category: 分类
            filename: 文件名
        
        Returns:
            保存路径
        """
        # 确定保存目录
        category_map = {
            "书源": "book_sources",
            "书源合集": "book_source_collections",
            "订阅源": "rss_sources",
            "订阅源合集": "rss_source_collections",
        }
        
        subdir = category_map.get(category, "book_sources")
        save_path = os.path.join(self.knowledge_base_dir, subdir, filename)
        
        # 保存文件
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"知识库文档已保存: {save_path}")
        return save_path
    
    def _update_learning_stats(self, category: str, count: int):
        """
        更新学习统计
        
        Args:
            category: 分类
            count: 数量
        """
        stats_file = os.path.join(self.knowledge_base_dir, "learning_stats", "stats.json")
        
        try:
            # 读取现有统计
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {}
            
            # 更新统计
            if category not in stats:
                stats[category] = {
                    "total_learned": 0,
                    "last_update": None
                }
            
            stats[category]["total_learned"] += count
            stats[category]["last_update"] = datetime.now().isoformat()
            stats["last_global_update"] = datetime.now().isoformat()
            
            # 保存统计
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"学习统计已更新: {category} +{count}")
            
        except Exception as e:
            logger.error(f"更新学习统计失败: {e}")
    
    def learn_book_source(self, source_data: dict, source_info: dict, category: str, mark_learned: bool = True) -> bool:
        """
        学习书源

        Args:
            source_data: 书源数据
            source_info: 书源信息（包含link、pub_time、description、source_id等）
            category: 分类
            mark_learned: 是否标记为已学习（默认True）

        Returns:
            是否成功
        """
        try:
            # 检查是否已学习
            source_id = source_info.get('source_id', 'unknown')
            if mark_learned and self.is_learned(source_id=source_id):
                logger.info(f"书源已学习过，跳过: {source_id}")
                return True

            # 生成知识库文档
            knowledge_content = self._generate_knowledge_doc(source_data, source_info)

            if not knowledge_content:
                logger.warning("生成知识库文档失败")
                return False

            # 生成文件名
            if isinstance(source_data, list) and len(source_data) > 0:
                book_name = source_data[0].get('bookSourceName', '未知书源')
                source_url = source_data[0].get('bookSourceUrl', '')
            elif isinstance(source_data, dict):
                book_name = source_data.get('bookSourceName', '未知书源')
                source_url = source_data.get('bookSourceUrl', '')
            else:
                book_name = "未知书源"
                source_url = ''

            filename = self._generate_filename(source_id, book_name, category)

            # 保存知识库文档
            save_path = self._save_knowledge_doc(knowledge_content, category, filename)

            if save_path:
                # 更新学习统计
                self._update_learning_stats(category, 1)
                logger.info(f"成功学习书源: {book_name} (ID: {source_id})")

                # 标记为已学习
                if mark_learned:
                    original_file = source_info.get('original_file')
                    self.mark_as_learned(source_id, source_data if isinstance(source_data, dict) else source_data[0], source_url, original_file)

                return True
            else:
                return False

        except Exception as e:
            logger.error(f"学习书源失败: {e}")
            return False
    
    def batch_learn(self, sources: list, category: str):
        """
        批量学习书源
        
        Args:
            sources: 书源列表
            category: 分类
        """
        logger.info(f"开始批量学习，共 {len(sources)} 个书源")
        
        success_count = 0
        fail_count = 0
        
        for source in sources:
            source_data = source.get('data')
            source_info = {
                'link': source.get('link'),
                'pub_time': source.get('pub_time'),
                'description': source.get('description'),
                'download_count': 0  # 可以从网页中提取
            }
            
            if self.learn_book_source(source_data, source_info, category):
                success_count += 1
            else:
                fail_count += 1
        
        logger.info(f"批量学习完成，成功 {success_count}，失败 {fail_count}")
        
        return {
            "total": len(sources),
            "success": success_count,
            "fail": fail_count
        }
    
    def get_learning_stats(self) -> dict:
        """
        获取学习统计
        
        Returns:
            学习统计数据
        """
        stats_file = os.path.join(self.knowledge_base_dir, "learning_stats", "stats.json")
        
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"获取学习统计失败: {e}")
            return {}
    
    def export_learning_summary(self) -> str:
        """
        导出学习摘要
        
        Returns:
            学习摘要内容
        """
        stats = self.get_learning_stats()
        
        summary = f"""# 参考学习摘要

## 总体统计
- 最后更新: {stats.get('last_global_update', '未知')}
- 总学习书源数: {sum(s.get('total_learned', 0) for s in stats.values() if isinstance(s, dict))}

## 分类统计

"""
        
        for category, data in stats.items():
            if category == "last_global_update":
                continue
            
            if isinstance(data, dict):
                summary += f"### {category}\n"
                summary += f"- 已学习: {data.get('total_learned', 0)} 个\n"
                summary += f"- 最后更新: {data.get('last_update', '未知')}\n\n"
        
        # 添加最近的文档
        summary += "## 最近学习的书源\n\n"
        
        for subdir in ["book_sources", "book_source_collections", "rss_sources", "rss_source_collections"]:
            category_dir = os.path.join(self.knowledge_base_dir, subdir)
            if os.path.exists(category_dir):
                files = sorted(Path(category_dir).glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                if files:
                    summary += f"### {subdir}\n\n"
                    for file in files:
                        summary += f"- {file.name}\n"
                    summary += "\n"
        
        # 保存摘要
        summary_path = os.path.join(self.knowledge_base_dir, "learning_summary.md")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"学习摘要已导出: {summary_path}")
        
        return summary
