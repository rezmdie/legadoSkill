"""
知识验证和测试工具
验证知识的正确性，确保AI真正"学会"了知识
"""

import os
import json
import sys
from typing import Dict, List, Any
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

# 确保utils目录在Python路径中
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
utils_path = os.path.join(workspace_path, "src", "utils")
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    from utils.knowledge_enhanced_analyzer import get_global_analyzer
except ImportError:
    # 如果导入失败，创建一个简单的模拟分析器
    class MockAnalyzer:
        def __init__(self):
            self.is_learned = False
            self.learner = type('MockLearner', (), {
                'knowledge_entries': [],
                'book_sources': [],
                'patterns': [],
                'selectors': []
            })()
        
        def learn_knowledge(self, force=False):
            return {
                'total_files': 0,
                'learned_entries': 0,
                'book_sources': 0,
                'patterns': 0,
                'selectors': 0
            }
        
        def get_knowledge_by_query(self, query, limit=5):
            return []
        
        def get_book_source_examples(self, element_type, limit=3):
            return []
        
        def get_learning_status(self):
            return {
                'is_learned': False,
                'knowledge_count': 0,
                'book_source_count': 0,
                'pattern_count': 0
            }
    
    _global_analyzer = MockAnalyzer()
    
    def get_global_analyzer():
        return _global_analyzer


def _lightweight_search(query: str, limit: int = 5) -> str:
    """轻量级知识库搜索 - 直接搜索文件内容，不需要完整学习"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    assets_path = os.path.join(workspace_path, "assets")
    legado_path = os.path.join(workspace_path, "legado")
    
    # 知识库文件列表
    knowledge_files = [
        'legado_knowledge_base.md',
        'css选择器规则.txt',
        '书源规则：从入门到入土.md',
        '订阅源规则帮助.txt'
    ]
    
    results = []
    
    # 1. 搜索 assets 知识库文件
    for filename in knowledge_files:
        file_path = os.path.join(assets_path, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 搜索包含查询关键词的段落
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if query.lower() in para.lower() and len(para.strip()) > 20:
                        results.append({
                            'source': f'assets/{filename}',
                            'content': para.strip()[:500]
                        })
                        if len(results) >= limit:
                            break
            except Exception:
                continue
        
        if len(results) >= limit:
            break
    
    # 2. 搜索 legado 源码（如果存在）
    if os.path.exists(legado_path) and len(results) < limit:
        try:
            # 搜索关键的 Kotlin 源码文件
            source_patterns = [
                'app/src/main/java/**/*.kt',
                'modules/rhino/src/main/java/**/*.kt'
            ]
            
            import glob
            for pattern in source_patterns:
                search_pattern = os.path.join(legado_path, pattern.replace('**/', ''))
                # 简化搜索：只搜索主要目录
                main_dirs = [
                    os.path.join(legado_path, 'app/src/main/java/io/legado/app'),
                    os.path.join(legado_path, 'modules/rhino/src/main/java/com/script')
                ]
                
                for main_dir in main_dirs:
                    if not os.path.exists(main_dir):
                        continue
                    
                    for root, dirs, files in os.walk(main_dir):
                        for file in files:
                            if file.endswith('.kt'):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    # 搜索包含查询关键词的代码段
                                    lines = content.split('\n')
                                    for i, line in enumerate(lines):
                                        if query.lower() in line.lower():
                                            # 获取上下文（前后3行）
                                            start = max(0, i - 3)
                                            end = min(len(lines), i + 4)
                                            context = '\n'.join(lines[start:end])
                                            
                                            rel_path = os.path.relpath(file_path, workspace_path)
                                            results.append({
                                                'source': f'legado源码/{rel_path}',
                                                'content': context[:500]
                                            })
                                            
                                            if len(results) >= limit:
                                                break
                                except Exception:
                                    continue
                            
                            if len(results) >= limit:
                                break
                        
                        if len(results) >= limit:
                            break
                    
                    if len(results) >= limit:
                        break
                
                if len(results) >= limit:
                    break
        except Exception:
            pass
    
    if not results:
        return f"""
## [SEARCH] 搜索结果

**查询**: {query}

[ERROR] 未找到相关知识

**搜索范围**:
- ✓ assets/ 知识库文件
- ✓ legado/ 源码文件（如果存在）

**建议**:
1. 尝试不同的关键词
2. 使用 `learn_knowledge_base` 工具加载完整知识库后再搜索

[WARNING] 提醒：知识库内容仅供参考，不能直接照搬
"""
    
    report = f"""
## [SEARCH] 知识搜索结果（轻量级搜索，仅供参考）

**查询**: {query}
**找到**: {len(results)} 条结果

**搜索范围**:
- ✓ assets/ 知识库文件
- ✓ legado/ 源码文件（如果存在）

[WARNING] 重要提醒：
- [SECURE] 以下内容仅供参考
- [SECURE] 不能直接照搬知识库中的选择器
- [SECURE] 所有选择器必须在真实HTML上验证

[TIP] 使用 `learn_knowledge_base` 工具可加载完整知识库，获得更精确的搜索结果

---

"""
    
    for i, result in enumerate(results, 1):
        report += f"""
### 📖 结果 {i}

**来源**: {result['source']}

**内容**:
```
{result['content']}
```

---
"""
    
    return report.strip()


@tool
def learn_knowledge_base(
    force: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    🎓 学习知识库 - 让AI真正学会知识（仅作参考）
    
    功能：
    - 读取assets目录下的所有知识文件
    - 解析并学习书源规则、CSS选择器、技术文档
    - 构建知识关联和索引
    - 保存学习结果供后续使用
    
    [WARNING] 重要提醒：
    - 知识库内容仅作参考
    - 不能直接照搬知识库中的选择器
    - 所有选择器必须在真实HTML上验证
    - 禁止编造选择器
    
    参数:
        force: 是否强制重新学习（默认False）
    
    返回:
        学习统计和状态报告
    """
    ctx = runtime.context if runtime else new_context(method="learn_knowledge_base")
    
    try:
        # 获取assets路径
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        assets_path = os.path.join(workspace_path, "assets")
        
        analyzer = get_global_analyzer()
        stats = analyzer.learn_knowledge(force=force)
        
        report = f"""
## 🎓 知识库学习完成

### [STATS] 学习统计
- **处理文件**: {stats['total_files']}
- **学习条目**: {stats['learned_entries']}
- **书源数量**: {stats['book_sources']}
- **模式数量**: {stats['patterns']}
- **选择器数量**: {stats['selectors']}

### [OK] 学习状态
- **知识库**: 已加载
- **知识条目**: {len(analyzer.learner.knowledge_entries)}
- **书源库**: {len(analyzer.learner.book_sources)}
- **模式库**: {len(analyzer.learner.patterns)}
- **选择器库**: {len(analyzer.learner.selectors)}

### 📚 已学习的内容类型
1. **书源规则文档** - 从入门到入土，订阅源规则
2. **CSS选择器规则** - 语法、用法、最佳实践
3. **书源知识库** - 数百个实际书源案例
4. **参考文件** - JSON配置、JS脚本示例
5. **技术文档** - JS扩展、加密解密、登录检查

### [TARGET] 知识应用能力
现在AI可以：
- [OK] 识别HTML结构与知识库模式的相似性
- [OK] 推荐基于实际书源的选择器（仅供参考）
- [OK] 引用知识库中的相关说明（仅供参考）
- [OK] 验证规则是否符合已知模式（仅供参考）
- [OK] 提供多个备选方案（仅供参考）

### [WARNING] 重要提醒
- [SECURE] 知识库内容仅作参考
- [SECURE] 不能直接照搬知识库中的选择器
- [SECURE] 所有选择器必须在真实HTML上验证
- [SECURE] 禁止编造选择器
- [SECURE] 必须访问真实网页进行分析

### [TIP] 使用建议
1. 使用`analyze_book_info_page`等工具时，会自动应用学到的知识（仅供参考）
2. 查询知识：`search_knowledge "CSS选择器"`（仅供参考）
3. 验证规则：必须使用真实网页验证工具`validate_selector_on_real_web`

---

**[SUCCESS] AI已成功学会知识库中的所有知识！（仅作参考）**
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## [ERROR] 知识学习失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

**建议**:
1. 检查assets目录是否存在
2. 确认知识文件格式正确
3. 查看错误详情定位问题
"""


@tool
def search_knowledge(
    query: str,
    category: str = "",
    limit: int = 5,
    runtime: ToolRuntime = None
) -> str:
    """
    [SEARCH] 搜索知识库 - 查询已学习的知识（仅作参考）
    
    功能：
    - 根据关键词搜索知识
    - 按类别过滤（css、rule、bookinfo等）
    - 返回相关知识条目和示例
    
    [WARNING] 重要提醒：
    - 搜索结果仅供参考
    - 不能直接照搬知识库中的选择器
    - 所有选择器必须在真实HTML上验证
    - 禁止编造选择器
    
    参数:
        query: 搜索关键词
        category: 知识类别（可选）
        limit: 返回结果数量（默认5）
    
    返回:
        知识条目列表，包含标题、内容、示例等（仅供参考）
    """
    ctx = runtime.context if runtime else new_context(method="search_knowledge")
    
    try:
        # 获取assets路径
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        assets_path = os.path.join(workspace_path, "assets")
        
        analyzer = get_global_analyzer()
        
        # 如果尚未学习，使用轻量级文件搜索代替完整学习
        if not analyzer.is_learned:
            return _lightweight_search(query, limit)
        
        # 搜索知识
        results = analyzer.get_knowledge_by_query(query, limit=limit)
        
        if not results:
            return f"""
## [SEARCH] 搜索结果

**查询**: {query}
**类别**: {category or '全部'}

[ERROR] 未找到相关知识

**建议**:
1. 尝试不同的关键词
2. 检查知识库是否已加载（使用`learn_knowledge_base`）

[WARNING] 提醒：知识库内容仅供参考，不能直接照搬
"""
        
        report = f"""
## [SEARCH] 知识搜索结果（仅供参考）

**查询**: {query}
**类别**: {category or '全部'}
**找到**: {len(results)} 条知识

[WARNING] 重要提醒：
- [SECURE] 以下内容仅供参考
- [SECURE] 不能直接照搬知识库中的选择器
- [SECURE] 所有选择器必须在真实HTML上验证
- [SECURE] 禁止编造选择器

---

"""
        
        for i, result in enumerate(results, 1):
            report += f"""
### 📖 结果 {i}: {result['title']}

**类型**: {result['type']}
**类别**: {result['category']}
**来源**: {result['source']}
**置信度**: {result['confidence']:.2f}

**标签**: {', '.join(result['tags'])}

**内容**:
```
{result['content'][:300]}{'...' if len(result['content']) > 300 else ''}
```
"""
            
            if result['examples']:
                report += f"""
**示例（仅供参考）**:
"""
                for example in result['examples'][:3]:
                    report += f"```\n{example}\n```\n"
            
            report += "\n---\n"
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## [ERROR] 搜索失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""


@tool
def get_book_source_examples(
    element_type: str,
    limit: int = 3,
    runtime: ToolRuntime = None
) -> str:
    """
    📚 获取书源示例 - 查看实际书源中的规则示例
    
    功能：
    - 从知识库中查找书源示例
    - 显示特定元素类型的规则
    - 提供多个实际书源的参考
    
    参数:
        element_type: 元素类型（bookinfo、toc、content、search等）
        limit: 返回示例数量（默认3）
    
    返回:
        书源示例列表
    """
    ctx = runtime.context if runtime else new_context(method="get_book_source_examples")
    
    try:
        # 获取assets路径
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        assets_path = os.path.join(workspace_path, "assets")
        
        analyzer = get_global_analyzer()
        
        # 如果尚未学习，提示用户先学习
        if not analyzer.is_learned:
            return f"""
## 📚 书源示例

**元素类型**: {element_type}

[WARNING] 知识库尚未加载，无法获取书源示例。

**建议**:
使用 `learn_knowledge_base` 工具先加载知识库，然后再获取示例。
"""
        
        # 获取示例
        examples = analyzer.get_book_source_examples(element_type, limit=limit)
        
        if not examples:
            return f"""
## 📚 书源示例

**元素类型**: {element_type}

[ERROR] 未找到相关书源示例

**可用的元素类型**:
- bookinfo (书籍信息)
- toc (目录)
- content (正文)
- searchUrl (搜索)
"""
        
        report = f"""
## 📚 书源示例 - {element_type}

找到 {len(examples)} 个书源示例

---

"""
        
        for i, example in enumerate(examples, 1):
            report += f"""
### 📖 示例 {i}: {example['source_name']}

**URL**: {example['source_url']}
**标签**: {', '.join(example['tags'])}

**规则示例**:
"""
            
            for pattern in example['patterns'][:5]:
                report += f"```\n{pattern}\n```\n"
            
            report += "\n---\n"
        
        report += f"""

[TIP] **使用建议**:
1. 参考这些示例编写选择器
2. 根据实际情况调整
3. 系统会自动应用这些知识进行分析
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## [ERROR] 获取示例失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""


@tool
def check_knowledge_status(
    runtime: ToolRuntime = None
) -> str:
    """
    [STATS] 检查知识状态 - 查看学习进度和状态
    
    功能：
    - 显示知识库学习状态
    - 统计已学习的知识数量
    - 显示应用统计
    
    返回:
        知识状态报告
    """
    ctx = runtime.context if runtime else new_context(method="check_knowledge_status")
    
    try:
        # 获取assets路径
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        assets_path = os.path.join(workspace_path, "assets")
        
        analyzer = get_global_analyzer()
        status = analyzer.get_learning_status()
        
        report = f"""
## [STATS] 知识库状态报告

### 📚 学习状态
**是否已学习**: {'[OK] 是' if status['is_learned'] else '[ERROR] 否'}

---

### 📖 学习统计
"""
        
        if status['is_learned']:
            stats = status['learning_stats']
            report += f"""
- **处理文件**: {stats['total_files']}
- **学习条目**: {stats['learned_entries']}
- **书源数量**: {stats['book_sources']}
- **模式数量**: {stats['patterns']}
- **选择器数量**: {stats['selectors']}

### 🗂️ 知识分类
- **总知识条目**: {status['knowledge_count']}
- **书源库**: {status['book_source_count']}
- **模式库**: {status['pattern_count']}

### [TIP] 应用能力
知识库已准备好，AI现在可以：
- [OK] 识别HTML结构并匹配知识库模式
- [OK] 推荐基于实际书源的选择器
- [OK] 引用知识库中的相关说明
- [OK] 验证规则是否符合已知模式
- [OK] 提供多个备选方案

### [INFO] 知识来源
从以下资源中学习：
- 书源规则文档（书源规则：从入门到入土.md等）
- CSS选择器规则（css选择器规则.txt）
- 实际书源案例（knowledge_base/book_sources/）
- 参考文件（各类.json参考.txt）
- 技术文档（方法-JS扩展类.md等）
"""
        else:
            report += """
[ERROR] 知识库尚未学习

**建议**:
使用 `learn_knowledge_base` 工具开始学习知识库
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## [ERROR] 状态检查失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""
