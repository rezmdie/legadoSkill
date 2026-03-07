"""
智能正文页分析器 - 随机应变版
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


class SmartContentAnalyzer:
    """智能正文页分析器"""
    
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
            'content': self._analyze_content(),
            'next_chapter': self._analyze_next_chapter(),
            'prev_chapter': self._analyze_prev_chapter(),
            'chapter_title': self._analyze_chapter_title()
        }
        
        return {
            'url': self.url,
            'html': self.html,
            'structure': self.structure,
            'elements': self.elements
        }
    
    def _analyze_content(self) -> Dict[str, Any]:
        """分析正文内容"""
        # 使用知识库分析
        knowledge_result = self.knowledge_analyzer.analyze_with_knowledge(
            self.html,
            'content',
            '正文内容'
        )
        
        # 智能提取
        extraction_result = self.smart_strategy.extract_with_strategy('content')
        
        # 结构分析
        containers = self.structure['key_elements'].get('containers', [])
        
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
        
        # 结构分析结果 - 过滤大容器
        for container in containers:
            if not any(c['selector'] == container.selector for c in candidates):
                # 正文容器应该有较多文本
                if container.text_length > 500:
                    candidates.append({
                        'selector': container.selector,
                        'confidence': container.confidence,
                        'source': 'structure',
                        'text_length': container.text_length
                    })
        
        # 验证候选
        validated = self._validate_content_candidates(candidates)
        
        return {
            'description': '正文内容',
            'candidates': validated,
            'knowledge_references': knowledge_result.knowledge_references,
            'reasoning': knowledge_result.reasoning,
            'warnings': knowledge_result.warnings,
            'best_selector': validated[0]['selector'] if validated else None,
            'confidence': validated[0]['confidence'] if validated else 0.0
        }
    
    def _analyze_next_chapter(self) -> Dict[str, Any]:
        """分析下一章链接"""
        candidates = []
        
        # 常见的下一章选择器
        patterns = [
            '.next-chapter a',
            '.next a',
            'a:contains("下一章")',
            'a:contains("下一页")',
            '.chapter-next a',
            '#next'
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
                    # 检查文本是否包含"下一章"
                    text_result = self.extractor.extract(
                        selector=pattern,
                        method='css',
                        extract_all=True
                    )
                    
                    is_next_chapter = False
                    if text_result.success and text_result.sample_items:
                        is_next_chapter = any(
                            '下一' in str(item) for item in text_result.sample_items
                        )
                    
                    candidates.append({
                        'selector': pattern,
                        'confidence': test_result.confidence * (1.5 if is_next_chapter else 1.0),
                        'source': 'pattern',
                        'is_next_chapter': is_next_chapter
                    })
            except:
                pass
        
        return {
            'description': '下一章链接',
            'candidates': candidates,
            'best_selector': candidates[0]['selector'] if candidates else None
        }
    
    def _analyze_prev_chapter(self) -> Dict[str, Any]:
        """分析上一章链接"""
        candidates = []
        
        # 常见的上一章选择器
        patterns = [
            '.prev-chapter a',
            '.prev a',
            'a:contains("上一章")',
            'a:contains("上一页")',
            '.chapter-prev a',
            '#prev'
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
                    # 检查文本是否包含"上一章"
                    text_result = self.extractor.extract(
                        selector=pattern,
                        method='css',
                        extract_all=True
                    )
                    
                    is_prev_chapter = False
                    if text_result.success and text_result.sample_items:
                        is_prev_chapter = any(
                            '上一' in str(item) for item in text_result.sample_items
                        )
                    
                    candidates.append({
                        'selector': pattern,
                        'confidence': test_result.confidence * (1.5 if is_prev_chapter else 1.0),
                        'source': 'pattern',
                        'is_prev_chapter': is_prev_chapter
                    })
            except:
                pass
        
        return {
            'description': '上一章链接',
            'candidates': candidates,
            'best_selector': candidates[0]['selector'] if candidates else None
        }
    
    def _analyze_chapter_title(self) -> Dict[str, Any]:
        """分析章节标题"""
        candidates = []
        
        # 常见的章节标题选择器
        patterns = [
            'h1',
            'h2',
            '.chapter-title',
            '#chapter-title',
            '.title',
            '#title'
        ]
        
        for pattern in patterns:
            try:
                test_result = self.extractor.extract(
                    selector=pattern,
                    method='css',
                    extract_all=True
                )
                
                if test_result.success and test_result.extracted_count > 0:
                    candidates.append({
                        'selector': pattern,
                        'confidence': test_result.confidence,
                        'source': 'pattern',
                        'sample_items': test_result.sample_items[:3]
                    })
            except:
                pass
        
        return {
            'description': '章节标题',
            'candidates': candidates,
            'best_selector': candidates[0]['selector'] if candidates else None
        }
    
    def _validate_content_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """验证正文候选"""
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
                
                # 获取内容分析
                if test_result.success and test_result.sample_items:
                    content = ' '.join(str(item) for item in test_result.sample_items)
                    content_length = len(content)
                    
                    candidate['content_length'] = content_length
                    candidate['extracted_count'] = len(test_result.content) if isinstance(test_result.content, list) else 1
                    
                    # 正文应该有足够的内容
                    if content_length >= 500:
                        candidate['is_valid'] = True
                    elif content_length >= 200:
                        candidate['is_valid'] = True
                        candidate['warning'] = '内容较短，请确认是否为完整正文'
                    else:
                        candidate['is_valid'] = False
                        candidate['warning'] = '内容过短，可能不是正文'
                else:
                    candidate['is_valid'] = False
                    candidate['warning'] = '提取失败'
                
                validated.append(candidate)
            except Exception as e:
                candidate['test_success'] = False
                candidate['test_error'] = str(e)
                validated.append(candidate)
        
        # 重新排序
        validated.sort(key=lambda x: (
            x.get('test_confidence', 0) *
            (2.0 if x.get('is_valid', False) else 0.3)
        ), reverse=True)
        
        return validated
    
    def generate_rules(self) -> Dict[str, str]:
        """生成推荐规则"""
        rules = {}
        
        # 正文内容
        content = self.elements.get('content', {})
        best_content = content.get('best_selector')
        if best_content:
            # 生成替换规则去除广告
            rules['content'] = best_content + '@text'
        
        # 下一章
        next_chapter = self.elements.get('next_chapter', {})
        best_next = next_chapter.get('best_selector')
        if best_next:
            rules['nextContentUrl'] = best_next + '@href'
        
        # 上一章
        prev_chapter = self.elements.get('prev_chapter', {})
        best_prev = prev_chapter.get('best_selector')
        if best_prev:
            rules['prevContentUrl'] = best_prev + '@href'
        
        return rules
    
    def generate_replace_rules(self) -> Dict[str, str]:
        """生成替换规则"""
        rules = {}
        
        # 常见的替换规则
        common_replaces = [
            '##<script.*?</script>##',
            '##<style.*?</style>##',
            '##<!--.*?-->##',
            '##广告.*?##',
            '##本章完.*?##'
        ]
        
        for i, replace in enumerate(common_replaces):
            rules[f'replace{i+1}'] = replace
        
        return rules


@tool
def analyze_content_page(
    url: str,
    runtime: ToolRuntime = None
) -> str:
    """
    [START] 智能正文页分析器 - 随机应变版
    
    功能特点：
    - [OK] 获取真实HTML源代码
    - [OK] 深度分析HTML结构
    - [OK] 智能识别正文容器
    - [OK] 智能识别章节导航
    - [OK] 自动生成替换规则
    - [OK] 基于知识库自适应分析
    
    参数:
        url: 正文页的完整URL
    
    返回:
        完整的分析报告
    """
    ctx = runtime.context if runtime else new_context(method="analyze_content_page")
    
    try:
        # 获取真实HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        html = response.text
        
        # 创建智能分析器
        analyzer = SmartContentAnalyzer(url, html)
        
        # 执行智能分析
        analysis = analyzer.analyze()
        
        # 生成规则
        recommended_rules = analyzer.generate_rules()
        replace_rules = analyzer.generate_replace_rules()
        
        # 构建报告
        report = f"""
## [DOC] 智能正文页分析报告 - 随机应变版

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
- **内容密度**: 文本占比 {analysis['structure']['content_density'].get('text_ratio', 0):.2%}
- **链接密度**: {analysis['structure']['content_density'].get('link_density', 0):.2%}

#### 第2步：知识库模式匹配
"""

        # 添加正文的知识库推理
        content = analysis['elements']['content']
        if content.get('knowledge_references'):
            report += f"""
**正文内容**:
- 匹配模式: {', '.join(content['knowledge_references'])}
- 推理过程:
```
{content['reasoning']}
```
"""

        # 添加元素识别结果
        report += f"""
---

### [SEARCH] 智能元素识别结果

#### 📖 正文内容
"""
        for i, candidate in enumerate(content['candidates'][:3], 1):
            test_status = '[OK]' if candidate.get('test_success') else '[ERROR]'
            is_valid = '[OK]' if candidate.get('is_valid') else '[ERROR]'
            warning = candidate.get('warning', '')
            warning_line = f"- [WARNING]  {warning}" if warning else ""
            report += f"""
**候选 {i}** {test_status} {is_valid}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **内容长度**: {candidate.get('content_length', 0)} 字符
{warning_line}
"""

        # 下一章
        next_chapter = analysis['elements']['next_chapter']
        if next_chapter.get('candidates'):
            report += f"""
#### ➡️ 下一章
"""
            for i, candidate in enumerate(next_chapter['candidates'][:2], 1):
                is_next = '[OK]' if candidate.get('is_next_chapter') else '[ERROR]'
                report += f"""
**候选 {i}** {is_next}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f}
"""

        # 上一章
        prev_chapter = analysis['elements']['prev_chapter']
        if prev_chapter.get('candidates'):
            report += f"""
#### ⬅️ 上一章
"""
            for i, candidate in enumerate(prev_chapter['candidates'][:2], 1):
                is_prev = '[OK]' if candidate.get('is_prev_chapter') else '[ERROR]'
                report += f"""
**候选 {i}** {is_prev}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f}
"""

        # 章节标题
        chapter_title = analysis['elements']['chapter_title']
        if chapter_title.get('candidates'):
            report += f"""
#### 📌 章节标题
"""
            for i, candidate in enumerate(chapter_title['candidates'][:2], 1):
                report += f"""
**候选 {i}**:
- **选择器**: `{candidate['selector']}`
- **样本**: {candidate.get('sample_items', [''])[0][:50] if candidate.get('sample_items') else ''}
"""

        # 推荐规则
        report += f"""
---

### [TARGET] 推荐的正文规则

```json
{json.dumps(recommended_rules, ensure_ascii=False, indent=2)}
```

### [CONFIG] 推荐的替换规则

```json
{json.dumps(replace_rules, ensure_ascii=False, indent=2)}
```

---

### [TIP] 智能建议

1. **验证正文**: 确保提取的内容是完整的章节正文
2. **处理广告**: 使用替换规则去除广告和多余内容
3. **验证导航**: 确保上一章/下一章链接正确
4. **测试替换**: 在实际页面测试替换规则效果

**下一步操作**:
1. 复制上述规则到书源配置
2. 验证正文内容是否完整
3. 调整替换规则去除广告
4. 测试章节导航功能

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
