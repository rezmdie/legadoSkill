"""
智能目录页分析器 - 随机应变版
集成智能分析引擎，根据知识库自适应分析HTML结构
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Any

# 从utils模块导入（utils在PYTHONPATH中）
from utils.html_structure_analyzer import HTMLStructureAnalyzer
from utils.knowledge_based_analyzer import KnowledgeBasedAnalyzer
from utils.multi_mode_extractor import MultiModeExtractor, SmartExtractionStrategy
from utils.rule_validator import RuleValidator


class SmartTOCAnalyzer:
    """智能目录页分析器"""
    
    def __init__(self, url: str, html: str):
        self.url = url
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        
        # 初始化智能引擎（强制使用规则模式）
        self.structure_analyzer = HTMLStructureAnalyzer(html, use_ai=False)
        self.knowledge_analyzer = KnowledgeBasedAnalyzer()
        self.extractor = MultiModeExtractor(html)
        self.smart_strategy = SmartExtractionStrategy(html)
        self.validator = RuleValidator(html)
        
        # 分析结果
        self.structure = None
        self.elements = {}
    
    def analyze(self) -> Dict[str, Any]:
        """执行智能分析"""
        # 1. 分析HTML结构
        self.structure = self.structure_analyzer.analyze_structure()
        
        # 2. 识别关键元素
        self.elements = {
            'chapter_list': self._analyze_chapter_list(),
            'chapter_items': self._analyze_chapter_items(),
            'pagination': self._analyze_pagination(),
            'volume_info': self._analyze_volume_info()
        }
        
        return {
            'url': self.url,
            'html': self.html,
            'structure': self.structure,
            'elements': self.elements
        }
    
    def _analyze_chapter_list(self) -> Dict[str, Any]:
        """分析章节列表容器"""
        # 使用知识库分析
        knowledge_result = self.knowledge_analyzer.analyze_with_knowledge(
            self.html,
            'list',
            '章节列表容器'
        )
        
        # 智能提取
        extraction_result = self.smart_strategy.extract_with_strategy('list')
        
        # 结构分析
        lists = self.structure['key_elements'].get('lists', [])
        
        # 合并候选
        candidates = []
        
        # 知识库推荐
        for rec in knowledge_result.recommended_selectors:
            candidates.append({
                'selector': rec['selector'],
                'confidence': rec['confidence'],
                'source': 'knowledge',
                'pattern_reference': rec.get('pattern_reference', ''),
                'xpath': rec.get('xpath', '')
            })
        
        # 智能提取结果
        if extraction_result.get('best_result'):
            best = extraction_result['best_result']
            if not any(c['selector'] == best['selector'] for c in candidates):
                candidates.append({
                    'selector': best['selector'],
                    'confidence': best['confidence'],
                    'source': 'extraction',
                    'strategy': best['strategy']
                })
        
        # 结构分析结果
        for list_elem in lists:
            if not any(c['selector'] == list_elem.selector for c in candidates):
                candidates.append({
                    'selector': list_elem.selector,
                    'confidence': list_elem.confidence,
                    'source': 'structure',
                    'item_count': list_elem.child_count
                })
        
        # 验证候选
        validated = self._validate_list_candidates(candidates)
        
        return {
            'description': '章节列表容器',
            'candidates': validated,
            'knowledge_references': knowledge_result.knowledge_references,
            'reasoning': knowledge_result.reasoning,
            'warnings': knowledge_result.warnings,
            'best_selector': validated[0]['selector'] if validated else None,
            'confidence': validated[0]['confidence'] if validated else 0.0
        }
    
    def _analyze_chapter_items(self) -> Dict[str, Any]:
        """分析章节项"""
        candidates = []
        
        # 常见的章节项选择器模式
        patterns = [
            'li a',
            'li',
            '.chapter-item a',
            '.chapter a',
            '.list-item a',
            '.item a'
        ]
        
        for pattern in patterns:
            try:
                test_result = self.extractor.extract(
                    selector=pattern,
                    method='css',
                    extract_attr='href',
                    extract_all=True
                )
                
                if test_result.success and test_result.extracted_count > 0:
                    candidates.append({
                        'selector': pattern,
                        'confidence': min(test_result.confidence * 1.2, 1.0),
                        'source': 'pattern',
                        'extracted_count': test_result.extracted_count,
                        'sample_items': test_result.sample_items[:5]
                    })
            except:
                pass
        
        # 验证候选
        validated = self._validate_item_candidates(candidates)
        
        return {
            'description': '章节项',
            'candidates': validated,
            'best_selector': validated[0]['selector'] if validated else None,
            'confidence': validated[0]['confidence'] if validated else 0.0
        }
    
    def _analyze_pagination(self) -> Dict[str, Any]:
        """分析分页信息"""
        candidates = []
        
        # 常见的分页选择器
        patterns = [
            '.pagination a',
            '.page a',
            '.next-page',
            '.prev-page',
            'a[href*="page"]'
        ]
        
        for pattern in patterns:
            try:
                test_result = self.extractor.extract(
                    selector=pattern,
                    method='css',
                    extract_attr='href',
                    extract_all=True
                )
                
                if test_result.success and test_result.extracted_count > 0:
                    candidates.append({
                        'selector': pattern,
                        'confidence': test_result.confidence,
                        'source': 'pattern',
                        'extracted_count': test_result.extracted_count
                    })
            except:
                pass
        
        return {
            'description': '分页信息',
            'candidates': candidates,
            'has_pagination': len(candidates) > 0
        }
    
    def _analyze_volume_info(self) -> Dict[str, Any]:
        """分析分卷信息"""
        candidates = []
        
        # 查找可能的分卷标题
        volume_patterns = [
            'h3',
            'h4',
            '.volume',
            '.book-volume',
            '.part',
            '.section-title'
        ]
        
        for pattern in volume_patterns:
            try:
                test_result = self.extractor.extract(
                    selector=pattern,
                    method='css',
                    extract_attr=None,
                    extract_all=True
                )
                
                if test_result.success:
                    # 检查是否包含卷、篇等关键词
                    filtered = [
                        item for item in test_result.sample_items or []
                        if any(kw in item for kw in ['卷', '篇', '部', '分'])
                    ]
                    
                    if filtered:
                        candidates.append({
                            'selector': pattern,
                            'confidence': test_result.confidence,
                            'source': 'pattern',
                            'sample_items': filtered[:3]
                        })
            except:
                pass
        
        return {
            'description': '分卷信息',
            'candidates': candidates,
            'has_volume': len(candidates) > 0
        }
    
    def _validate_list_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """验证列表候选"""
        validated = []
        
        for candidate in candidates:
            selector = candidate['selector']
            
            try:
                test_result = self.extractor.extract(
                    selector=selector,
                    method='css',
                    extract_all=True
                )
                
                candidate['test_success'] = test_result.success
                candidate['test_confidence'] = test_result.confidence
                candidate['extracted_count'] = len(test_result.content) if isinstance(test_result.content, list) else 1
                
                # 列表应该包含多个子元素
                if candidate['extracted_count'] >= 3:
                    candidate['is_valid'] = True
                else:
                    candidate['is_valid'] = False
                    candidate['warning'] = '列表项数量过少'
                
                validated.append(candidate)
            except Exception as e:
                candidate['test_success'] = False
                candidate['test_error'] = str(e)
                validated.append(candidate)
        
        # 重新排序
        validated.sort(key=lambda x: (
            x.get('test_confidence', 0) *
            (1.5 if x.get('is_valid', False) else 0.5)
        ), reverse=True)
        
        return validated
    
    def _validate_item_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """验证章节项候选"""
        validated = []
        
        for candidate in candidates:
            selector = candidate['selector']
            
            try:
                test_result = self.extractor.extract(
                    selector=selector,
                    method='css',
                    extract_attr='href',
                    extract_all=True
                )
                
                candidate['test_success'] = test_result.success
                candidate['test_confidence'] = test_result.confidence
                candidate['extracted_count'] = test_result.extracted_count
                candidate['sample_items'] = test_result.sample_items or []
                
                # 章节项应该有链接
                if candidate['extracted_count'] >= 5:
                    candidate['is_valid'] = True
                else:
                    candidate['is_valid'] = False
                
                validated.append(candidate)
            except Exception as e:
                candidate['test_success'] = False
                candidate['test_error'] = str(e)
                validated.append(candidate)
        
        validated.sort(key=lambda x: x.get('test_confidence', 0), reverse=True)
        
        return validated
    
    def generate_rules(self) -> Dict[str, str]:
        """生成推荐规则"""
        rules = {}
        
        # 章节列表
        chapter_list = self.elements.get('chapter_list', {})
        best_list = chapter_list.get('best_selector')
        if best_list:
            rules['ruleContent'] = best_list
        
        # 章节名称
        chapter_items = self.elements.get('chapter_items', {})
        best_items = chapter_items.get('best_selector')
        if best_items:
            rules['chapterName'] = best_items + '@text'
        
        # 章节链接
        if best_items:
            rules['chapterUrl'] = best_items + '@href'
        
        return rules


@tool
def analyze_toc_page(
    url: str,
    runtime: ToolRuntime = None
) -> str:
    """
    [START] 智能目录页分析器 - 随机应变版
    
    功能特点：
    - [OK] 获取真实HTML源代码
    - [OK] 深度分析HTML结构
    - [OK] 智能识别章节列表容器
    - [OK] 智能识别章节项
    - [OK] 检测分页和分卷信息
    - [OK] 基于知识库自适应分析
    
    参数:
        url: 目录页的完整URL
    
    返回:
        完整的分析报告
    """
    ctx = runtime.context if runtime else new_context(method="analyze_toc_page")
    
    try:
        # 获取真实HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        html = response.text
        
        # 创建智能分析器
        analyzer = SmartTOCAnalyzer(url, html)
        
        # 执行智能分析
        analysis = analyzer.analyze()
        
        # 生成规则
        recommended_rules = analyzer.generate_rules()
        
        # 构建报告
        report = f"""
## 📑 智能目录页分析报告 - 随机应变版

### 📍 页面信息
- **URL**: {url}
- **状态**: {'[OK] 成功' if response.status_code == 200 else f'[ERROR] {response.status_code}'}
- **编码**: {response.encoding}
- **HTML大小**: {len(html)} 字符
- **页面类型**: {analysis['structure'].get('page_type', 'unknown')}

---

### 🧠 智能分析引擎工作日志

#### 第1步：HTML结构深度分析
- **页面类型识别**: {analysis['structure'].get('page_type', 'unknown')}
- **关键元素数量**:
  - 标题: {len(analysis['structure']['key_elements'].get('titles', []))}
  - 列表: {len(analysis['structure']['key_elements'].get('lists', []))}
  - 链接: {len(analysis['structure']['key_elements'].get('links', []))}

#### 第2步：知识库模式匹配
"""

        # 添加章节列表的知识库推理
        chapter_list = analysis['elements']['chapter_list']
        if chapter_list.get('knowledge_references'):
            report += f"""
**章节列表容器**:
- 匹配模式: {', '.join(chapter_list['knowledge_references'])}
- 推理过程:
```
{chapter_list['reasoning']}
```
"""

        # 添加元素识别结果
        report += f"""
---

### [SEARCH] 智能元素识别结果

#### 📚 章节列表容器
"""
        for i, candidate in enumerate(chapter_list['candidates'][:3], 1):
            test_status = '[OK]' if candidate.get('test_success') else '[ERROR]'
            is_valid = '[OK]' if candidate.get('is_valid') else '[ERROR]'
            report += f"""
**候选 {i}** {test_status} {is_valid}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **提取数量**: {candidate.get('extracted_count', 0)}
"""

        chapter_items = analysis['elements']['chapter_items']
        report += f"""
#### [NOTE] 章节项
"""
        for i, candidate in enumerate(chapter_items['candidates'][:3], 1):
            test_status = '[OK]' if candidate.get('test_success') else '[ERROR]'
            report += f"""
**候选 {i}** {test_status}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f}
- **提取数量**: {candidate.get('extracted_count', 0)}
- **样本**:
"""
            for item in candidate.get('sample_items', [])[:3]:
                report += f"  - {item[:60]}\n"

        # 分页信息
        pagination = analysis['elements']['pagination']
        if pagination.get('has_pagination'):
            report += f"""
#### [DOC] 分页信息
检测到分页功能！
"""
            for candidate in pagination['candidates'][:3]:
                report += f"- 选择器: `{candidate['selector']}`\n"

        # 分卷信息
        volume = analysis['elements']['volume_info']
        if volume.get('has_volume'):
            report += f"""
#### 📖 分卷信息
检测到分卷！
"""
            for candidate in volume['candidates'][:3]:
                report += f"- 选择器: `{candidate['selector']}`\n"

        # 推荐规则
        report += f"""
---

### [TARGET] 推荐的目录规则

```json
{json.dumps(recommended_rules, ensure_ascii=False, indent=2)}
```

---

### [TIP] 智能建议

1. **验证列表容器**: 确保选择器正确匹配包含所有章节的容器
2. **验证章节项**: 检查章节名称和链接是否正确提取
3. **处理分页**: 如果有分页，需要配置下一页规则
4. **处理分卷**: 如果有分卷，可能需要特殊处理

**下一步操作**:
1. 复制上述规则到书源配置
2. 验证章节列表是否完整
3. 测试章节链接是否有效

---

### [DOC] 完整HTML源代码（供深度分析）

```html
{html}
```
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## [ERROR] 分析失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""
