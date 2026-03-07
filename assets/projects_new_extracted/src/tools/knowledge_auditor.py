"""
知识库审查工具
根据真实HTML审查知识库内容，验证知识库中的选择器是否适用于当前页面
"""

import os
import json
from typing import Dict, List, Any, Optional
from langchain.tools import tool
from bs4 import BeautifulSoup


class KnowledgeAuditor:
    """知识库审查器"""
    
    def __init__(self, html: str, url: str):
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, 'html.parser')
        self.audit_results = {
            'url': url,
            'html_size': len(html),
            'timestamp': __import__('time').time(),
            'reviewed_patterns': [],
            'valid_patterns': [],
            'invalid_patterns': [],
            'unknown_patterns': []
        }
    
    def audit_selector(self, selector: str, description: str = "") -> Dict[str, Any]:
        """
        审查单个选择器
        
        Args:
            selector: CSS选择器
            description: 选择器描述
        
        Returns:
            审查结果
        """
        try:
            elements = self.soup.select(selector)
            
            result = {
                'selector': selector,
                'description': description,
                'match_count': len(elements),
                'valid': len(elements) > 0,
                'samples': []
            }
            
            # 提取样本
            for elem in elements[:5]:
                text = elem.get_text(strip=True)[:100]
                tag = elem.name
                classes = ' '.join(elem.get('class', []))
                
                result['samples'].append({
                    'text': text,
                    'tag': tag,
                    'classes': classes
                })
            
            return result
            
        except Exception as e:
            return {
                'selector': selector,
                'description': description,
                'valid': False,
                'error': str(e),
                'match_count': 0,
                'samples': []
            }
    
    def audit_knowledge_pattern(
        self,
        pattern: Dict[str, Any],
        category: str = ""
    ) -> Dict[str, Any]:
        """
        审查知识库中的模式
        
        Args:
            pattern: 知识库模式（包含selector、description等）
            category: 模式类别
        
        Returns:
            审查结果
        """
        selector = pattern.get('selector', '')
        description = pattern.get('description', '')
        
        if not selector:
            return {
                'pattern': pattern,
                'valid': False,
                'error': '缺少选择器'
            }
        
        # 审查选择器
        audit_result = self.audit_selector(selector, description)
        
        # 添加类别信息
        audit_result['category'] = category
        audit_result['pattern_source'] = pattern.get('source', 'unknown')
        
        # 记录结果
        self.audit_results['reviewed_patterns'].append(audit_result)
        
        if audit_result['valid']:
            self.audit_results['valid_patterns'].append(audit_result)
        else:
            self.audit_results['invalid_patterns'].append(audit_result)
        
        return audit_result
    
    def get_audit_report(self) -> str:
        """生成审查报告"""
        total = len(self.audit_results['reviewed_patterns'])
        valid = len(self.audit_results['valid_patterns'])
        invalid = len(self.audit_results['invalid_patterns'])
        
        report = f"""
## 🔍 知识库审查报告

### 📋 审查信息

- **网页**: {self.url}
- **HTML大小**: {self.audit_results['html_size']} 字符
- **审查时间**: {self.audit_results['timestamp']}
- **审查模式数**: {total}
- **有效模式**: {valid} ({valid/total*100 if total > 0 else 0:.1f}%)
- **无效模式**: {invalid} ({invalid/total*100 if total > 0 else 0:.1f}%)

---

### ✅ 有效模式

以下模式在当前HTML上有效，可以使用：

"""
        
        for pattern in self.audit_results['valid_patterns']:
            report += f"""
**{pattern['description']}**
- **选择器**: `{pattern['selector']}`
- **匹配数量**: {pattern['match_count']}
- **类别**: {pattern.get('category', 'unknown')}
- **来源**: {pattern.get('pattern_source', 'unknown')}
"""
            
            if pattern.get('samples'):
                report += f"- **样本**: {pattern['samples'][0]['text']}\n"
        
        report += f"""

---

### ❌ 无效模式

以下模式在当前HTML上无效，不能使用：

"""
        
        for pattern in self.audit_results['invalid_patterns']:
            report += f"""
**{pattern['description']}**
- **选择器**: `{pattern['selector']}`
- **匹配数量**: {pattern['match_count']}
- **类别**: {pattern.get('category', 'unknown')}
- **来源**: {pattern.get('pattern_source', 'unknown')}
"""
            
            if pattern.get('error'):
                report += f"- **错误**: {pattern['error']}\n"
        
        report += f"""

---

### 💡 建议

1. **有效模式**可以直接使用
2. **无效模式**需要重新分析HTML
3. 建议在真实HTML上重新测试无效的选择器
4. 可以参考有效模式的特征

---

### 📊 统计

- 总计审查: {total} 个模式
- ✅ 有效: {valid} 个
- ❌ 无效: {invalid} 个
- 📈 有效率: {(valid/total*100) if total > 0 else 0:.1f}%
"""
        
        return report.strip()


def get_html_storage_path(url: str) -> str:
    """
    获取HTML存储路径
    
    Args:
        url: 网页URL
    
    Returns:
        存储路径
    """
    # 生成文件名（使用URL的hash）
    import hashlib
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_dir = os.path.join(workspace_path, "assets", "html_storage")
    os.makedirs(html_dir, exist_ok=True)
    
    return os.path.join(html_dir, f"{url_hash}.html")


def save_html_permanently(url: str, html: str) -> str:
    """
    永久保存HTML
    
    Args:
        url: 网页URL
        html: HTML内容
    
    Returns:
        保存路径
    """
    storage_path = get_html_storage_path(url)
    
    # 保存HTML
    with open(storage_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 保存元数据
    meta_path = storage_path.replace('.html', '.meta.json')
    meta = {
        'url': url,
        'size': len(html),
        'timestamp': __import__('time').time(),
        'storage_path': storage_path
    }
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    return storage_path


def load_html_permanently(url: str) -> Optional[Dict[str, Any]]:
    """
    加载永久保存的HTML
    
    Args:
        url: 网页URL
    
    Returns:
        HTML内容和元数据，如果不存在则返回None
    """
    storage_path = get_html_storage_path(url)
    meta_path = storage_path.replace('.html', '.meta.json')
    
    if not os.path.exists(storage_path):
        return None
    
    # 读取元数据
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    # 读取HTML
    with open(storage_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    return {
        'html': html,
        'meta': meta,
        'storage_path': storage_path
    }


@tool
def audit_knowledge_base(
    url: str,
    html: str = "",
    categories: str = ""
) -> str:
    """
    🔍 审查知识库 - 验证知识库内容是否适用于真实HTML

    功能：
    - 获取真实HTML源代码（如果未提供）
    - 审查知识库中的选择器是否适用于当前HTML
    - 标记有效/无效的知识库内容
    - 生成审查报告
    
    ⚠️ 重要：
    - 知识库内容仅供参考，必须经过真实HTML审查
    - 只有在真实HTML上验证有效的选择器才能使用
    - 审查结果用于生成书源
    
    参数:
        url: 网页URL
        html: HTML内容（可选，如果不提供则自动获取）
        categories: 要审查的类别（如bookinfo, content, toc等，多个用逗号分隔）
    
    返回:
        审查报告
    """
    try:
        # 获取HTML
        if not html:
            from utils.smart_request import smart_request
            
            print(f"🌐 正在访问真实网页: {url}")
            response = smart_request(url)
            
            if not response or not response.get('success'):
                raise Exception(f"获取真实网页失败: {response.get('error', 'Unknown error') if response else 'No response'}")
            
            html = response['content']
            print(f"✅ 成功获取真实HTML，大小: {len(html)} 字符")
        
        # 永久保存HTML
        storage_path = save_html_permanently(url, html)
        print(f"💾 HTML已永久保存到: {storage_path}")
        
        # 创建审查器
        auditor = KnowledgeAuditor(html, url)
        
        # 加载知识库
        workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        knowledge_file = os.path.join(workspace_path, "assets", "Legado知识库.txt")
        
        patterns_to_audit = []
        
        if os.path.exists(knowledge_file):
            # 从知识库文件中提取模式
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_content = f.read()
            
            # 简单提取：查找选择器模式
            import re
            selector_pattern = r'([^\s]+)\s*[:：]\s*(.*?)(?=\n|$)'
            matches = re.findall(selector_pattern, knowledge_content)
            
            for match in matches:
                selector, description = match
                if selector and selector.startswith(('.', '#', '[')):
                    patterns_to_audit.append({
                        'selector': selector,
                        'description': description,
                        'source': 'Legado知识库.txt'
                    })
        
        # 如果知识库没有模式，使用常见模式
        if not patterns_to_audit:
            print("⚠️ 知识库未找到模式，使用常见模式进行审查")
            patterns_to_audit = [
                {'selector': '.title', 'description': '常见书名选择器', 'source': 'common'},
                {'selector': '.author', 'description': '常见作者选择器', 'source': 'common'},
                {'selector': '.cover', 'description': '常见封面选择器', 'source': 'common'},
                {'selector': '.intro', 'description': '常见简介选择器', 'source': 'common'},
                {'selector': 'img[src]', 'description': '常见图片选择器', 'source': 'common'},
                {'selector': 'a[href]', 'description': '常见链接选择器', 'source': 'common'},
                {'selector': 'h1', 'description': '常见标题选择器', 'source': 'common'},
                {'selector': 'h2', 'description': '常见副标题选择器', 'source': 'common'},
            ]
        
        # 审查所有模式
        print(f"🔍 开始审查 {len(patterns_to_audit)} 个模式...")
        
        for i, pattern in enumerate(patterns_to_audit, 1):
            print(f"  [{i}/{len(patterns_to_audit)}] 审查: {pattern['selector']}")
            auditor.audit_knowledge_pattern(pattern, category='knowledge_base')
        
        # 生成报告
        report = auditor.get_audit_report()
        
        # 添加HTML信息
        report = f"""
## 🔍 知识库审查报告（强制审查模式）

### 📋 审查信息

- **网页**: {url}
- **HTML大小**: {len(html)} 字符
- **HTML存储路径**: {storage_path}
- **审查模式数**: {len(patterns_to_audit)}

⚠️ **重要提醒**：
- ✅ HTML已永久保存，用于生成书源
- ✅ 只有经过审查验证有效的选择器才能使用
- ✅ 知识库内容仅供参考，不能直接使用
- ✅ 必须在真实HTML上验证

---

{report}

---

### 💾 HTML存储信息

- **保存路径**: {storage_path}
- **文件大小**: {len(html)} 字节
- **存储时间**: {auditor.audit_results['timestamp']}

⚠️ **重要**：此HTML将用于生成书源，请确保HTML完整且正确！

---

### 🎯 使用有效模式

以下模式在真实HTML上验证有效，可以直接使用：

"""
        
        for pattern in auditor.audit_results['valid_patterns']:
            report += f"""
**{pattern['description']}**
```
{pattern['selector']}
```
"""
        
        report += """

### ❌ 无效模式

以下模式在真实HTML上验证无效，不能直接使用：

"""
        
        for pattern in auditor.audit_results['invalid_patterns']:
            report += f"""
**{pattern['description']}**
```
{pattern['selector']}
```
"""
            if pattern.get('error'):
                report += f"错误: {pattern['error']}\n"
        
        report += """

---

### 📌 总结

✅ 已完成知识库审查
✅ 已永久保存HTML源代码
✅ 已标记有效/无效模式
✅ 可以使用有效模式生成书源

💡 **下一步**：
1. 使用有效模式生成书源规则
2. 如果有效模式不足，重新分析HTML
3. 手动定义规则（使用`manual_define_rule`）
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 审查失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

### 💡 建议

1. 检查URL是否正确且可访问
2. 检查网络连接
3. 检查知识库文件是否存在
"""


@tool
def get_saved_html(
    url: str
) -> str:
    """
    💾 获取已保存的HTML

    获取之前永久保存的HTML源代码

    参数:
        url: 网页URL

    返回:
        HTML内容和存储信息
    """
    result = load_html_permanently(url)

    if not result:
        return f"""
## ❌ HTML未找到

**URL**: {url}

此URL的HTML尚未保存。

### 💡 建议

1. 使用`audit_knowledge_base`工具获取并保存HTML
2. 使用其他分析工具会自动保存HTML
3. 确保URL正确
"""

    html = result['html']
    meta = result['meta']

    report = f"""
## 💾 已保存的HTML

### 📋 存储信息

**URL**: {url}
**存储路径**: {result['storage_path']}
**文件大小**: {meta['size']} 字符
**保存时间**: {meta['timestamp']}

---

### 💻 HTML内容（完整源代码）

```html
{html}
```

---

### 🎯 使用说明

此HTML已保存并审查，可以用于：
1. 重新审查知识库
2. 生成书源规则
3. 分析页面结构
4. 测试选择器

⚠️ **重要**：这是真实网页的HTML源代码，禁止篡改！
"""

    return report


@tool
def list_saved_htmls() -> str:
    """
    📋 列出所有已保存的HTML

    列出所有永久保存的HTML文件

    返回:
        HTML列表
    """
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_dir = os.path.join(workspace_path, "assets", "html_storage")

    if not os.path.exists(html_dir):
        return """
## 📋 已保存的HTML列表

暂无已保存的HTML文件。

### 💡 建议

1. 使用`audit_knowledge_base`工具获取并保存HTML
2. 使用分析工具会自动保存HTML
"""

    # 读取所有元数据文件
    meta_files = []
    for file in os.listdir(html_dir):
        if file.endswith('.meta.json'):
            meta_files.append(file)

    if not meta_files:
        return """
## 📋 已保存的HTML列表

暂无已保存的HTML文件。

### 💡 建议

1. 使用`audit_knowledge_base`工具获取并保存HTML
2. 使用分析工具会自动保存HTML
"""

    report = """
## 📋 已保存的HTML列表

"""

    for meta_file in sorted(meta_files):
        meta_path = os.path.join(html_dir, meta_file)
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        report += f"""
### 📄 {meta['url'][:60]}{'...' if len(meta['url']) > 60 else ''}

- **URL**: {meta['url']}
- **大小**: {meta['size']} 字符
- **保存时间**: {meta['timestamp']}
- **存储路径**: {meta['storage_path']}

---

"""

    report += f"""
### 📊 统计

- 总计保存: {len(meta_files)} 个HTML文件
- 存储目录: {html_dir}

### 🎯 使用说明

1. 使用`get_saved_html`工具查看具体HTML内容
2. 使用`audit_knowledge_base`工具重新审查
3. 使用已保存的HTML生成书源规则
"""

    return report.strip()
