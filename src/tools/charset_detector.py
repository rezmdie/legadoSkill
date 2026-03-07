"""
网站编码检测工具

用于智能检测网站的编码类型（UTF-8、GBK、GB2312、GB18030等）
"""

import re
import json
from typing import Dict, Optional, Tuple
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

import requests
from bs4 import BeautifulSoup


def detect_from_headers(response: requests.Response) -> Optional[str]:
    """
    从 HTTP 响应头中检测编码

    Args:
        response: requests Response 对象

    Returns:
        编码类型（如 'gbk', 'utf-8'）或 None
    """
    content_type = response.headers.get('Content-Type', '')
    if not content_type:
        return None

    # 查找 charset 参数
    match = re.search(r'charset\s*=\s*["\']?([^"\';\s,]+)', content_type, re.IGNORECASE)
    if match:
        charset = match.group(1).lower()
        # 标准化一些常见的编码名称
        charset_map = {
            'gb2312': 'gbk',
            'gb18030': 'gbk',
            'x-gbk': 'gbk',
            'x-gb2312': 'gbk',
            'utf8': 'utf-8',
            'iso-8859-1': 'latin-1',
        }
        return charset_map.get(charset, charset)

    return None


def detect_from_meta(html_content: str) -> Optional[str]:
    """
    从 HTML meta 标签中检测编码

    Args:
        html_content: HTML 内容

    Returns:
        编码类型（如 'gbk', 'utf-8'）或 None
    """
    # 匹配 <meta charset="..."> 格式
    charset_pattern = r'<meta[^>]+charset\s*=\s*["\']?([^"\';\s>]+)["\']?'
    match = re.search(charset_pattern, html_content, re.IGNORECASE)
    if match:
        charset = match.group(1).lower()
        # 标准化编码名称
        charset_map = {
            'gb2312': 'gbk',
            'gb18030': 'gbk',
            'x-gbk': 'gbk',
            'utf8': 'utf-8',
        }
        return charset_map.get(charset, charset)

    # 匹配 <meta http-equiv="Content-Type" content="..."> 格式
    meta_pattern = r'<meta\s+http-equiv\s*=\s*["\']?Content-Type["\']?[^>]*content\s*=\s*["\'][^"\']*charset\s*=\s*["\']?([^"\';\s,]+)'
    match = re.search(meta_pattern, html_content, re.IGNORECASE)
    if match:
        charset = match.group(1).lower()
        charset_map = {
            'gb2312': 'gbk',
            'gb18030': 'gbk',
            'x-gbk': 'gbk',
            'utf8': 'utf-8',
        }
        return charset_map.get(charset, charset)

    return None


def detect_by_content(html_content: str) -> Tuple[str, float]:
    """
    通过内容分析检测编码（使用 chardet）

    Args:
        html_content: HTML 内容

    Returns:
        (编码类型, 置信度)
    """
    if not CHARDET_AVAILABLE:
        return 'utf-8', 0.0

    try:
        # 将字符串转换为字节（使用 latin-1 保留原始字节）
        bytes_content = html_content.encode('latin-1')

        # 使用 chardet 检测编码
        result = chardet.detect(bytes_content)
        charset = result['encoding'].lower() if result['encoding'] else 'utf-8'
        confidence = result['confidence'] or 0.0

        # 标准化编码名称
        charset_map = {
            'gb2312': 'gbk',
            'gb18030': 'gbk',
            'big5': 'gbk',  # 繁体中文也归类到 gbk（对于简单场景）
        }

        normalized_charset = charset_map.get(charset, charset)

        # 对于中文，优先返回 gbk 或 utf-8
        if 'gb' in charset or 'big5' in charset:
            normalized_charset = 'gbk'

        return normalized_charset, confidence
    except Exception as e:
        return 'utf-8', 0.0


def detect_by_chinese_characters(html_content: str) -> Tuple[str, float]:
    """
    通过中文字符特征检测编码

    Args:
        html_content: HTML 内容

    Returns:
        (编码类型, 置信度)
    """
    try:
        # 尝试使用不同的编码解码，看哪种能正确解码中文字符
        encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'big5']
        results = {}

        for encoding in encodings_to_try:
            try:
                decoded = html_content.encode('latin-1').decode(encoding)
                # 统计中文字符数量
                chinese_chars = len([c for c in decoded if '\u4e00' <= c <= '\u9fff'])
                results[encoding] = chinese_chars
            except:
                results[encoding] = 0

        # 找到中文字符最多的编码
        best_encoding = max(results.items(), key=lambda x: x[1])[0]

        # 计算置信度
        total_chars = len(results[best_encoding])
        confidence = min(0.95, results[best_encoding] / max(total_chars, 1)) if total_chars > 0 else 0.0

        return best_encoding, confidence
    except:
        return 'utf-8', 0.0


@tool
def detect_charset(url: str, max_retries: int = 3, timeout: int = 10, runtime: ToolRuntime = None) -> str:
    """
    智能检测网站的编码类型

    该工具会通过多种方式检测网站编码：
    1. 检查 HTTP 响应头中的 Content-Type
    2. 检查 HTML meta 标签中的 charset
    3. 使用 chardet 库进行内容分析（如果可用）
    4. 通过中文字符特征推断

    Args:
        url: 要检测的网站 URL
        max_retries: 最大重试次数，默认为 3
        timeout: 请求超时时间（秒），默认为 10

    Returns:
        JSON 格式的检测结果，包含：
        - charset: 检测到的编码类型（如 'utf-8', 'gbk'）
        - confidence: 置信度（0.0 - 1.0）
        - source: 检测来源（headers/meta/content/characters/fallback）
        - details: 详细信息（所有检测方法的结果）

    Examples:
        >>> detect_charset("https://www.example.com")
        >>> detect_charset("https://www.69shuba.com")
    """
    ctx = runtime.context if runtime else new_context(method="detect_charset")

    result = {
        "url": url,
        "charset": "utf-8",  # 默认值
        "confidence": 0.0,
        "source": "fallback",
        "details": {
            "headers": None,
            "meta": None,
            "content": None,
            "characters": None
        },
        "errors": []
    }

    try:
        # 发送 HTTP 请求
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            allow_redirects=True
        )

        # 获取 HTML 内容
        html_content = response.text

        # 1. 从 HTTP 响应头检测
        headers_charset = detect_from_headers(response)
        result["details"]["headers"] = headers_charset

        if headers_charset:
            result["charset"] = headers_charset
            result["confidence"] = 0.95
            result["source"] = "headers"

        # 2. 从 HTML meta 标签检测
        meta_charset = detect_from_meta(html_content)
        result["details"]["meta"] = meta_charset

        if meta_charset and meta_charset != result["charset"]:
            # 如果 meta 标签与响应头不一致，优先使用 meta 标签
            result["charset"] = meta_charset
            result["confidence"] = 0.9
            result["source"] = "meta"

        # 3. 使用 chardet 进行内容分析
        if CHARDET_AVAILABLE:
            content_charset, content_confidence = detect_by_content(html_content)
            result["details"]["content"] = {
                "charset": content_charset,
                "confidence": content_confidence
            }

            # 如果置信度高且与当前结果不一致，更新结果
            if content_confidence > 0.8 and content_charset != result["charset"]:
                result["charset"] = content_charset
                result["confidence"] = content_confidence
                result["source"] = "content"

        # 4. 通过中文字符特征检测（作为验证）
        char_charset, char_confidence = detect_by_chinese_characters(html_content)
        result["details"]["characters"] = {
            "charset": char_charset,
            "confidence": char_confidence
        }

        # 如果多种检测结果一致，提高置信度
        if (result["details"]["headers"] == result["charset"] and
            result["details"]["meta"] == result["charset"]):
            result["confidence"] = 0.99

        # 5. 特殊情况处理：对于常见的中文老网站，即使检测为 UTF-8，也可能是 GBK
        # 如果检测为 UTF-8 但中文显示异常，可能是 GBK
        if result["charset"] == "utf-8" and char_confidence > 0.7:
            # 检查是否有明显的编码错误迹象
            try:
                utf8_decoded = html_content.encode('latin-1').decode('utf-8')
                # 检查是否有替换字符
                if '\ufffd' in utf8_decoded:
                    result["charset"] = "gbk"
                    result["source"] = "characters_fallback"
                    result["errors"].append("UTF-8 解码出现替换字符，可能是 GBK 编码")
            except:
                pass

        # 生成配置建议
        result["recommendation"] = {
            "charset_config": f'"{result["charset"]}"',
            "usage_example": f'/search,{{"charset":"{result["charset"]}"}}'
        }

    except requests.exceptions.Timeout:
        result["errors"].append(f"请求超时（{timeout}秒）")
        result["charset"] = "utf-8"
        result["confidence"] = 0.0
    except requests.exceptions.RequestException as e:
        result["errors"].append(f"请求失败: {str(e)}")
        result["charset"] = "utf-8"
        result["confidence"] = 0.0
    except Exception as e:
        result["errors"].append(f"检测失败: {str(e)}")
        result["charset"] = "utf-8"
        result["confidence"] = 0.0

    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def detect_charset_from_html(html_content: str) -> str:
    """
    从 HTML 内容中检测编码

    该工具会通过分析 HTML meta 标签和内容特征来检测编码

    Args:
        html_content: HTML 内容字符串

    Returns:
        JSON 格式的检测结果，包含：
        - charset: 检测到的编码类型（如 'utf-8', 'gbk'）
        - confidence: 置信度（0.0 - 1.0）
        - source: 检测来源（meta/content/characters）
        - details: 详细信息

    Examples:
        >>> html = '<html><head><meta charset="gbk"></head><body>内容</body></html>'
        >>> detect_charset_from_html(html)
    """
    result = {
        "charset": "utf-8",  # 默认值
        "confidence": 0.0,
        "source": "fallback",
        "details": {
            "meta": None,
            "content": None,
            "characters": None
        },
        "errors": []
    }

    try:
        # 1. 从 HTML meta 标签检测
        meta_charset = detect_from_meta(html_content)
        result["details"]["meta"] = meta_charset

        if meta_charset:
            result["charset"] = meta_charset
            result["confidence"] = 0.9
            result["source"] = "meta"

        # 2. 使用 chardet 进行内容分析
        if CHARDET_AVAILABLE:
            content_charset, content_confidence = detect_by_content(html_content)
            result["details"]["content"] = {
                "charset": content_charset,
                "confidence": content_confidence
            }

            if content_confidence > 0.8:
                result["charset"] = content_charset
                result["confidence"] = content_confidence
                result["source"] = "content"

        # 3. 通过中文字符特征检测
        char_charset, char_confidence = detect_by_chinese_characters(html_content)
        result["details"]["characters"] = {
            "charset": char_charset,
            "confidence": char_confidence
        }

        # 生成配置建议
        result["recommendation"] = {
            "charset_config": f'"{result["charset"]}"',
            "usage_example": f'/search,{{"charset":"{result["charset"]}"}}'
        }

    except Exception as e:
        result["errors"].append(f"检测失败: {str(e)}")

    return json.dumps(result, ensure_ascii=False, indent=2)


# 导出工具列表
__all__ = ['detect_charset', 'detect_charset_from_html']
