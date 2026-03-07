"""
智能网站分析器
自动分析网站结构，智能构建请求，获取正确的列表内容
"""

import re
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from bs4 import BeautifulSoup
import requests
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

# 导入知识库搜索功能
try:
    from .knowledge_tools import _lightweight_search
except ImportError:
    def _lightweight_search(query: str, limit: int = 5) -> str:
        return "[WARNING] 知识库搜索功能不可用"


@tool
def smart_analyze_website(url: str, runtime: ToolRuntime = None) -> str:
    """
    智能分析网站结构，自动识别搜索、分页、列表等关键信息

    参数:
        url: 网站URL

    返回:
        网站结构分析报告
    """
    ctx = runtime.context if runtime else new_context(method="smart_analyze_website")

    try:
        # 🚨 第一阶段：收集信息（严格按照系统提示词）
        # 必须调用5个必查工具（系统提示词第48-53行）
        knowledge_context = ""
        
        # 1. 调用search_knowledge查询CSS选择器规则（第一步）
        try:
            css_result = _lightweight_search("CSS选择器格式 提取类型 @text @html @ownText @textNode @href @src", limit=3)
            if css_result and not "[ERROR]" in css_result:
                knowledge_context += f"## 📚 CSS选择器规则（第一步）\n\n{css_result}\n\n---\n"
        except Exception as e:
            knowledge_context += "⚠️ CSS选择器规则查询失败\n\n"
        
        # 2. 调用search_knowledge查询134个真实书源分析结果（第二步）
        try:
            analysis_result = _lightweight_search("134个真实书源分析 常用选择器 提取类型 正则模式", limit=3)
            if analysis_result and not "[ERROR]" in analysis_result:
                knowledge_context += f"## 📚 134个真实书源分析结果（第二步）\n\n{analysis_result}\n\n---\n"
        except Exception as e:
            knowledge_context += "⚠️ 134个真实书源分析结果查询失败\n\n"
        
        # 3. 调用search_knowledge查询真实书源模板（第三步）
        try:
            templates_result = _lightweight_search("真实书源模板 69书吧 笔趣阁 起点", limit=3)
            if templates_result and not "[ERROR]" in templates_result:
                knowledge_context += f"## 📚 真实书源模板（第三步）\n\n{templates_result}\n\n---\n"
        except Exception as e:
            knowledge_context += "⚠️ 真实书源模板查询失败\n\n"
        
        # 4. 调用search_knowledge查询POST请求配置（第四步）
        try:
            post_result = _lightweight_search("POST请求配置 method body String() webView charset", limit=3)
            if post_result and not "[ERROR]" in post_result:
                knowledge_context += f"## 📚 POST请求配置（第四步）\n\n{post_result}\n\n---\n"
        except Exception as e:
            knowledge_context += "⚠️ POST请求配置查询失败\n\n"
        
        # 5. 调用search_knowledge查询书源JSON结构（第五步）
        try:
            structure_result = _lightweight_search("书源JSON结构 BookSource 字段 searchUrl ruleSearch", limit=3)
            if structure_result and not "[ERROR]" in structure_result:
                knowledge_context += f"## 📚 书源JSON结构（第五步）\n\n{structure_result}\n\n---\n"
        except Exception as e:
            knowledge_context += "⚠️ 书源JSON结构查询失败\n\n"
        
        # 获取网页
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # 分析各个组件
        analysis = {
            'url': url,
            'search_info': _analyze_search_form(soup, url),
            'pagination_info': _analyze_pagination(soup, url),
            'list_structure': _analyze_list_structure(soup),
            'ajax_info': _analyze_ajax(soup),
            'security_info': _analyze_security(soup)
        }

        # 生成报告
        report = _generate_analysis_report(analysis)

        # 将知识库上下文添加到报告前面
        return knowledge_context + report

    except Exception as e:
        return f"[ERROR] 智能分析失败：{str(e)}"


@tool
def smart_build_search_request(base_url: str, search_keyword: str = "test", runtime: ToolRuntime = None) -> str:
    """
    智能构建搜索请求

    参数:
        base_url: 基础URL
        search_keyword: 搜索关键词（用于测试）

    返回:
        构建的搜索请求和预测的搜索结果页面URL
    """
    ctx = runtime.context if runtime else new_context(method="smart_build_search_request")

    try:
        # 先分析网站
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 访问基础页面
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # 分析搜索表单
        search_info = _analyze_search_form(soup, base_url)

        # 构建搜索URL
        search_requests = []

        if search_info['forms']:
            for form in search_info['forms']:
                request_info = {
                    'type': form['method'].upper(),
                    'url': form['action'],
                    'params': {},
                    'headers': {}
                }

                # 构建参数
                if form['method'].lower() == 'post':
                    # POST请求
                    request_info['params'] = {
                        input_field['name']: search_keyword
                        for input_field in form['inputs']
                        if input_field['type'] in ['text', 'search']
                    }
                else:
                    # GET请求
                    query_params = {}
                    for input_field in form['inputs']:
                        if input_field['type'] in ['text', 'search']:
                            query_params[input_field['name']] = search_keyword

                    if query_params:
                        # 将参数添加到URL
                        parsed = urlparse(form['action'])
                        existing_params = parse_qs(parsed.query)
                        existing_params.update(query_params)
                        new_query = urlencode(existing_params, doseq=True)
                        request_info['url'] = urlunparse((
                            parsed.scheme,
                            parsed.netloc,
                            parsed.path,
                            parsed.params,
                            new_query,
                            parsed.fragment
                        ))

                search_requests.append(request_info)

        # 如果没有找到表单，尝试URL参数检测
        if not search_requests:
            url_pattern = _detect_search_url_pattern(base_url, soup)
            if url_pattern:
                search_url = url_pattern.replace('{{key}}', search_keyword)
                search_requests.append({
                    'type': 'GET',
                    'url': search_url,
                    'params': {},
                    'headers': {}
                })

        # 生成报告
        report = _generate_search_request_report(search_requests, base_url, search_keyword)

        return report

    except Exception as e:
        return f"[ERROR] 智能构建搜索请求失败：{str(e)}"


@tool
def smart_fetch_list(url: str, page: int = 1, runtime: ToolRuntime = None) -> str:
    """
    智能获取列表页面，自动处理分页

    参数:
        url: 列表页面URL
        page: 页码（默认1）

    返回:
        列表内容和分页信息
    """
    ctx = runtime.context if runtime else new_context(method="smart_fetch_list")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 构建分页URL
        page_url = _build_page_url(url, page)

        # 获取页面
        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # 分析列表结构
        list_info = _analyze_list_structure(soup)

        # 分析分页信息
        pagination_info = _analyze_pagination(soup, url)

        # 提取列表项
        items = []
        if list_info['list_selectors']:
            for selector in list_info['list_selectors'][:3]:  # 尝试前3个选择器
                elements = soup.select(selector)
                if elements:
                    items = [{
                        'index': i,
                        'html': str(elem),
                        'text': elem.get_text(strip=True)[:200]
                    } for i, elem in enumerate(elements[:5])]  # 提取前5个
                    break

        # 生成报告
        report = _generate_list_fetch_report(page_url, html, list_info, pagination_info, items, page)

        return report

    except Exception as e:
        return f"[ERROR] 智能获取列表失败：{str(e)}"


def _analyze_search_form(soup: BeautifulSoup, base_url: str) -> Dict:
    """分析搜索表单"""
    forms = soup.find_all('form')

    search_forms = []

    for form in forms:
        form_info = {
            'action': urljoin(base_url, str(form.get('action', ''))),
            'method': str(form.get('method', 'GET')).upper(),
            'inputs': []
        }

        # 查找所有input元素
        inputs = form.find_all('input')
        for inp in inputs:
            input_info = {
                'type': inp.get('type', 'text'),
                'name': inp.get('name', ''),
                'id': inp.get('id', ''),
                'placeholder': inp.get('placeholder', ''),
                'value': inp.get('value', '')
            }
            if input_info['name']:
                form_info['inputs'].append(input_info)

        # 查找button元素
        buttons = form.find_all('button')
        for btn in buttons:
            if btn.get('type') in ['submit', ''] or not btn.get('type'):
                form_info['submit_button'] = btn.get_text(strip=True)[:50]
                break

        # 判断是否是搜索表单
        is_search = False
        search_keywords = ['search', 'query', 'keyword', 'q']
        for keyword in search_keywords:
            # 检查action
            if keyword in form_info['action'].lower():
                is_search = True
                break
            # 检查input的name
            for inp in form_info['inputs']:
                if keyword in inp['name'].lower() or keyword in inp.get('placeholder', '').lower():
                    is_search = True
                    break
            if is_search:
                break

        if is_search:
            search_forms.append(form_info)

    return {
        'found': len(search_forms) > 0,
        'forms': search_forms
    }


def _analyze_pagination(soup: BeautifulSoup, base_url: str) -> Dict:
    """分析分页信息"""
    pagination_info = {
        'found': False,
        'type': None,
        'page_param': None,
        'selectors': [],
        'total_pages': None
    }

    # 查找分页关键词
    pagination_keywords = ['page', 'pagination', 'pager', 'nav', 'next', 'prev', '上一页', '下一页']

    # 查找可能包含分页的元素
    for keyword in pagination_keywords:
        # 查找class包含关键词的元素
        by_class = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
        # 查找id包含关键词的元素
        by_id = soup.find_all(id=lambda x: x and keyword in str(x).lower())

        if by_class or by_id:
            pagination_info['found'] = True
            for elem in by_class[:3]:
                class_name = ' '.join(elem.get('class', []))
                pagination_info['selectors'].append(f".{class_name}")
            for elem in by_id[:3]:
                elem_id = elem.get('id')
                pagination_info['selectors'].append(f"#{elem_id}")
            break

    # 查找分页链接
    links = soup.find_all('a', href=True)
    page_pattern = re.compile(r'[?&](p|page|offset)=(\d+)', re.IGNORECASE)

    for link in links:
        href = link.get('href', '')
        match = page_pattern.search(href)
        if match:
            pagination_info['found'] = True
            pagination_info['type'] = 'url_param'
            pagination_info['page_param'] = match.group(1)
            break

    return pagination_info


def _analyze_list_structure(soup: BeautifulSoup) -> Dict:
    """分析列表结构"""
    list_selectors = []

    # 常见的列表容器class
    list_keywords = ['list', 'item', 'book', 'article', 'post', 'content', 'card']

    for keyword in list_keywords:
        # 查找包含列表特征的容器
        by_class = soup.find_all(class_=lambda x: x and keyword in str(x).lower())
        for elem in by_class[:5]:
            class_name = ' '.join(elem.get('class', []))
            # 检查是否有多个相似的子元素（说明是列表）
            children = elem.find_all(recursive=False)
            if len(children) >= 3:
                list_selectors.append(f".{class_name}")

    # 查找ul/ol列表
    for tag in ['ul', 'ol']:
        lists = soup.find_all(tag)
        for lst in lists[:3]:
            items = lst.find_all('li', recursive=False)
            if len(items) >= 3:
                if lst.get('class'):
                    class_name = ' '.join(lst.get('class', []))
                    list_selectors.append(f"{tag}.{class_name}")
                elif lst.get('id'):
                    list_selectors.append(f"{tag}#{lst.get('id')}")
                else:
                    list_selectors.append(tag)

    return {
        'list_selectors': list_selectors[:10],  # 最多返回10个
        'recommended': list_selectors[0] if list_selectors else None
    }


def _analyze_ajax(soup: BeautifulSoup) -> Dict:
    """分析AJAX加载"""
    ajax_info = {
        'found': False,
        'apis': [],
        'js_files': []
    }

    # 查找script标签中的API调用
    scripts = soup.find_all('script')
    for script in scripts:
        if script.get('src'):
            ajax_info['js_files'].append(script.get('src'))
        else:
            js_content = script.string
            if js_content:
                # 查找常见的API模式
                api_patterns = [
                    r'fetch\([\'"]([^\'"]+)[\'"]\)',
                    r'\$\.ajax\([\'"]([^\'"]+)[\'"]\)',
                    r'axios\.get\([\'"]([^\'"]+)[\'"]\)',
                    r'api/[\w/]+'
                ]
                for pattern in api_patterns:
                    matches = re.findall(pattern, js_content)
                    if matches:
                        ajax_info['found'] = True
                        ajax_info['apis'].extend(matches)

    return ajax_info


def _analyze_security(soup: BeautifulSoup) -> Dict:
    """分析安全特性"""
    security_info = {
        'csrf_token': None,
        'requires_login': False,
        'has_captcha': False
    }

    # 查找CSRF token
    csrf_patterns = ['csrf', 'token', '_token']
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        name = str(meta.get('name', '')).lower()
        content = str(meta.get('content', ''))
        if any(pattern in name for pattern in csrf_patterns):
            security_info['csrf_token'] = content

    # 查找登录相关元素
    login_keywords = ['login', '登录', 'signin']
    for keyword in login_keywords:
        if soup.find(text=re.compile(keyword, re.IGNORECASE)):
            security_info['requires_login'] = True
            break

    # 查找验证码
    captcha_keywords = ['captcha', '验证码', 'recaptcha']
    for keyword in captcha_keywords:
        if soup.find(text=re.compile(keyword, re.IGNORECASE)):
            security_info['has_captcha'] = True
            break

    return security_info


def _detect_search_url_pattern(base_url: str, soup: BeautifulSoup) -> Optional[str]:
    """检测搜索URL模式"""
    # 查找链接中的搜索模式
    links = soup.find_all('a', href=True)

    search_patterns = []
    for link in links:
        href = str(link.get('href', ''))
        if any(keyword in href.lower() for keyword in ['search', 'query', 'q=']):
            # 提取URL模式
            pattern = re.sub(r'=[^&]+', '={{key}}', href)
            search_patterns.append(pattern)

    if search_patterns:
        return search_patterns[0]

    return None


def _build_page_url(base_url: str, page: int) -> str:
    """构建分页URL"""
    parsed = urlparse(base_url)

    # 尝试常见的分页参数
    page_params = ['page', 'p', 'offset', 'start']

    existing_params = parse_qs(parsed.query)

    # 如果已有分页参数，更新它
    updated = False
    for param in page_params:
        if param in existing_params:
            existing_params[param] = [str(page)]
            updated = True
            break

    # 如果没有分页参数，添加page参数
    if not updated:
        existing_params['page'] = [str(page)]

    new_query = urlencode(existing_params, doseq=True)

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))


def _generate_analysis_report(analysis: Dict) -> str:
    """生成分析报告"""
    report = f"""
## [ANALYSIS] 智能网站分析报告

### [INFO] 基本信息
- **URL**: {analysis['url']}

### [SEARCH] 搜索功能分析

"""

    if analysis['search_info']['found']:
        report += f"[OK] 找到 {len(analysis['search_info']['forms'])} 个搜索表单\n\n"

        for i, form in enumerate(analysis['search_info']['forms'], 1):
            report += f"#### 表单 #{i}\n\n"
            report += f"- **请求方式**: {form['method']}\n"
            report += f"- **提交地址**: `{form['action']}`\n"
            report += f"- **参数字段**: {len(form['inputs'])} 个\n\n"

            if form['inputs']:
                report += "**字段列表**:\n"
                for inp in form['inputs'][:5]:
                    report += f"  - `{inp['name']}` ({inp['type']})"
                    if inp['placeholder']:
                        report += f" - 提示: {inp['placeholder']}"
                    report += "\n"
                report += "\n"

            if form.get('submit_button'):
                report += f"- **提交按钮**: {form['submit_button']}\n\n"
    else:
        report += "[ERROR] 未找到搜索表单\n\n"
        report += "[TIP] 可能的搜索方式：\n"
        report += "1. URL参数搜索（如 ?q=keyword）\n"
        report += "2. JavaScript动态搜索\n"
        report += "3. 需要登录后才能搜索\n\n"

    report += "### [DOC] 分页功能分析\n\n"

    if analysis['pagination_info']['found']:
        report += "[OK] 找到分页功能\n\n"
        report += f"- **分页类型**: {analysis['pagination_info'].get('type', '未知')}\n"
        report += f"- **分页参数**: `{analysis['pagination_info'].get('page_param', '未知')}`\n"

        if analysis['pagination_info']['selectors']:
            report += f"- **分页选择器**:\n"
            for selector in analysis['pagination_info']['selectors'][:3]:
                report += f"  - `{selector}`\n"
        report += "\n"
    else:
        report += "[ERROR] 未找到分页功能\n\n"
        report += "[TIP] 可能是无限滚动或AJAX加载\n\n"

    report += "### [INFO] 列表结构分析\n\n"

    if analysis['list_structure']['list_selectors']:
        report += f"[OK] 找到 {len(analysis['list_structure']['list_selectors'])} 个可能的列表容器\n\n"
        report += "**推荐选择器**:\n"

        for i, selector in enumerate(analysis['list_structure']['list_selectors'][:5], 1):
            marker = "[STAR]" if i == 1 else f"{i}."
            report += f"{marker} `{selector}`\n"

        if analysis['list_structure']['recommended']:
            report += f"\n**最推荐**: `{analysis['list_structure']['recommended']}`\n"
    else:
        report += "[ERROR] 未找到明显的列表结构\n\n"

    report += "\n### [SECURE] 安全特性分析\n\n"

    security = analysis['security_info']
    if security['csrf_token']:
        report += f"[WARNING] 检测到CSRF Token: `{security['csrf_token'][:20]}...`\n\n"

    if security['requires_login']:
        report += "[WARNING] 可能需要登录\n\n"

    if security['has_captcha']:
        report += "[WARNING] 检测到验证码\n\n"

    if not any([security['csrf_token'], security['requires_login'], security['has_captcha']]):
        report += "[OK] 未检测到特殊安全限制\n\n"

    report += """
### [TIP] 书源编写建议

#### 1. 搜索URL构建
"""
    if analysis['search_info']['found']:
        report += "根据搜索表单，可以使用以下格式构建搜索URL：\n\n"
        for form in analysis['search_info']['forms']:
            if form['method'] == 'GET':
                param_names = [inp['name'] for inp in form['inputs'] if inp['type'] in ['text', 'search']]
                if param_names:
                    report += f"- `{form['action']}?{param_names[0]}={{{{key}}}}`\n"
    else:
        report += "未找到搜索表单，可能需要手动分析URL模式\n\n"

    report += """
#### 2. 选择器建议
"""
    if analysis['list_structure']['recommended']:
        report += f"使用推荐的选择器：`{analysis['list_structure']['recommended']}`\n\n"
        report += "然后分析子元素提取：\n"
        report += "- 书名：`.title@text`\n"
        report += "- 作者：`.author@text`\n"
        report += "- 链接：`a@href`\n\n"

    report += """
#### 3. 下一步操作

1. 使用 `smart_build_search_request` 构建实际的搜索请求
2. 使用 `smart_fetch_list` 获取列表内容
3. 根据返回的列表结构编写选择器
4. 使用 `edit_book_source` 创建完整的书源
    """

    return report


def _generate_search_request_report(requests: List[Dict], base_url: str, keyword: str) -> str:
    """生成搜索请求报告"""
    report = f"""
## [CONFIG] 智能搜索请求构建报告

### [INFO] 基础信息
- **基础URL**: {base_url}
- **测试关键词**: {keyword}
- **找到的请求方式**: {len(requests)} 个

### [INFO] 请求列表

"""

    if not requests:
        report += "[ERROR] 未能自动构建搜索请求\n\n"
        report += "[TIP] 建议：\n"
        report += "1. 手动查找网站的搜索功能\n"
        report += "2. 使用浏览器开发者工具分析网络请求\n"
        report += "3. 查看网站的JavaScript代码\n\n"
        return report

    for i, req in enumerate(requests, 1):
        report += f"#### 请求 #{i}\n\n"
        report += f"- **请求方式**: {req['type']}\n"
        report += f"- **请求URL**: `{req['url']}`\n\n"

        if req['params']:
            report += "**请求参数**:\n"
            for key, value in req['params'].items():
                report += f"  - `{key}`: `{value}`\n"
            report += "\n"

        report += "**Legado书源配置**:\n\n"
        if req['type'] == 'GET':
            report += f"```json\n"
            report += f'{{\n'
            report += f'  "searchUrl": "{req["url"].replace(keyword, "{{{{key}}}}")}"\n'
            report += f'}}\n'
            report += "```\n\n"
        else:
            report += "POST请求，需要在请求头中添加配置\n\n"

    report += """
### [TEST] 测试建议

1. 将上面的searchUrl复制到书源配置中
2. 使用 `smart_fetch_list` 测试实际效果
3. 根据返回结果调整参数

### 📚 书源编写下一步

1. 使用 `edit_book_source` 创建书源
2. 填入上面的searchUrl
3. 使用 `smart_fetch_list` 获取列表内容
4. 编写ruleSearch规则
5. 在Legado APP中测试
    """

    return report


def _generate_list_fetch_report(url: str, html: str, list_info: Dict, pagination_info: Dict, items: List, page: int) -> str:
    """生成列表获取报告"""
    report = f"""
## [DOC] 列表获取报告

### [INFO] 请求信息
- **URL**: {url}
- **页码**: {page}
- **页面大小**: {len(html)} 字节

### [INFO] 列表结构分析

"""

    if list_info['recommended']:
        report += f"[OK] 推荐列表选择器: `{list_info['recommended']}`\n\n"
    elif list_info['list_selectors']:
        report += f"[OK] 找到 {len(list_info['list_selectors'])} 个可能的列表容器\n\n"
        for selector in list_info['list_selectors'][:3]:
            report += f"- `{selector}`\n"
    else:
        report += "[ERROR] 未找到明显的列表结构\n\n"
        report += "[TIP] 可能的原因：\n"
        report += "1. 列表由JavaScript动态加载\n"
        report += "2. 需要登录才能访问\n"
        report += "3. URL不正确\n\n"

    report += "### [DOC] 列表项内容（前5项）\n\n"

    if items:
        for item in items:
            report += f"#### 项目 #{item['index']}\n\n"
            report += f"**文本**: {item['text']}\n\n"
            report += "**HTML片段**:\n```html\n"
            report += item['html'][:300]
            report += "\n```\n\n"
    else:
        report += "[ERROR] 未能提取列表项\n\n"
        report += "[TIP] 可能的原因：\n"
        report += "1. 列表由JavaScript动态加载\n"
        report += "2. 需要登录才能访问\n"
        report += "3. URL不正确\n\n"

    report += "### [DOC] 完整HTML源代码（用于参考）\n\n"
    report += "```html\n"
    # 返回完整的HTML（不截断）
    report += html
    report += "\n```\n\n"

    report += "### [DOC] 分页信息\n\n"

    if pagination_info['found']:
        report += f"[OK] 找到分页功能\n"
        report += f"- **分页参数**: `{pagination_info.get('page_param', 'page')}`\n"
        report += f"- **下一页URL**: {_build_page_url(url, page + 1)}\n\n"
    else:
        report += "[ERROR] 未找到分页功能\n\n"

    report += """
### [TIP] 选择器编写建议

根据上面的列表项内容，可以编写以下选择器：

```json
{
  "ruleSearch": {
    "bookList": "推荐的列表选择器",
    "name": "书名元素选择器@text",
    "author": "作者元素选择器@text",
    "bookUrl": "链接元素选择器@href"
  }
}
```

### 📚 下一步操作

1. 参考上面的完整HTML源代码，查看实际的页面结构
2. 根据列表项的HTML结构编写详细的选择器
3. **严格按照知识库中的规则**编写选择器语法
4. 使用 `edit_book_source` 更新书源规则
5. 使用 `smart_fetch_list` 测试其他页面
6. 在Legado APP中实际测试

### [WARNING] 重要提示

**编写规则时必须**：
1. **严格按照知识库内容**：查看 `assets/legado_knowledge_base.md` 和 `assets/css选择器规则.txt`
2. **参考实际HTML**：根据上面完整HTML源代码中的实际结构编写
3. **准确使用语法**：确保CSS选择器、提取类型等语法正确
4. **测试验证**：必须在Legado APP中实际测试，模拟结果仅供参考
    """

    return report


def urljoin(base: str, url: str) -> str:
    """简单的URL拼接"""
    from urllib.parse import urljoin as _urljoin
    return _urljoin(base, url)
