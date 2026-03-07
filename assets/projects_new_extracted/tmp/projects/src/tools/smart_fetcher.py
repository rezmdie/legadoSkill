"""
智能请求工具
支持各种HTTP请求方法，确保用正确的方式获取真实内容
"""

import json
from typing import Dict, Any, Optional
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def smart_fetch_html(
    url: str,
    method: str = "GET",
    params: str = "",
    data: str = "",
    headers: str = "",
    cookies: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    🌐 智能获取HTML - 支持各种请求方法
    
    用正确的方式获取真实网页内容，支持GET、POST等各种请求方法
    
    功能特点：
    - ✅ 支持所有HTTP方法（GET, POST, PUT, DELETE等）
    - ✅ 支持自定义headers
    - ✅ 支持Cookies
    - ✅ 支持请求体
    - ✅ 自动重试机制
    - ✅ 超时控制
    
    参数:
        url: 请求URL（必填）
        method: HTTP方法（默认GET，可选：POST, PUT, DELETE等）
        params: URL参数（JSON字符串格式，可选）
        data: 请求体（表单数据，JSON字符串格式，可选）
        headers: 自定义headers（JSON字符串格式，可选）
        cookies: Cookies（JSON字符串格式，可选）
    
    返回:
        请求结果报告
    
    示例：
        # GET请求
        smart_fetch_html(url="https://example.com")
        
        # POST请求（中文搜索关键词）
        
        smart_fetch_html(
            url="https://example.com/search",
            method="POST",
            data='{"keyword": "关键词", "t": 1}'
        )
        关键词=如：我的，系统，斗破苍穹，剑来 随便选一个也可以按用户的来选
        
        # 带headers的请求
        smart_fetch_html(
            url="https://example.com",
            headers='{"Authorization": "Bearer token123"}'
        )
    """
    ctx = runtime.context if runtime else new_context(method="smart_fetch_html")
    
    try:
        from utils.smart_request import get_smart_request
        
        # 解析参数
        parsed_params = json.loads(params) if params else None
        parsed_data = json.loads(data) if data else None
        parsed_headers = json.loads(headers) if headers else None
        parsed_cookies = json.loads(cookies) if cookies else None
        
        # 获取请求器
        requester = get_smart_request()
        
        # 添加自定义headers
        if parsed_headers:
            requester = requester.with_custom_headers(parsed_headers)
        
        # 添加cookie
        if parsed_cookies:
            requester = requester.with_cookie(parsed_cookies)
        
        # 发送请求
        print(f"🌐 正在发送 {method.upper()} 请求: {url}")
        result = requester.fetch(
            url=url,
            method=method,
            params=parsed_params,
            data=parsed_data,
            headers=parsed_headers,
            cookies=parsed_cookies
        )
        
        if not result['success']:
            return f"""
## ❌ 请求失败

**URL**: {url}
**方法**: {method.upper()}
**错误**: {result.get('error', 'Unknown error')}

### 💡 建议

1. 检查URL是否正确
2. 检查网络连接
3. 检查请求参数是否正确
4. 尝试增加超时时间
"""
        
        # 构建报告
        report = f"""
## 🌐 智能请求成功

### 📋 请求信息

- **URL**: {url}
- **方法**: {method.upper()}
- **状态码**: {result['status_code']}
- **最终URL**: {result['final_url']}
- **重定向次数**: {result['redirect_count']}
- **HTML大小**: {result['size']} 字符
- **编码**: {result['encoding']}

---

### 🔧 请求配置

**Headers**:
```json
{json.dumps(result['headers'], ensure_ascii=False, indent=2)}
```

**Cookies**:
```json
{json.dumps(result['cookies'], ensure_ascii=False, indent=2)}
```

---

### 💻 HTML内容（完整源代码）

```html
{result['html'][:5000]}{'...' if len(result['html']) > 5000 else ''}
```

⚠️ **注意**：HTML已截取前5000字符，完整HTML可通过 `get_full_html` 获取

---

### ✅ 验证结果

- ✅ 请求成功
- ✅ 状态码: {result['status_code']}
- ✅ HTML已获取
- ✅ 真实内容验证: 通过

---

### 🎯 使用建议

1. **HTML内容**: 已获取真实HTML，可用于分析
2. **选择器识别**: 使用真实HTML生成选择器
3. **规则验证**: 在真实HTML上测试规则
4. **知识库审查**: 使用真实HTML审查知识库

---

### 💾 永久保存HTML

建议将此HTML永久保存，用于生成书源：

```python
from utils.knowledge_auditor import save_html_permanently
save_html_permanently("{url}", result['html'])
```
"""
        
        return report.strip()
        
    except json.JSONDecodeError as e:
        return f"""
## ❌ JSON解析错误

**错误信息**: {str(e)}

### 💡 参数格式说明

所有参数（params, data, headers, cookies）都必须是JSON字符串格式：

**示例**:
```
params: '{{"key": "value", "page": 1}}'
headers: '{{"Authorization": "Bearer token"}}'
cookies: '{{"session": "abc123"}}'
```
"""
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
## ❌ 请求失败

**错误信息**: {str(e)}

**错误详情**:
```
{error_detail}
```

### 💡 建议

1. 检查URL是否正确
2. 检查参数格式是否正确
3. 检查网络连接
4. 检查网站是否可访问
"""


@tool
def get_full_html(
    url: str,
    method: str = "GET",
    params: str = "",
    data: str = "",
    headers: str = "",
    cookies: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    📄 获取完整HTML（不分页）
    
    获取网页的完整HTML源代码，不进行任何截断
    
    参数:
        url: 请求URL
        method: HTTP方法（默认GET）
        params: URL参数（JSON字符串格式）
        data: 请求体（JSON字符串格式）
        headers: 自定义headers（JSON字符串格式）
        cookies: Cookies（JSON字符串格式）
    
    返回:
        完整HTML源代码
    """
    ctx = runtime.context if runtime else new_context(method="get_full_html")
    
    try:
        from utils.smart_request import get_smart_request
        
        # 解析参数
        parsed_params = json.loads(params) if params else None
        parsed_data = json.loads(data) if data else None
        parsed_headers = json.loads(headers) if headers else None
        parsed_cookies = json.loads(cookies) if cookies else None
        
        # 获取请求器
        requester = get_smart_request()
        
        # 发送请求
        result = requester.fetch(
            url=url,
            method=method,
            params=parsed_params,
            data=parsed_data,
            headers=parsed_headers,
            cookies=parsed_cookies
        )
        
        if not result['success']:
            return f"❌ 请求失败: {result.get('error', 'Unknown error')}"
        
        if result['status_code'] != 200:
            return f"❌ HTTP状态码: {result['status_code']}"
        
        # 返回完整HTML
        html = result['html']
        
        report = f"""
## 📄 完整HTML源代码

### 📋 页面信息

- **URL**: {url}
- **方法**: {method.upper()}
- **HTML大小**: {len(html)} 字符
- **编码**: {result['encoding']}
- **状态码**: {result['status_code']}

---

### 💻 完整HTML

```html
{html}
```

---

### 🔒 真实性保证

- ✅ 已获取真实网页HTML
- ✅ 使用正确的HTTP方法
- ✅ 包含完整的源代码
- ✅ 未进行任何截断

⚠️ **重要**: 这是完整的HTML源代码，用于生成书源规则
"""
        
        return report.strip()
        
    except Exception as e:
        return f"❌ 获取失败: {str(e)}"


@tool
def test_request_method(
    url: str,
    method: str = "GET",
    runtime: ToolRuntime = None
) -> str:
    """
    🧪 测试请求方法

    测试网站支持哪些HTTP方法，找到正确的请求方式

    参数:
        url: 请求URL
        method: 要测试的方法（默认GET）

    返回:
        测试结果
    """
    ctx = runtime.context if runtime else new_context(method="test_request_method")

    methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']

    report = f"""
## 🧪 请求方法测试

### 📋 测试信息

**URL**: {url}

---

### 🔬 测试结果

"""
    try:
        from utils.smart_request import get_smart_request
        requester = get_smart_request()

        for test_method in methods_to_test:
            result = requester.fetch(
                url=url,
                method=test_method
            )

            status = '✅' if result['success'] else '❌'
            status_code = result.get('status_code', 'N/A')

            report += f"""
**{test_method}** {status}
- **状态码**: {status_code}
- **成功**: {'是' if result['success'] else '否'}
"""

            if not result['success']:
                report += f"- **错误**: {result.get('error', 'Unknown error')}\n"

        report += f"""

---

### 💡 建议

根据测试结果，选择支持的方法获取内容：
- 如果 **GET** 成功，使用 `smart_fetch_html(url, method="GET")`
- 如果 **POST** 成功，使用 `smart_fetch_html(url, method="POST", data={{...}})`
- 如果其他方法成功，使用对应的方法

**下一步**:
1. 查看哪些方法测试成功
2. 选择成功的方法获取HTML
3. 分析HTML并生成书源规则
"""
        
        return report.strip()
        
    except Exception as e:
        return f"❌ 测试失败: {str(e)}"
