"""
选择器真实验证工具
确保所有选择器都在真实HTML上测试过
"""

import os
import sys
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
import json

# 确保utils目录在Python路径中
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
utils_path = os.path.join(workspace_path, "src", "utils")
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

from utils.real_web_validator import get_real_web_validator


@tool
def validate_selector_on_real_web(
    url: str,
    selector: str,
    expect_count: int = None,
    runtime: ToolRuntime = None
) -> str:
    """
    🔍 选择器真实验证器 - 严格验证版
    
    在真实网页上验证选择器的有效性，禁止Mock
    
    功能特点：
    - 🔒 必须访问真实网页
    - 🔒 获取真实HTML源代码
    - 🔒 在真实HTML上测试选择器
    - ✅ 显示提取的内容样本
    - ✅ 验证选择器语法
    - ✅ 验证匹配数量
    
    参数:
        url: 真实网页的URL（必须可访问）
        selector: 要验证的CSS选择器
        expect_count: 期望匹配的数量（可选）
    
    返回:
        验证结果报告
    """
    ctx = runtime.context if runtime else new_context(method="validate_selector_on_real_web")
    
    try:
        # 获取真实网页验证器
        validator = get_real_web_validator()
        
        # 获取真实HTML
        print(f"🌐 正在访问真实网页: {url}")
        html_result = validator.fetch_real_html(url)
        
        if not html_result['success']:
            raise Exception(f"获取真实网页失败: {html_result.get('error', 'Unknown error')}")
        
        html = html_result['html']
        print(f"✅ 成功获取真实HTML，大小: {html_result['size']} 字符")
        
        # 在真实HTML上验证选择器
        print(f"🔍 正在真实HTML上测试选择器: {selector}")
        validation_result = validator.validate_selector_on_real_html(
            selector=selector,
            html=html,
            expect_count=expect_count
        )
        
        # 构建报告
        report = f"""
## 🔍 选择器真实验证报告

### 📍 网页信息
- **URL**: {url}
- **HTML大小**: {html_result['size']} 字符
- **验证状态**: ✅ 已验证为真实网页HTML

---

### 🔬 选择器测试结果

**选择器**: `{selector}`

**测试状态**: {'✅ 有效' if validation_result['valid'] else '❌ 无效'}

**匹配数量**: {validation_result['extracted_count']} 个元素

**测试消息**: {validation_result['message']}

---

### 📋 提取的内容样本

"""
        
        if validation_result.get('sample_results'):
            for i, sample in enumerate(validation_result['sample_results'][:10], 1):
                report += f"""
**样本 {i}**:
- **文本**: {sample['text']}
- **标签**: {sample['tag']}
- **类名**: {', '.join(sample['classes'])}
"""
        else:
            report += "❌ 未提取到任何内容\n"
        
        # 数量验证
        if expect_count is not None:
            report += f"""
---

### 📊 数量验证

- **期望数量**: {expect_count}
- **实际数量**: {validation_result['extracted_count']}
- **验证结果**: {'✅ 通过' if validation_result['extracted_count'] == expect_count else '❌ 不匹配'}
"""
        
        # 建议
        report += f"""

---

### 💡 建议

"""
        
        if validation_result['valid']:
            report += f"""
✅ 该选择器在真实网页上有效，可以使用！

**建议**:
1. 可以直接在书源规则中使用此选择器
2. 检查提取的内容是否符合预期
3. 如果需要精确匹配，可以添加更多限制条件
"""
        else:
            report += f"""
❌ 该选择器在真实网页上无效，需要调整！

**可能的问题**:
1. 选择器语法错误
2. 选择器与网页结构不匹配
3. 页面结构可能已变化

**建议**:
1. 在浏览器中打开网页，使用开发者工具检查元素
2. 重新分析网页HTML结构
3. 尝试更简单的选择器进行测试
4. 使用智能分析器自动识别选择器
"""
        
        report += f"""

---

### 🔒 真实性保证

- ✅ 已访问真实网页
- ✅ HTML来源：真实网页源代码
- ✅ 选择器已在真实HTML上测试
- ✅ 禁止任何Mock或示例
- ✅ 所有结果基于真实数据

---

### 📄 详细结果

```json
{json.dumps(validation_result, ensure_ascii=False, indent=2)}
```
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 验证失败

**错误信息**: {str(e)}

---

### 🔒 严格模式提醒

本验证器采用严格真实模式：
- ✅ 必须访问真实网页
- ✅ 必须获取真实HTML源代码
- ✅ 禁止任何Mock或示例HTML

---

### 📋 错误详情

```
{error_detail}
```

### 💡 建议

1. ✅ 检查URL是否正确且可访问
2. ✅ 检查选择器语法是否正确
3. ✅ 在浏览器中打开URL，使用开发者工具测试选择器
4. ✅ 确保这是一个真实的网页，不是Mock页面

**⚠️ 重要**: 本验证器禁止使用Mock或示例HTML，必须基于真实网页进行验证。
"""


@tool
def extract_from_real_web(
    url: str,
    selector: str,
    extract_attr: str = None,
    max_items: int = 20,
    runtime: ToolRuntime = None
) -> str:
    """
    📤 真实网页内容提取器 - 严格提取版
    
    从真实网页提取内容，禁止Mock
    
    功能特点：
    - 🔒 必须访问真实网页
    - 🔒 获取真实HTML源代码
    - 🔒 在真实HTML上提取内容
    - ✅ 支持提取文本或属性
    - ✅ 显示提取的完整内容
    
    参数:
        url: 真实网页的URL（必须可访问）
        selector: CSS选择器
        extract_attr: 要提取的属性（如'src', 'href'），留空则提取文本
        max_items: 最多提取的项目数量
    
    返回:
        提取结果报告
    """
    ctx = runtime.context if runtime else new_context(method="extract_from_real_web")
    
    try:
        # 获取真实网页验证器
        validator = get_real_web_validator()
        
        # 获取真实HTML
        print(f"🌐 正在访问真实网页: {url}")
        html_result = validator.fetch_real_html(url)
        
        if not html_result['success']:
            raise Exception(f"获取真实网页失败: {html_result.get('error', 'Unknown error')}")
        
        html = html_result['html']
        print(f"✅ 成功获取真实HTML，大小: {html_result['size']} 字符")
        
        # 从真实HTML提取内容
        print(f"📤 正在从真实HTML提取内容，选择器: {selector}")
        extract_result = validator.extract_from_real_html(
            selector=selector,
            html=html,
            extract_attr=extract_attr
        )
        
        # 构建报告
        report = f"""
## 📤 真实网页内容提取报告

### 📍 网页信息
- **URL**: {url}
- **HTML大小**: {html_result['size']} 字符
- **验证状态**: ✅ 已验证为真实网页HTML

---

### 🔬 提取结果

**选择器**: `{selector}`

**提取类型**: `{extract_attr if extract_attr else '文本'}`

**提取状态**: {'✅ 成功' if extract_result['success'] else '❌ 失败'}

**提取数量**: {extract_result['count']} 个项目

**消息**: {extract_result.get('message', '')}

---

### 📋 提取的内容

"""
        
        if extract_result.get('extracted'):
            for i, item in enumerate(extract_result['extracted'][:max_items], 1):
                report += f"""
**项目 {i}**: {item}
"""
        else:
            report += "❌ 未提取到任何内容\n"
        
        # 建议
        report += f"""

---

### 💡 使用建议

"""
        
        if extract_result['success'] and extract_result['count'] > 0:
            report += f"""
✅ 成功提取内容！

**下一步**:
1. 检查提取的内容是否符合预期
2. 如果用于书源规则，可以使用如下格式：
   - 提取文本: `{selector}@text`
   - 提取属性: `{selector}@{extract_attr}`
3. 如需过滤，可以添加正则表达式
"""
        else:
            report += f"""
❌ 未提取到内容或提取失败！

**可能的问题**:
1. 选择器未匹配到任何元素
2. 选择器语法错误
3. 页面结构可能已变化

**建议**:
1. 使用验证工具测试选择器有效性
2. 在浏览器开发者工具中检查元素
3. 使用智能分析器自动识别选择器
"""
        
        report += f"""

---

### 🔒 真实性保证

- ✅ 已访问真实网页
- ✅ HTML来源：真实网页源代码
- ✅ 内容从真实HTML提取
- ✅ 禁止任何Mock或示例
- ✅ 所有结果基于真实数据

---

### 📄 完整结果

```json
{json.dumps(extract_result, ensure_ascii=False, indent=2)}
```
"""
        
        return report.strip()
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 提取失败

**错误信息**: {str(e)}

---

### 🔒 严格模式提醒

本提取器采用严格真实模式：
- ✅ 必须访问真实网页
- ✅ 必须获取真实HTML源代码
- ✅ 禁止任何Mock或示例HTML

---

### 📋 错误详情

```
{error_detail}
```

### 💡 建议

1. ✅ 检查URL是否正确且可访问
2. ✅ 检查选择器语法是否正确
3. ✅ 使用验证工具先测试选择器有效性
4. ✅ 确保这是一个真实的网页，不是Mock页面

**⚠️ 重要**: 本提取器禁止使用Mock或示例HTML，必须基于真实网页进行提取。
"""
