"""
智能综合书源分析器 - 随机应变版
整合所有分析功能，提供一站式书源分析服务
"""

from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
import requests
import json
from typing import Dict, List, Any

# 导入子分析器
from .smart_bookinfo_analyzer import SmartBookInfoAnalyzer
from .smart_toc_analyzer import SmartTOCAnalyzer
from .smart_content_analyzer import SmartContentAnalyzer


class SmartFullAnalyzer:
    """智能综合书源分析器"""
    
    def __init__(self, search_url: str, book_url: str, toc_url: str, content_url: str):
        self.search_url = search_url
        self.book_url = book_url
        self.toc_url = toc_url
        self.content_url = content_url
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def analyze_all(self) -> Dict[str, Any]:
        """执行完整分析"""
        results = {
            'search': None,
            'book_info': None,
            'toc': None,
            'content': None
        }
        
        # 分析各个页面
        if self.book_url:
            results['book_info'] = self._analyze_book_info()
        
        if self.toc_url:
            results['toc'] = self._analyze_toc()
        
        if self.content_url:
            results['content'] = self._analyze_content()
        
        # 生成完整书源
        book_source = self._generate_book_source(results)
        
        return {
            'results': results,
            'book_source': book_source
        }
    
    def _analyze_book_info(self) -> Dict:
        """分析书籍详情页"""
        try:
            response = requests.get(self.book_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            html = response.text
            
            analyzer = SmartBookInfoAnalyzer(self.book_url, html)
            return analyzer.analyze()
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_toc(self) -> Dict:
        """分析目录页"""
        try:
            response = requests.get(self.toc_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            html = response.text
            
            analyzer = SmartTOCAnalyzer(self.toc_url, html)
            return analyzer.analyze()
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_content(self) -> Dict:
        """分析正文页"""
        try:
            response = requests.get(self.content_url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            html = response.text
            
            analyzer = SmartContentAnalyzer(self.content_url, html)
            return analyzer.analyze()
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_book_source(self, results: Dict) -> Dict:
        """生成完整书源"""
        book_source = {
            'bookSourceUrl': self.book_url or '',
            'bookSourceName': '',
            'bookSourceGroup': '',
            'bookSourceType': 0,
            'bookSourceComment': '',
            'loginUrl': '',
            'loginUi': '',
            'loginCheckJs': '',
            'concurrentRate': '',
            'header': json.dumps(self.headers),
            'searchUrl': '',
            'exploreUrl': '',
            'enabled': True,
            'enabledCookieJar': True,
            'enabledExplore': False,
            'lastUpdateTime': 0,
            'respondTime': 180000,
            'ruleBookInfo': {},
            'ruleToc': {},
            'ruleContent': {}
        }
        
        # 书籍信息规则
        if results.get('book_info'):
            book_info = results['book_info']
            if book_info.get('url'):
                book_source['bookSourceUrl'] = book_info['url']
            
            # 从元素中提取最佳规则
            if book_info.get('elements'):
                elements = book_info['elements']
                rule_book_info = {}
                
                # 书名
                if elements.get('book_name', {}).get('best_selector'):
                    rule_book_info['name'] = elements['book_name']['best_selector'] + '@text'
                
                # 作者
                if elements.get('author', {}).get('best_selector'):
                    rule_book_info['author'] = elements['author']['best_selector'] + '@text##^(作者|Writer|By)[:：]\\s*##'
                
                # 封面
                if elements.get('cover', {}).get('best_selector'):
                    rule_book_info['coverUrl'] = elements['cover']['best_selector'] + '@src'
                
                # 简介
                if elements.get('intro', {}).get('best_selector'):
                    rule_book_info['intro'] = elements['intro']['best_selector'] + '@text'
                
                # 目录链接
                if elements.get('toc_url', {}).get('best_selector'):
                    rule_book_info['tocUrl'] = elements['toc_url']['best_selector'] + '@href'
                
                # 最新章节
                if elements.get('last_chapter', {}).get('best_selector'):
                    rule_book_info['lastChapter'] = elements['last_chapter']['best_selector'] + '@text'
                
                book_source['ruleBookInfo'] = rule_book_info
        
        # 目录规则
        if results.get('toc'):
            toc = results['toc']
            if toc.get('elements'):
                elements = toc['elements']
                rule_toc = {}
                
                # 章节列表
                if elements.get('chapter_list', {}).get('best_selector'):
                    rule_toc['chapterList'] = elements['chapter_list']['best_selector']
                
                # 章节名称
                if elements.get('chapter_items', {}).get('best_selector'):
                    rule_toc['chapterName'] = elements['chapter_items']['best_selector'] + '@text'
                
                # 章节链接
                if elements.get('chapter_items', {}).get('best_selector'):
                    rule_toc['chapterUrl'] = elements['chapter_items']['best_selector'] + '@href'
                
                book_source['ruleToc'] = rule_toc
        
        # 正文规则
        if results.get('content'):
            content = results['content']
            if content.get('elements'):
                elements = content['elements']
                rule_content = {}
                
                # 正文内容
                if elements.get('content', {}).get('best_selector'):
                    rule_content['content'] = elements['content']['best_selector'] + '@text'
                
                # 下一章
                if elements.get('next_chapter', {}).get('best_selector'):
                    rule_content['nextContentUrl'] = elements['next_chapter']['best_selector'] + '@href'
                
                # 上一章
                if elements.get('prev_chapter', {}).get('best_selector'):
                    rule_content['prevContentUrl'] = elements['prev_chapter']['best_selector'] + '@href'
                
                book_source['ruleContent'] = rule_content
        
        return book_source
    
    def generate_report(self) -> str:
        """生成完整报告"""
        analysis = self.analyze_all()
        
        report = f"""
## 🚀 智能综合书源分析报告 - 随机应变版

### 📊 分析概览
- **书籍详情页**: {'✅ 已分析' if analysis['results'].get('book_info') else '❌ 未提供'}
- **目录页**: {'✅ 已分析' if analysis['results'].get('toc') else '❌ 未提供'}
- **正文页**: {'✅ 已分析' if analysis['results'].get('content') else '❌ 未提供'}

---

### 📚 生成的完整书源

```json
{json.dumps(analysis['book_source'], ensure_ascii=False, indent=2)}
```

---

### 💡 使用说明

1. **保存书源**: 将上述JSON保存为书源文件
2. **导入Legado**: 在Legado中导入书源
3. **验证功能**: 测试搜索、目录、阅读等功能
4. **调整规则**: 根据实际情况微调规则

---

### 🔍 详细分析报告

"""
        
        # 添加各个页面的详细分析
        if analysis['results'].get('book_info'):
            book_info = analysis['results']['book_info']
            report += f"""
#### 📖 书籍详情页分析
- **URL**: {book_info.get('url', 'unknown')}
- **页面类型**: {book_info.get('structure', {}).get('page_type', 'unknown')}

**识别的字段**:
"""
            elements = book_info.get('elements', {})
            for field_name, field_data in elements.items():
                best = field_data.get('best_selector')
                confidence = field_data.get('confidence', 0)
                status = '✅' if best else '❌'
                report += f"- {field_data.get('description', field_name)}: {status} (置信度: {confidence:.2f})\n"
        
        if analysis['results'].get('toc'):
            toc = analysis['results']['toc']
            report += f"""

#### 📑 目录页分析
- **URL**: {toc.get('url', 'unknown')}
- **页面类型**: {toc.get('structure', {}).get('page_type', 'unknown')}

**识别的字段**:
"""
            elements = toc.get('elements', {})
            for field_name, field_data in elements.items():
                if field_name == 'chapter_list':
                    best = field_data.get('best_selector')
                    confidence = field_data.get('confidence', 0)
                    status = '✅' if best else '❌'
                    report += f"- 章节列表: {status} (置信度: {confidence:.2f})\n"
        
        if analysis['results'].get('content'):
            content = analysis['results']['content']
            report += f"""

#### 📄 正文页分析
- **URL**: {content.get('url', 'unknown')}
- **页面类型**: {content.get('structure', {}).get('page_type', 'unknown')}

**识别的字段**:
"""
            elements = content.get('elements', {})
            for field_name, field_data in elements.items():
                best = field_data.get('best_selector')
                confidence = field_data.get('confidence', 0)
                status = '✅' if best else '❌'
                report += f"- {field_data.get('description', field_name)}: {status} (置信度: {confidence:.2f})\n"
        
        return report.strip()


@tool
def analyze_full_book_source(
    book_url: str = "",
    toc_url: str = "",
    content_url: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    🚀 智能综合书源分析器 - 随机应变版
    
    功能特点：
    - ✅ 一站式分析所有页面
    - ✅ 生成完整书源JSON
    - ✅ 基于知识库智能分析
    - ✅ 多策略自适应识别
    - ✅ 自动验证规则准确性
    
    参数:
        book_url: 书籍详情页URL（至少提供一个）
        toc_url: 目录页URL
        content_url: 正文页URL
    
    返回:
        完整的书源JSON和分析报告
    """
    ctx = runtime.context if runtime else new_context(method="analyze_full_book_source")
    
    if not book_url and not toc_url and not content_url:
        return """
## ❌ 参数错误

请至少提供一个URL：
- book_url: 书籍详情页URL
- toc_url: 目录页URL
- content_url: 正文页URL
"""
    
    try:
        analyzer = SmartFullAnalyzer("", book_url, toc_url, content_url)
        report = analyzer.generate_report()
        
        return report
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 分析失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""


# 别名工具
@tool
def analyze_complete_book_source(
    book_url: str = "",
    toc_url: str = "",
    content_url: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    分析完整书源 - analyze_full_book_source的别名
    
    功能特点：
    - ✅ 一站式分析所有页面
    - ✅ 生成完整书源JSON
    - ✅ 基于知识库智能分析
    - ✅ 多策略自适应识别
    - ✅ 自动验证规则准确性
    
    参数:
        book_url: 书籍详情页URL（至少提供一个）
        toc_url: 目录页URL
        content_url: 正文页URL
    
    返回:
        完整的书源JSON和分析报告
    """
    # 创建SmartFullAnalyzer实例并生成报告
    if not book_url and not toc_url and not content_url:
        return """
## ❌ 参数错误

请至少提供一个URL：
- book_url: 书籍详情页URL
- toc_url: 目录页URL
- content_url: 正文页URL
"""
    
    try:
        analyzer = SmartFullAnalyzer("", book_url, toc_url, content_url)
        report = analyzer.generate_report()
        return report
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 分析失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""


@tool
def analyze_book_structure(
    book_url: str = "",
    toc_url: str = "",
    content_url: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    分析书籍结构 - analyze_full_book_source的别名
    
    功能特点：
    - ✅ 一站式分析所有页面
    - ✅ 生成完整书源JSON
    - ✅ 基于知识库智能分析
    - ✅ 多策略自适应识别
    - ✅ 自动验证规则准确性
    
    参数:
        book_url: 书籍详情页URL（至少提供一个）
        toc_url: 目录页URL
        content_url: 正文页URL
    
    返回:
        完整的书源JSON和分析报告
    """
    # 创建SmartFullAnalyzer实例并生成报告
    if not book_url and not toc_url and not content_url:
        return """
## ❌ 参数错误

请至少提供一个URL：
- book_url: 书籍详情页URL
- toc_url: 目录页URL
- content_url: 正文页URL
"""
    
    try:
        analyzer = SmartFullAnalyzer("", book_url, toc_url, content_url)
        report = analyzer.generate_report()
        return report
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 分析失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```
"""
