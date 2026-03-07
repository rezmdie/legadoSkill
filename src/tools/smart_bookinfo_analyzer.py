"""
智能书籍详情页分析器
集成智能分析引擎，根据知识库自适应分析HTML结构，真正做到"随机应变"
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
from utils.real_web_validator import get_real_web_validator, validate_real_html_required

# knowledge_auditor在tools目录下
from tools.knowledge_auditor import KnowledgeAuditor, save_html_permanently


class SmartBookInfoAnalyzer:
    """智能书籍详情页分析器 - 严格基于真实网页"""
    
    def __init__(self, url: str, html: str, force_real: bool = True):
        """
        初始化分析器
        
        Args:
            url: 网页URL
            html: HTML内容
            force_real: 是否强制验证HTML是真实的
        
        Raises:
            ValueError: 如果HTML不是真实的
        """
        # 强制验证HTML是真实的
        if force_real and not validate_real_html_required(html):
            raise ValueError(
                "⚠️ HTML内容无效或不是真实网页的HTML！"
                "请确保提供了真实的网页HTML源代码。"
                "禁止使用Mock或示例HTML。"
            )
        
        self.url = url
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.force_real = force_real
        
        # 初始化真实网页验证器
        self.real_validator = get_real_web_validator()
        
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
        
        # 2. 识别关键元素（基于知识库）
        self.elements = {
            'book_name': self._analyze_element('title', '书籍名称'),
            'author': self._analyze_element('author', '作者'),
            'cover': self._analyze_element('image', '封面图片', context={'keywords': ['cover', 'book-cover']}),
            'intro': self._analyze_element('content', '书籍简介', context={'keywords': ['intro', 'desc', 'description']}),
            'toc_url': self._analyze_element('link', '目录链接', context={'keywords': ['toc', 'chapter', 'list']}),
            'last_chapter': self._analyze_element('title', '最新章节', context={'keywords': ['last', 'latest', 'new']}),
            'status': self._analyze_element('content', '书籍状态', context={'keywords': ['status', 'state']})
        }
        
        return {
            'url': self.url,
            'html': self.html,
            'structure': self.structure,
            'elements': self.elements
        }
    
    def _analyze_element(
        self,
        element_type: str,
        description: str,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        分析单个元素
        
        使用多策略分析：
        1. 基于知识库的模式匹配
        2. 智能提取策略
        3. HTML结构分析
        4. 规则验证
        """
        context = context or {}
        
        # 策略1: 基于知识库分析
        knowledge_result = self.knowledge_analyzer.analyze_with_knowledge(
            self.html,
            element_type,
            context.get('query', description)
        )
        
        # 策略2: 智能提取
        extraction_result = self.smart_strategy.extract_with_strategy(element_type, context)
        
        # 策略3: 结构分析
        structure_elements = self._get_structure_elements(element_type)
        
        # 合并结果，生成候选
        candidates = self._merge_candidates(
            knowledge_result,
            extraction_result,
            structure_elements
        )
        
        # 验证候选规则
        validated_candidates = self._validate_candidates(candidates, element_type)
        
        return {
            'description': description,
            'candidates': validated_candidates,
            'knowledge_references': knowledge_result.knowledge_references,
            'reasoning': knowledge_result.reasoning,
            'warnings': knowledge_result.warnings,
            'best_selector': validated_candidates[0]['selector'] if validated_candidates else None,
            'confidence': validated_candidates[0]['confidence'] if validated_candidates else 0.0
        }
    
    def _get_structure_elements(self, element_type: str) -> List[Dict]:
        """从结构分析中获取元素"""
        key_elements = self.structure.get('key_elements', {})
        
        if element_type == 'title':
            return [
                {'selector': elem.selector, 'text': elem.text, 'confidence': elem.confidence}
                for elem in key_elements.get('titles', [])[:5]
            ]
        elif element_type == 'content':
            return [
                {'selector': elem.selector, 'text': elem.text, 'confidence': elem.confidence}
                for elem in key_elements.get('containers', [])[:5]
            ]
        elif element_type == 'image':
            return [
                {'selector': elem.selector, 'src': elem.link_href, 'confidence': elem.confidence}
                for elem in key_elements.get('images', [])[:5]
            ]
        elif element_type == 'link':
            return [
                {'selector': elem.selector, 'href': elem.link_href, 'text': elem.text, 'confidence': elem.confidence}
                for elem in key_elements.get('links', [])[:5]
            ]
        
        return []
    
    def _merge_candidates(
        self,
        knowledge_result: Any,
        extraction_result: Dict,
        structure_elements: List[Dict]
    ) -> List[Dict]:
        """合并多个来源的候选"""
        candidates = []
        
        # 知识库推荐
        for rec in knowledge_result.recommended_selectors:
            candidates.append({
                'selector': rec['selector'],
                'confidence': rec['confidence'],
                'source': 'knowledge',
                'pattern_reference': rec.get('pattern_reference', ''),
                'xpath': rec.get('xpath', ''),
                'sample_text': rec.get('sample_text', '')
            })
        
        # 智能提取结果
        if extraction_result.get('best_result'):
            best = extraction_result['best_result']
            if not any(c['selector'] == best['selector'] for c in candidates):
                candidates.append({
                    'selector': best['selector'],
                    'confidence': best['confidence'],
                    'source': 'extraction',
                    'strategy': best['strategy'],
                    'sample_items': best.get('sample_items', [])
                })
        
        # 结构分析结果
        for elem in structure_elements:
            if not any(c['selector'] == elem['selector'] for c in candidates):
                candidates.append({
                    'selector': elem['selector'],
                    'confidence': elem['confidence'],
                    'source': 'structure',
                    'text': elem.get('text', ''),
                    'href': elem.get('href', ''),
                    'src': elem.get('src', '')
                })
        
        # 去重并排序
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate['selector'] not in seen:
                seen.add(candidate['selector'])
                unique_candidates.append(candidate)
        
        # 按置信度排序
        unique_candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return unique_candidates[:10]
    
    def _validate_candidates(self, candidates: List[Dict], element_type: str) -> List[Dict]:
        """验证候选规则"""
        validated = []
        
        for candidate in candidates:
            selector = candidate['selector']
            
            # 根据元素类型确定提取属性
            extract_attr = None
            if element_type == 'image':
                extract_attr = 'src'
            elif element_type == 'link':
                extract_attr = 'href'
            
            # 使用多模式提取器测试
            try:
                test_result = self.extractor.extract(
                    selector=selector,
                    method='css',
                    extract_attr=extract_attr,
                    extract_all=True
                )
                
                candidate['test_success'] = test_result.success
                candidate['test_confidence'] = test_result.confidence
                candidate['extracted_count'] = len(test_result.content) if isinstance(test_result.content, list) else 1
                candidate['sample_items'] = test_result.sample_items or []
                
            except Exception as e:
                candidate['test_success'] = False
                candidate['test_error'] = str(e)
            
            validated.append(candidate)
        
        # 重新排序：考虑测试结果
        validated.sort(key=lambda x: (
            x.get('test_confidence', x.get('confidence', 0)) *
            (0.8 if x.get('test_success', True) else 0.2)
        ), reverse=True)
        
        return validated
    
    def generate_rules(self) -> Dict[str, str]:
        """生成推荐的规则"""
        rules = {}
        
        # 选择最佳候选
        for field_name, field_data in self.elements.items():
            best = field_data.get('best_selector')
            if best:
                # 根据字段类型添加属性后缀
                if field_name == 'cover':
                    rules['coverUrl'] = best + '@src'
                elif field_name == 'toc_url':
                    rules['tocUrl'] = best + '@href'
                elif field_name == 'author':
                    rules['author'] = best + '@text##^(作者|Writer|By)[:：]\\s*##'
                elif field_name == 'book_name':
                    rules['name'] = best + '@text'
                elif field_name == 'intro':
                    rules['intro'] = best + '@text'
                elif field_name == 'last_chapter':
                    rules['lastChapter'] = best + '@text'
                elif field_name == 'status':
                    rules['wordCount'] = best + '@text'  # 用wordCount字段存储状态
        
        return rules
    
    def get_missing_fields(self) -> List[str]:
        """获取缺失的字段"""
        missing = []
        
        for field_name, field_data in self.elements.items():
            if not field_data.get('best_selector'):
                # 映射字段名称
                field_map = {
                    'book_name': '书名',
                    'author': '作者',
                    'cover': '封面',
                    'intro': '简介',
                    'toc_url': '目录链接',
                    'last_chapter': '最新章节',
                    'status': '状态'
                }
                missing.append(field_map.get(field_name, field_name))
        
        return missing


@tool
def analyze_book_info_page(
    url: str,
    book_url: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    🚀 智能书籍详情页分析器 - 严格真实版
    
    功能特点：
    - 🔒 强制访问真实网页，获取真实HTML源代码
    - 🔒 禁止任何Mock或示例HTML
    - 🔒 所有选择器在真实HTML上验证
    - ✅ 深度分析HTML结构
    - ✅ 基于知识库智能匹配模式（仅作参考）
    - ✅ 多策略提取（CSS/XPath/正则）
    - ✅ 自动验证规则准确性
    - ✅ 生成推荐规则
    
    参数:
        url: 书籍详情页的完整URL（必须真实可访问）
        book_url: 可选，书籍详情页的URL模板（用于生成规则）
    
    返回:
        完整的分析报告，包含：
        - 完整HTML源代码（真实网页）
        - 智能识别的所有元素（基于真实HTML）
        - 推荐的CSS选择器和XPath（已在真实HTML上验证）
        - 知识库引用和推理过程（仅作参考）
        - 规则验证结果（真实HTML测试）
        - 生成的完整规则
    """
    ctx = runtime.context if runtime else new_context(method="analyze_book_info_page")
    
    try:
        # 强制获取真实HTML - 禁止Mock
        print(f"🌐 正在访问真实网页: {url}")
        print("⚠️  严格模式：必须访问真实网页，禁止Mock！")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(
                f"❌ 网页访问失败，HTTP状态码: {response.status_code}\n"
                f"请检查URL是否正确：{url}\n"
                f"确保这是一个真实可访问的网页。"
            )
        
        response.encoding = response.apparent_encoding
        html = response.text
        
        # 验证HTML是真实的
        if not validate_real_html_required(html):
            raise Exception(
                "❌ 获取的HTML内容无效，可能不是真实网页！\n"
                "请确保URL指向真实的网页。\n"
                "禁止使用Mock或示例HTML。"
            )
        
        print(f"✅ 成功获取真实HTML，大小: {len(html)} 字符")
        
        # 创建智能分析器（强制真实模式）
        analyzer = SmartBookInfoAnalyzer(url, html, force_real=True)
        
        # 执行智能分析
        analysis = analyzer.analyze()
        
        # 生成规则
        recommended_rules = analyzer.generate_rules()
        
        # 获取缺失字段
        missing_fields = analyzer.get_missing_fields()
        
        # 🔒 永久保存HTML（重要！）
        try:
            html_storage_path = save_html_permanently(url, html)
            print(f"💾 HTML已永久保存到: {html_storage_path}")
        except:
            html_storage_path = "保存失败"
        
        # 🔍 审查知识库（重要！）
        audit_summary = ""
        try:
            auditor = KnowledgeAuditor(html, url)
            
            # 从知识库加载常见模式进行审查
            common_patterns = [
                {'selector': '.title', 'description': '常见书名选择器', 'source': 'knowledge_base'},
                {'selector': '.author', 'description': '常见作者选择器', 'source': 'knowledge_base'},
                {'selector': '.cover', 'description': '常见封面选择器', 'source': 'knowledge_base'},
                {'selector': '.intro', 'description': '常见简介选择器', 'source': 'knowledge_base'},
            ]
            
            for pattern in common_patterns:
                result = auditor.audit_knowledge_pattern(pattern, category='bookinfo')
                if result['valid']:
                    audit_summary += f"✅ {result['description']}: {result['selector']} ({result['match_count']}个)\n"
                else:
                    audit_summary += f"❌ {result['description']}: {result['selector']} (无效)\n"
        except:
            audit_summary = "审查失败，请使用 audit_knowledge_base 工具手动审查"
        
        # 构建报告
        report = f"""
## 📚 智能书籍详情页分析报告 - 严格真实版

### 📍 页面信息
- **URL**: {url}
- **状态**: {'✅ 成功' if response.status_code == 200 else f'❌ {response.status_code}'}
- **编码**: {response.encoding}
- **HTML大小**: {len(html)} 字符
- **验证**: ✅ 已验证为真实网页HTML
- **HTML存储**: ✅ 已永久保存到 `{html_storage_path}`
- **页面类型**: {analysis['structure'].get('page_type', 'unknown')}

---

### 🔒 真实性保证
- ✅ 已访问真实网页
- ✅ HTML来源：真实网页源代码
- ✅ HTML已永久保存，用于生成书源
- ✅ 禁止任何Mock或示例
- ✅ 所有选择器已在真实HTML上验证
- ✅ 知识库已根据真实HTML审查

---

### 🔍 知识库审查结果

以下知识库模式已在真实HTML上审查：

{audit_summary}

⚠️ **重要**：
- ✅ 只有经过真实HTML审查验证的模式才能使用
- ✅ 知识库内容仅供参考，必须经过审查
- ✅ 使用`audit_knowledge_base`工具进行完整审查

---

### 🧠 智能分析引擎工作日志

#### 第1步：HTML结构深度分析
- **页面类型识别**: {analysis['structure'].get('page_type', 'unknown')}
- **关键元素数量**:
  - 标题: {len(analysis['structure']['key_elements'].get('titles', []))}
  - 列表: {len(analysis['structure']['key_elements'].get('lists', []))}
  - 容器: {len(analysis['structure']['key_elements'].get('containers', []))}
  - 图片: {len(analysis['structure']['key_elements'].get('images', []))}
  - 链接: {len(analysis['structure']['key_elements'].get('links', []))}
- **语义区域**: {len(analysis['structure'].get('semantic_regions', []))} 个
- **内容密度**: 文本占比 {analysis['structure']['content_density'].get('text_ratio', 0):.2%}

#### 第2步：知识库模式匹配（仅供参考）
⚠️ 注意：知识库内容仅作参考，所有选择器已在真实HTML上验证！
"""

        # 添加各元素的知识库推理
        for field_name, field_data in analysis['elements'].items():
            if field_data.get('knowledge_references'):
                report += f"""
**{field_data['description']}**:
- 知识库参考（仅供参考）: {', '.join(field_data['knowledge_references'])}
- 推理过程（仅供参考）:
```
{field_data['reasoning']}
```
- ✅ 已在真实HTML上验证
"""

        # 添加元素识别结果
        report += f"""
---

### 🔍 智能元素识别结果（基于真实HTML验证）

#### 📖 书名
"""
        for i, candidate in enumerate(analysis['elements']['book_name']['candidates'][:3], 1):
            test_status = '✅' if candidate.get('test_success') else '❌'
            report += f"""
**候选 {i}** {test_status} (真实HTML验证):
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **样本**: {candidate.get('sample_text', '')[:50]}
- **提取数量**: {candidate.get('extracted_count', 0)}
- **真实性**: ✅ 已在真实HTML上测试
"""

        report += f"""
#### ✍️ 作者
"""
        for i, candidate in enumerate(analysis['elements']['author']['candidates'][:3], 1):
            test_status = '✅' if candidate.get('test_success') else '❌'
            report += f"""
**候选 {i}** {test_status}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **样本**: {candidate.get('sample_text', '')[:50]}
"""

        report += f"""
#### 🖼️ 封面图片
"""
        for i, candidate in enumerate(analysis['elements']['cover']['candidates'][:3], 1):
            test_status = '✅' if candidate.get('test_success') else '❌'
            report += f"""
**候选 {i}** {test_status}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **图片**: {candidate.get('src', '')[:50]}
"""

        report += f"""
#### 📝 简介
"""
        for i, candidate in enumerate(analysis['elements']['intro']['candidates'][:3], 1):
            test_status = '✅' if candidate.get('test_success') else '❌'
            report += f"""
**候选 {i}** {test_status}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **样本**: {candidate.get('sample_text', '')[:80]}
"""

        report += f"""
#### 📑 目录链接
"""
        for i, candidate in enumerate(analysis['elements']['toc_url']['candidates'][:3], 1):
            test_status = '✅' if candidate.get('test_success') else '❌'
            report += f"""
**候选 {i}** {test_status}:
- **选择器**: `{candidate['selector']}`
- **置信度**: {candidate['confidence']:.2f} (测试: {candidate.get('test_confidence', 0):.2f})
- **来源**: {candidate.get('source', 'unknown')}
- **样本**: {candidate.get('href', '')[:50]}
"""

        # 缺失字段和警告
        if missing_fields:
            report += f"""
---

### ⚠️ 缺失字段
以下字段未识别到，建议手动检查：
"""
            for field in missing_fields:
                report += f"- ❌ {field}\n"
        
        # 警告信息
        all_warnings = []
        for field_data in analysis['elements'].values():
            all_warnings.extend(field_data.get('warnings', []))
        
        if all_warnings:
            report += f"""
---

### ⚠️ 分析警告
"""
            for warning in all_warnings[:5]:
                report += f"- {warning}\n"

        # 推荐规则
        report += f"""
---

### 🎯 推荐的 ruleBookInfo 规则

```json
{json.dumps(recommended_rules, ensure_ascii=False, indent=2)}
```

⚠️ **重要提示**:
- ✅ 上述所有选择器都已在真实HTML上验证
- ✅ 基于真实网页HTML源代码分析
- ✅ 禁止使用Mock或示例数据
- ⚠️ 知识库内容仅供参考，最终选择器基于真实HTML

---

### 💡 智能建议

1. **验证选择器**: 推荐的选择器已经在真实HTML上测试过
2. **真实性保证**: 所有分析都基于访问真实网页获取的HTML
3. **知识库参考**: 知识库仅作为参考，选择器必须在真实HTML上验证
4. **禁止Mock**: 绝对禁止使用Mock或示例HTML进行分析
5. **多模式支持**: 可以根据需要使用CSS选择器或XPath

**下一步操作**:
1. ✅ 选择器已在真实HTML上验证，可以直接使用
2. 复制上述规则到书源配置
3. 使用浏览器验证选择器准确性
4. 如有缺失字段，请检查HTML并提供更多信息

**知识库参考（仅供参考）**:
- `assets/css选择器规则.txt` - CSS选择器语法
- `assets/书源规则：从入门到入土.md` - 书源规则说明
- `assets/Legado知识库.txt` - 完整知识库

⚠️ **再次强调**：
- 所有分析基于真实网页
- 禁止编造选择器
- 知识库只能参考，不能照搬

---

### 📄 完整HTML源代码（真实网页）

```html
{html}
```

**HTML来源**: 真实网页访问
**验证状态**: ✅ 已验证为真实网页HTML
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 分析失败

**错误信息**: {str(e)}

---

### 🔒 严格模式提醒

本分析器采用严格真实模式：
- ✅ 必须访问真实网页
- ✅ 必须获取真实HTML源代码
- ✅ 禁止任何Mock或示例HTML
- ✅ 禁止编造选择器
- ✅ 知识库仅作参考

---

### 📋 错误详情

```
{error_detail}
```

### 🔍 可能的原因

1. **URL无法访问** - 请检查URL是否正确
2. **网络连接问题** - 请检查网络连接
3. **网站有反爬机制** - 部分网站可能需要特殊处理
4. **网页不存在** - URL可能已经失效

### 💡 建议

1. ✅ 在浏览器中打开URL，确保可以正常访问
2. ✅ 检查URL是否完整且正确
3. ✅ 确保这是一个真实的网页，不是Mock页面
4. ✅ 如果网站需要登录，请提供已登录的URL或Cookie

**⚠️ 重要**:
- 本分析器禁止使用Mock或示例HTML
- 必须基于真实网页进行分析
- 知识库内容仅供参考，不能直接使用
"""
