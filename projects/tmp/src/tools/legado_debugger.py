"""
Legado书源规则调试器
模拟Legado的规则解析功能，用于调试书源规则

该模块实现了Legado的核心规则解析功能：
- Default规则解析（使用BeautifulSoup替代JSoup）
- XPath规则解析（使用lxml）
- JsonPath规则解析（使用jsonpath-ng）
- 正则表达式处理
- 变量替换

作者：Legado书源驯兽师
"""

import re
import json
import logging
from typing import Any, List, Dict, Optional, Union
from bs4 import BeautifulSoup, Tag, NavigableString
from lxml import etree
from jsonpath_ng import parse
from urllib.parse import urljoin, urlparse
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleMode:
    """规则模式枚举"""
    DEFAULT = "Default"
    XPATH = "XPath"
    JSON = "Json"
    JS = "Js"
    WEB_JS = "WebJs"


class SourceRule:
    """单个规则项"""

    def __init__(self, rule_str: str):
        self.rule_str = rule_str
        self.mode = RuleMode.DEFAULT
        self.rule = ""
        self.replace_regex = ""
        self.replace_value = ""
        self.put_map = {}

        self._parse_rule()

    def _parse_rule(self):
        """解析规则字符串"""
        # 解析规则模式
        if self.rule_str.startswith("@XPath:"):
            self.mode = RuleMode.XPATH
            self.rule = self.rule_str[7:]
        elif self.rule_str.startswith("@Json:"):
            self.mode = RuleMode.JSON
            self.rule = self.rule_str[6:]
        elif self.rule_str.startswith("@js:"):
            self.mode = RuleMode.JS
            self.rule = self.rule_str[4:]
        elif self.rule_str.startswith("@WebJs:"):
            self.mode = RuleMode.WEB_JS
            self.rule = self.rule_str[7:]
        elif self.rule_str.startswith("//") or self.rule_str.startswith("/"):
            self.mode = RuleMode.XPATH
            self.rule = self.rule_str
        elif self.rule_str.startswith("$."):
            self.mode = RuleMode.JSON
            self.rule = self.rule_str
        else:
            self.mode = RuleMode.DEFAULT
            self.rule = self.rule_str

        # 解析正则替换（##分隔）
        parts = re.split(r'##(.+?)(?:##|$)', self.rule, maxsplit=1)
        if len(parts) > 1:
            self.rule = parts[0]
            regex_match = parts[1] if parts[1] else ""
            if regex_match:
                # 检查是否有替换值
                replace_parts = re.split(r'##(.*)$', regex_match, maxsplit=1)
                self.replace_regex = replace_parts[0]
                if len(replace_parts) > 1:
                    self.replace_value = replace_parts[1]

    def get_param_size(self) -> int:
        """获取参数数量"""
        return len(re.findall(r'\{\{\w+\}\}', self.rule))


class LegadoDebugger:
    """Legado规则调试器"""

    def __init__(self, html_content: str = "", base_url: str = ""):
        """
        初始化调试器

        Args:
            html_content: HTML内容
            base_url: 基础URL
        """
        self.content = html_content
        self.base_url = base_url
        self.soup = None
        self.json_data = None
        self.variables = {}

        if html_content:
            self._init_html(html_content)

    def _init_html(self, html_content: str):
        """初始化HTML解析"""
        try:
            self.soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")

    def set_content(self, content: str):
        """设置内容"""
        self.content = content
        self._init_html(content)

    def set_base_url(self, base_url: str):
        """设置基础URL"""
        self.base_url = base_url

    def get_string(self, rule_str: str, content: str = None) -> str:
        """
        根据规则获取字符串

        Args:
            rule_str: 规则字符串
            content: 内容（可选）

        Returns:
            提取的字符串
        """
        if not rule_str:
            return ""

        content = content or self.content
        if not content:
            return ""

        rule = SourceRule(rule_str)

        # 根据模式解析
        if rule.mode == RuleMode.DEFAULT:
            result = self._parse_default(rule.rule, content)
        elif rule.mode == RuleMode.XPATH:
            result = self._parse_xpath(rule.rule, content)
        elif rule.mode == RuleMode.JSON:
            result = self._parse_jsonpath(rule.rule, content)
        else:
            result = rule.rule

        # 应用正则替换
        if result and rule.replace_regex:
            result = self._apply_regex(result, rule.replace_regex, rule.replace_value)

        return result or ""

    def get_string_list(self, rule_str: str, content: str = None) -> List[str]:
        """
        根据规则获取字符串列表

        Args:
            rule_str: 规则字符串
            content: 内容（可选）

        Returns:
            提取的字符串列表
        """
        if not rule_str:
            return []

        content = content or self.content
        if not content:
            return []

        rule = SourceRule(rule_str)

        # 根据模式解析列表
        if rule.mode == RuleMode.DEFAULT:
            results = self._parse_default_list(rule.rule, content)
        elif rule.mode == RuleMode.XPATH:
            results = self._parse_xpath_list(rule.rule, content)
        elif rule.mode == RuleMode.JSON:
            results = self._parse_jsonpath_list(rule.rule, content)
        else:
            results = [rule.rule]

        # 应用正则替换
        if rule.replace_regex:
            results = [self._apply_regex(r, rule.replace_regex, rule.replace_value) or ""
                       for r in results]

        return results

    def _parse_default(self, rule: str, content: str) -> str:
        """
        解析Default规则

        Default规则格式：CSS选择器@提取类型

        示例：
        - .title@text - 提取文本
        - .title@href - 提取href属性
        - .title@html - 提取HTML
        - text.下一章@href - 根据文本查找并提取href
        - .title.0@text - 提取第一个元素
        - .title.-1@text - 提取最后一个元素

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串
        """
        if not self.soup:
            return ""

        parts = rule.split('@')

        # text.文本@属性 格式
        if len(parts) == 2 and parts[0].startswith('text.'):
            text_match = parts[0][5:]
            attr = parts[1]

            # 查找包含指定文本的元素
            element = self.soup.find(string=text_match)
            if element:
                element = element.parent
                if attr == 'text':
                    return element.get_text(strip=True)
                elif attr == 'html':
                    return str(element)
                elif attr:
                    return element.get(attr, "")

            return ""

        # 标准CSS选择器@属性格式
        elif len(parts) == 2:
            selector = parts[0]
            attr = parts[1]

            # 处理位置索引（如 .0, .-1）
            index = None
            if selector.count('.') >= 1:
                # 分离选择器和索引
                selector_parts = selector.split('.')
                if selector_parts[-1].lstrip('-').isdigit():
                    selector = '.'.join(selector_parts[:-1])
                    index = int(selector_parts[-1])

            elements = self.soup.select(selector)

            if elements:
                # 处理索引
                if index is not None:
                    if index < 0:
                        index = len(elements) + index
                    if 0 <= index < len(elements):
                        elements = [elements[index]]
                    else:
                        return ""

                # 处理排除规则（如 0:1,3:5）
                # 简化实现：只取第一个元素
                element = elements[0]

                if attr == 'text':
                    return element.get_text(strip=True)
                elif attr == 'html':
                    return str(element)
                elif attr == 'ownText':
                    return ''.join([str(child).strip() for child in element.children if not isinstance(child, Tag)])
                elif attr == 'textNodes':
                    return ' '.join([str(child).strip() for child in element.children if not isinstance(child, Tag)])
                elif attr:
                    return element.get(attr, "")

        return ""

    def _parse_default_list(self, rule: str, content: str) -> List[str]:
        """
        解析Default规则获取列表

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串列表
        """
        if not self.soup:
            return []

        parts = rule.split('@')

        if len(parts) != 2:
            return []

        selector = parts[0]
        attr = parts[1]

        elements = self.soup.select(selector)

        results = []
        for element in elements:
            if attr == 'text':
                results.append(element.get_text(strip=True))
            elif attr == 'html':
                results.append(str(element))
            elif attr == 'ownText':
                results.append(''.join([str(child).strip() for child in element.children if not isinstance(child, Tag)]))
            elif attr == 'textNodes':
                results.append(' '.join([str(child).strip() for child in element.children if not isinstance(child, Tag)]))
            elif attr:
                results.append(element.get(attr, ""))

        return results

    def _parse_xpath(self, rule: str, content: str) -> str:
        """
        解析XPath规则

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串
        """
        try:
            html = etree.HTML(content)
            result = html.xpath(rule)

            if result:
                if isinstance(result[0], etree._Element):
                    return result[0].text or ""
                else:
                    return str(result[0])
        except Exception as e:
            logger.error(f"XPath解析失败: {rule}, 错误: {e}")

        return ""

    def _parse_xpath_list(self, rule: str, content: str) -> List[str]:
        """
        解析XPath规则获取列表

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串列表
        """
        try:
            html = etree.HTML(content)
            results = html.xpath(rule)

            return [str(r).strip() if not isinstance(r, etree._Element) else (r.text or "")
                    for r in results]
        except Exception as e:
            logger.error(f"XPath解析失败: {rule}, 错误: {e}")

        return []

    def _parse_jsonpath(self, rule: str, content: str) -> str:
        """
        解析JsonPath规则

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串
        """
        try:
            if not self.json_data:
                self.json_data = json.loads(content)

            jsonpath_expression = parse(rule)
            result = jsonpath_expression.find(self.json_data)

            if result:
                return str(result[0].value)
        except Exception as e:
            logger.error(f"JsonPath解析失败: {rule}, 错误: {e}")

        return ""

    def _parse_jsonpath_list(self, rule: str, content: str) -> List[str]:
        """
        解析JsonPath规则获取列表

        Args:
            rule: 规则字符串
            content: 内容

        Returns:
            提取的字符串列表
        """
        try:
            if not self.json_data:
                self.json_data = json.loads(content)

            jsonpath_expression = parse(rule)
            results = jsonpath_expression.find(self.json_data)

            return [str(r.value) for r in results]
        except Exception as e:
            logger.error(f"JsonPath解析失败: {rule}, 错误: {e}")

        return []

    def _apply_regex(self, text: str, pattern: str, replacement: str = "") -> str:
        """
        应用正则表达式

        Args:
            text: 文本
            pattern: 正则表达式
            replacement: 替换字符串

        Returns:
            替换后的文本
        """
        try:
            if not pattern:
                return text

            # 检查是否是捕获组格式（如 $1）
            if '$' in replacement and '(' in pattern:
                # 使用捕获组
                match = re.search(pattern, text)
                if match:
                    # 替换捕获组
                    result = text
                    for i, group in enumerate(match.groups(), 1):
                        result = result.replace(f'${i}', group or '')
                    # 删除匹配的部分
                    result = re.sub(pattern, replacement, result)
                    return result
                else:
                    return text
            else:
                # 普通替换
                return re.sub(pattern, replacement, text)
        except Exception as e:
            logger.error(f"正则替换失败: {pattern}, 错误: {e}")
            return text


def test_debugger():
    """测试调试器"""
    print("=== Legado规则调试器测试 ===\n")

    # 测试HTML
    html = """
    <div class="book-list">
        <div class="item">
            <h1 class="title">斗破苍穹</h1>
            <p class="author">作者：天蚕土豆</p>
            <a href="/book/12345.html">查看详情</a>
        </div>
        <div class="item">
            <h1 class="title">完美世界</h1>
            <p class="author">作者：辰东</p>
            <a href="/book/67890.html">查看详情</a>
        </div>
    </div>

    <div class="nav">
        <a href="/chapter/1_2.html">下一页</a>
        <a href="/chapter/2.html">下一章</a>
    </div>
    """

    debugger = LegadoDebugger(html, "https://example.com")

    # 测试Default规则
    print("1. 测试CSS选择器@text:")
    print(f"   规则: .title@text")
    print(f"   结果: {debugger.get_string('.title@text')}")
    print()

    print("2. 测试CSS选择器@href:")
    print(f"   规则: a@href")
    print(f"   结果: {debugger.get_string('a@href')}")
    print()

    print("3. 测试text.文本@href:")
    print(f"   规则: text.下一章@href")
    print(f"   结果: {debugger.get_string('text.下一章@href')}")
    print()

    print("4. 测试位置索引:")
    print(f"   规则: .title.-1@text")
    print(f"   结果: {debugger.get_string('.title.-1@text')}")
    print()

    print("5. 测试正则替换:")
    print(f"   规则: .author@text##.*作者：##")
    print(f"   结果: {debugger.get_string('.author@text##.*作者：##')}")
    print()

    print("6. 测试列表提取:")
    print(f"   规则: .title@text")
    print(f"   结果: {debugger.get_string_list('.title@text')}")
    print()


if __name__ == "__main__":
    test_debugger()
