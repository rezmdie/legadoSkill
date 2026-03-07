"""
网站源代码获取工具
用于获取指定网站的HTML源代码，以便分析页面结构并编写书源规则
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def fetch_web_page(url: str, render_js: bool = False, timeout: int = 30, runtime: ToolRuntime = None) -> str:
    """
    获取网站的HTML源代码

    参数:
        url: 网站URL（完整地址，如 https://example.com）
        render_js: 是否渲染JavaScript（默认False，仅获取静态HTML）
        timeout: 请求超时时间（秒，默认30）

    返回:
        HTML源代码和页面结构分析
    """
    ctx = runtime.context if runtime else new_context(method="fetch_web_page")

    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'

        html = response.text

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 分析页面结构
        analysis = _analyze_page_structure(soup, url)

        # 构建结果
        result = f"""
## [WEB] 网站源代码获取成功

### [STATS] 基本信息
- **URL**: {url}
- **状态码**: {response.status_code}
- **字符编码**: {response.encoding}
- **页面大小**: {len(html)} 字节
- **是否渲染JS**: {'是' if render_js else '否（仅静态HTML）'}

### 🏗️ 页面结构分析

{analysis}

### [NOTE] 完整HTML源代码（用于参考）

```html
{html}
```

### [TIP] 下一步建议

1. **查看页面结构**：分析上面的结构分析，找到目标元素的class、id等
2. **提取元素信息**：根据需要，可以要求我提取特定元素的HTML
3. **编写选择器**：根据结构分析，使用CSS选择器或JSOUP语法编写规则
4. **测试验证**：使用 `debug_book_source` 工具测试选择器是否正确

### [WARNING] 重要提示

**编写规则时必须**：
1. **严格按照知识库内容**：查看 `assets/legado_knowledge_base.md` 和 `assets/css选择器规则.txt`
2. **参考实际HTML**：根据上面完整HTML源代码中的实际结构编写
3. **准确使用语法**：确保CSS选择器、提取类型等语法正确
4. **测试验证**：必须在Legado APP中实际测试，模拟结果仅供参考

### [LINK] 知识库参考

- **核心规则文档**: `assets/legado_knowledge_base.md`
- **CSS选择器规则**: `assets/css选择器规则.txt`
- **书源规则说明**: `assets/书源规则：从入门到入土.md`

**注意事项**：
- 如果网站使用了JavaScript动态加载内容，可能需要使用 `render_js=True` 或浏览器工具
- 某些网站可能有反爬机制，需要特殊的请求头或Cookie
- 建议在实际环境中测试书源，因为模拟环境可能与真实环境有差异
        """

        return result

    except requests.Timeout:
        return f"[ERROR] 请求超时：网站 {url} 响应时间过长（超过 {timeout} 秒）\n\n[TIP] 建议：\n1. 检查网站是否可访问\n2. 增加超时时间\n3. 检查网络连接"
    except requests.exceptions.SSLError:
        return f"[ERROR] SSL证书错误：网站 {url} 的证书可能过期或无效\n\n[TIP] 建议：\n1. 检查网站URL是否正确\n2. 网站可能需要使用https协议"
    except requests.exceptions.ConnectionError:
        return f"[ERROR] 连接错误：无法连接到网站 {url}\n\n[TIP] 建议：\n1. 检查URL是否正确\n2. 检查网络连接\n3. 网站可能已关闭或需要特殊访问方式"
    except Exception as e:
        return f"[ERROR] 获取网页失败：{str(e)}\n\n[TIP] 建议：\n1. 检查URL格式是否正确\n2. 确认网站是否可访问\n3. 尝试使用浏览器访问该URL"


@tool
def extract_elements(html: str, selector: str = "", tag: str = "", class_name: str = "", id_name: str = "", runtime: ToolRuntime = None) -> str:
    """
    从HTML中提取特定元素

    参数:
        html: HTML源代码字符串
        selector: CSS选择器（优先使用）
        tag: HTML标签名（如div, a, img）
        class_name: class属性值
        id_name: id属性值

    返回:
        提取的元素列表和详细信息
    """
    ctx = runtime.context if runtime else new_context(method="extract_elements")

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # 根据参数查找元素
        if selector:
            elements = soup.select(selector)
        elif tag:
            elements = soup.find_all(tag, class_=class_name, id=id_name)
        else:
            return "[ERROR] 必须提供selector或tag参数"

        if not elements:
            return f"[ERROR] 未找到匹配的元素\n\n[TIP] 建议：\n1. 检查选择器是否正确\n2. 查看完整的HTML源代码\n3. 尝试使用更宽松的选择器"

        # 构建结果
        result = f"""
## [SEARCH] 元素提取结果

### [STATS] 基本信息
- **匹配元素数量**: {len(elements)}
- **使用的查询方式**: {f"CSS选择器: {selector}" if selector else f"标签: {tag}, class: {class_name}, id: {id_name}"}

### [INFO] 元素详情

"""
        # 最多显示前10个元素
        for i, elem in enumerate(elements[:10], 1):
            result += f"#### 元素 #{i}\n\n"

            # 基本信息
            tag_name = elem.name
            elem_id = elem.get('id', '')
            elem_class = ' '.join(elem.get('class', []))
            elem_text = elem.get_text(strip=True)[:100]

            result += f"- **标签**: `{tag_name}`\n"
            if elem_id:
                result += f"- **ID**: `{elem_id}`\n"
            if elem_class:
                result += f"- **Class**: `{elem_class}`\n"
            result += f"- **文本**: {elem_text}\n\n"

            # 建议的选择器
            if elem_id:
                result += f"[OK] **推荐选择器**: `#{elem_id}`\n\n"
            elif elem_class:
                result += f"[OK] **推荐选择器**: `.{elem_class.split()[0]}`\n\n"

            # 显示HTML片段
            elem_html = str(elem)[:300]
            result += f"**HTML片段**:\n```html\n{elem_html}\n{'...' if len(str(elem)) > 300 else ''}\n```\n\n"

        if len(elements) > 10:
            result += f"\n... 还有 {len(elements) - 10} 个元素未显示\n"

        result += f"""
### [TIP] 选择器建议

基于提取到的元素，以下是常用的选择器写法：

**优先级从高到低**：
1. **ID选择器**（最稳定）：`#元素ID`
2. **类选择器**：`.类名`
3. **标签+类选择器**：`标签.类名`
4. **属性选择器**：`[属性名="属性值"]`
5. **结构选择器**：`父元素 > 子元素`

**示例**：
```json
{{
  "ruleSearch": {{
    "bookList": ".book-item",
    "name": "h2.title@text",
    "author": ".author@text",
    "bookUrl": "a@href"
  }}
}}
```

### 📚 下一步操作

1. 使用 `edit_book_source` 工具创建或编辑书源
2. 将上面的选择器填入对应的规则字段
3. 使用 `debug_book_source` 工具测试规则
4. 根据测试结果调整选择器
        """

        return result

    except Exception as e:
        return f"[ERROR] 提取元素失败：{str(e)}"


@tool
def analyze_search_structure(url: str, runtime: ToolRuntime = None) -> str:
    """
    分析网站的搜索页面结构

    参数:
        url: 搜索页面的URL

    返回:
        搜索页面结构分析，包括表单、输入框、按钮等元素
    """
    ctx = runtime.context if runtime else new_context(method="analyze_search_structure")

    try:
        # 获取网页
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # 查找搜索相关元素
        result = f"""
## [SEARCH] 搜索页面结构分析

### [STATS] 基本信息
- **URL**: {url}
- **状态码**: {response.status_code}

### 🏷️ 搜索表单分析

"""

        # 查找form元素
        forms = soup.find_all('form')
        if forms:
            result += f"#### 表单元素 ({len(forms)} 个)\n\n"
            for i, form in enumerate(forms[:5], 1):
                result += f"**表单 #{i}**\n\n"
                result += f"- **Action**: `{form.get('action', '无')}`\n"
                result += f"- **Method**: `{form.get('method', 'GET')}`\n\n"

                # 查找input元素
                inputs = form.find_all('input')
                if inputs:
                    result += "**输入框**:\n"
                    for inp in inputs:
                        inp_type = inp.get('type', 'text')
                        inp_name = inp.get('name', '无')
                        inp_placeholder = inp.get('placeholder', '无')
                        result += f"  - 类型: `{inp_type}`, 名称: `{inp_name}`, 提示: `{inp_placeholder}`\n"
                    result += "\n"
        else:
            result += "[ERROR] 未找到表单元素（可能是AJAX搜索）\n\n"

        # 查找搜索相关的class和id
        result += "#### 可能的搜索容器\n\n"
        search_keywords = ['search', 'query', 'keyword', 'input', 'form']

        found_elements = []
        for keyword in search_keywords:
            # 查找class包含关键词的元素
            by_class = soup.find_all(class_=lambda x: x and keyword.lower() in str(x).lower())
            # 查找id包含关键词的元素
            by_id = soup.find_all(id=lambda x: x and keyword.lower() in str(x).lower())

            if by_class:
                for elem in by_class[:3]:
                    elem_info = {
                        'selector': f".{'.'.join(elem.get('class', []))}",
                        'tag': elem.name,
                        'text': elem.get_text(strip=True)[:50]
                    }
                    found_elements.append(elem_info)

            if by_id:
                for elem in by_id[:3]:
                    elem_info = {
                        'selector': f"#{elem.get('id')}",
                        'tag': elem.name,
                        'text': elem.get_text(strip=True)[:50]
                    }
                    found_elements.append(elem_info)

        if found_elements:
            result += "**可能的选择器**:\n\n"
            for i, elem_info in enumerate(found_elements[:10], 1):
                result += f"{i}. `{elem_info['selector']}` - {elem_info['tag']} - {elem_info['text']}\n"
        else:
            result += "[ERROR] 未找到明显的搜索容器\n\n"

        result += f"""
### [TIP] 书源编写建议

**搜索URL构建**：
```
搜索URL = 基础URL + 搜索参数
```

**示例**：
```json
{{
  "searchUrl": "https://example.com/search?q={{key}}&page={{page}}",
  "ruleSearch": {{
    "bookList": ".book-item",
    "name": "h2@text",
    "author": ".author@text",
    "bookUrl": "a@href"
  }}
}}
```

### 📚 下一步操作

1. 根据上面的分析，确定搜索URL的格式
2. 使用 `fetch_web_page` 获取搜索结果页面的HTML
3. 使用 `extract_elements` 提取搜索结果列表的元素
4. 使用 `edit_book_source` 创建完整的书源
        """

        return result

    except Exception as e:
        return f"[ERROR] 分析搜索结构失败：{str(e)}\n\n[TIP] 建议：\n1. 检查URL是否正确\n2. 确认网站是否有搜索功能\n3. 尝试使用浏览器访问该URL"


def _analyze_page_structure(soup, url):
    """分析页面结构"""
    analysis = ""

    # 标题
    title = soup.find('title')
    if title:
        analysis += f"- **页面标题**: {title.get_text(strip=True)}\n"

    # Meta描述
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        analysis += f"- **页面描述**: {description.get('content', '无')}\n"

    # 常见的容器元素
    common_containers = ['content', 'main', 'article', 'post', 'item', 'list']
    analysis += "\n**常见容器元素**:\n\n"

    for keyword in common_containers:
        by_class = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
        by_id = soup.find_all(id=lambda x: x and keyword in str(x).lower())

        if by_class or by_id:
            analysis += f"- `{keyword}`: 找到 {len(by_class) + len(by_id)} 个元素\n"

            # 显示示例
            if by_class:
                example = by_class[0]
                class_name = ' '.join(example.get('class', []))
                analysis += f"  示例选择器: `.{class_name}`\n"
            if by_id:
                example = by_id[0]
                analysis += f"  示例选择器: `#{example.get('id')}`\n"

            analysis += "\n"

    # 链接分析
    links = soup.find_all('a', href=True)
    if links:
        analysis += f"**链接数量**: {len(links)}\n"

        # 统计链接类型
        internal_links = [l for l in links if urljoin(url, l['href']).startswith(url)]
        external_links = len(links) - len(internal_links)
        analysis += f"- 内部链接: {len(internal_links)}\n"
        analysis += f"- 外部链接: {external_links}\n\n"

    # 图片分析
    images = soup.find_all('img', src=True)
    if images:
        analysis += f"**图片数量**: {len(images)}\n\n"

    return analysis
