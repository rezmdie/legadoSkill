"""
Legado书源调试工具
用于测试完整的书源规则

使用方法:
    from src.tools.book_source_debugger import BookSourceDebugger
    
    # 创建调试器
    debugger = BookSourceDebugger()
    
    # 加载书源JSON
    book_source = debugger.load_book_source("path/to/source.json")
    
    # 测试搜索规则
    debugger.test_search(book_source, "斗破苍穹")
    
    # 测试书籍信息规则
    debugger.test_book_info(book_source, "https://example.com/book/12345.html")
    
    # 测试目录规则
    debugger.test_toc(book_source, "https://example.com/book/12345.html")
    
    # 测试正文规则
    debugger.test_content(book_source, "https://example.com/chapter/12345.html")
"""

import json
import requests
from typing import Dict, List, Any, Optional
from tools.legado_debugger import LegadoDebugger
import logging

logger = logging.getLogger(__name__)


class BookSourceDebugger:
    """书源调试器"""

    def __init__(self):
        self.debugger = None
        self.book_source = None
        self.http_client = requests.Session()
        self.http_client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def load_book_source(self, book_source_json: str) -> Dict:
        """
        加载书源JSON

        Args:
            book_source_json: 书源JSON字符串或文件路径

        Returns:
            书源字典
        """
        if book_source_json.startswith('{') or book_source_json.startswith('['):
            # 直接是JSON字符串
            try:
                if book_source_json.startswith('['):
                    sources = json.loads(book_source_json)
                    self.book_source = sources[0] if sources else {}
                else:
                    self.book_source = json.loads(book_source_json)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                return {}
        else:
            # 是文件路径
            try:
                with open(book_source_json, 'r', encoding='utf-8') as f:
                    sources = json.load(f)
                    self.book_source = sources[0] if isinstance(sources, list) else sources
            except Exception as e:
                logger.error(f"文件读取失败: {e}")
                return {}

        logger.info(f"成功加载书源: {self.book_source.get('bookSourceName', '未知书源')}")
        return self.book_source

    def fetch_html(self, url: str, method: str = "GET", body: str = None, headers: Dict = None) -> str:
        """
        获取HTML内容

        Args:
            url: URL
            method: HTTP方法
            body: 请求体
            headers: 请求头

        Returns:
            HTML内容
        """
        try:
            if method.upper() == "POST":
                response = self.http_client.post(url, data=body, headers=headers, timeout=10)
            else:
                response = self.http_client.get(url, headers=headers, timeout=10)

            response.raise_for_status()
            response.encoding = response.apparent_encoding

            return response.text
        except Exception as e:
            logger.error(f"获取HTML失败: {url}, 错误: {e}")
            return ""

    def test_search(self, book_source: Dict, keyword: str) -> Dict:
        """
        测试搜索规则

        Args:
            book_source: 书源字典
            keyword: 搜索关键词

        Returns:
            搜索结果
        """
        logger.info(f"\n=== 测试搜索规则 ===")
        logger.info(f"关键词: {keyword}")

        # 构建搜索URL
        search_url = book_source.get("searchUrl", "")
        if "{{key}}" in search_url:
            search_url = search_url.replace("{{key}}", keyword)

        logger.info(f"搜索URL: {search_url}")

        # 获取搜索结果HTML
        html = self.fetch_html(search_url)
        if not html:
            logger.error("获取搜索页面失败")
            return {}

        self.debugger = LegadoDebugger(html, book_source.get("bookSourceUrl", ""))

        # 解析搜索结果
        rule_search = book_source.get("ruleSearch", {})
        book_list_rule = rule_search.get("bookList", "")
        name_rule = rule_search.get("name", "")
        author_rule = rule_search.get("author", "")
        book_url_rule = rule_search.get("bookUrl", "")
        cover_url_rule = rule_search.get("coverUrl", "")

        results = []

        if book_list_rule:
            # 获取书籍列表元素
            book_elements = self.debugger.get_string_list(book_list_rule)

            for i, _ in enumerate(book_elements):
                result = {
                    "index": i + 1,
                }

                # 提取书名
                if name_rule:
                    result["name"] = self.debugger.get_string(name_rule)
                    logger.info(f"  书名: {result['name']}")

                # 提取作者
                if author_rule:
                    result["author"] = self.debugger.get_string(author_rule)
                    logger.info(f"  作者: {result['author']}")

                # 提取书籍URL
                if book_url_rule:
                    result["bookUrl"] = self.debugger.get_string(book_url_rule)
                    logger.info(f"  书籍URL: {result['bookUrl']}")

                # 提取封面
                if cover_url_rule:
                    result["coverUrl"] = self.debugger.get_string(cover_url_rule)
                    logger.info(f"  封面: {result['coverUrl']}")

                results.append(result)
                if i >= 2:  # 只显示前3个结果
                    logger.info("  ...")
                    break

        logger.info(f"\n找到 {len(results)} 个结果")
        return {"results": results}

    def test_book_info(self, book_source: Dict, book_url: str) -> Dict:
        """
        测试书籍信息规则

        Args:
            book_source: 书源字典
            book_url: 书籍详情页URL

        Returns:
            书籍信息
        """
        logger.info(f"\n=== 测试书籍信息规则 ===")
        logger.info(f"书籍URL: {book_url}")

        # 获取书籍详情页HTML
        html = self.fetch_html(book_url)
        if not html:
            logger.error("获取书籍详情页失败")
            return {}

        self.debugger = LegadoDebugger(html, book_source.get("bookSourceUrl", ""))

        # 解析书籍信息
        rule_book_info = book_source.get("ruleBookInfo", {})
        name_rule = rule_book_info.get("name", "")
        author_rule = rule_book_info.get("author", "")
        cover_url_rule = rule_book_info.get("coverUrl", "")
        intro_rule = rule_book_info.get("intro", "")
        kind_rule = rule_book_info.get("kind", "")
        last_chapter_rule = rule_book_info.get("lastChapter", "")

        book_info = {}

        # 提取书名
        if name_rule:
            book_info["name"] = self.debugger.get_string(name_rule)
            logger.info(f"  书名: {book_info['name']}")

        # 提取作者
        if author_rule:
            book_info["author"] = self.debugger.get_string(author_rule)
            logger.info(f"  作者: {book_info['author']}")

        # 提取封面
        if cover_url_rule:
            book_info["coverUrl"] = self.debugger.get_string(cover_url_rule)
            logger.info(f"  封面: {book_info['coverUrl']}")

        # 提取简介
        if intro_rule:
            book_info["intro"] = self.debugger.get_string(intro_rule)
            logger.info(f"  简介: {book_info['intro'][:50]}..." if len(book_info.get('intro', '')) > 50 else f"  简介: {book_info.get('intro', '')}")

        # 提取分类
        if kind_rule:
            book_info["kind"] = self.debugger.get_string(kind_rule)
            logger.info(f"  分类: {book_info['kind']}")

        # 提取最新章节
        if last_chapter_rule:
            book_info["lastChapter"] = self.debugger.get_string(last_chapter_rule)
            logger.info(f"  最新章节: {book_info['lastChapter']}")

        return book_info

    def test_toc(self, book_source: Dict, toc_url: str, max_chapters: int = 5) -> Dict:
        """
        测试目录规则

        Args:
            book_source: 书源字典
            toc_url: 目录页URL
            max_chapters: 最大显示章节数

        Returns:
            目录列表
        """
        logger.info(f"\n=== 测试目录规则 ===")
        logger.info(f"目录URL: {toc_url}")

        # 获取目录页HTML
        html = self.fetch_html(toc_url)
        if not html:
            logger.error("获取目录页失败")
            return {}

        self.debugger = LegadoDebugger(html, book_source.get("bookSourceUrl", ""))

        # 解析目录
        rule_toc = book_source.get("ruleToc", {})
        chapter_list_rule = rule_toc.get("chapterList", "")
        chapter_name_rule = rule_toc.get("chapterName", "")
        chapter_url_rule = rule_toc.get("chapterUrl", "")

        chapters = []

        if chapter_list_rule:
            # 获取章节列表
            chapter_elements = self.debugger.get_string_list(chapter_list_rule)

            for i, _ in enumerate(chapter_elements):
                chapter = {
                    "index": i + 1,
                }

                # 提取章节名
                if chapter_name_rule:
                    chapter["name"] = self.debugger.get_string(chapter_name_rule)

                # 提取章节URL
                if chapter_url_rule:
                    chapter["url"] = self.debugger.get_string(chapter_url_rule)

                if chapter.get("name"):
                    logger.info(f"  章节 {chapter['index']}: {chapter['name']}")
                    if chapter.get("url"):
                        logger.info(f"    URL: {chapter['url']}")

                    chapters.append(chapter)

                    if i >= max_chapters - 1:
                        logger.info(f"  ... (共 {len(chapter_elements)} 章)")
                        break

        logger.info(f"\n显示前 {len(chapters)} 章")
        return {"chapters": chapters}

    def test_content(self, book_source: Dict, chapter_url: str) -> Dict:
        """
        测试正文规则

        Args:
            book_source: 书源字典
            chapter_url: 章节URL

        Returns:
            正文内容
        """
        logger.info(f"\n=== 测试正文规则 ===")
        logger.info(f"章节URL: {chapter_url}")

        # 获取章节页HTML
        html = self.fetch_html(chapter_url)
        if not html:
            logger.error("获取章节页失败")
            return {}

        self.debugger = LegadoDebugger(html, book_source.get("bookSourceUrl", ""))

        # 解析正文
        rule_content = book_source.get("ruleContent", {})
        content_rule = rule_content.get("content", "")
        next_content_url_rule = content_rule.get("nextContentUrl", "")

        content = {}

        # 提取正文内容
        if content_rule:
            text = self.debugger.get_string(content_rule)
            content["text"] = text
            logger.info(f"  正文长度: {len(text)} 字符")
            logger.info(f"  正文预览: {text[:100]}...")

        # 提取下一页链接
        if next_content_url_rule:
            next_url = self.debugger.get_string(next_content_url_rule)
            content["nextUrl"] = next_url
            logger.info(f"  下一页URL: {next_url}")

        return content

    def run_full_test(self, book_source_json: str, keyword: str = "斗破苍穹") -> Dict:
        """
        运行完整测试

        Args:
            book_source_json: 书源JSON
            keyword: 测试关键词

        Returns:
            测试结果
        """
        logger.info("=" * 60)
        logger.info("Legado书源完整测试")
        logger.info("=" * 60)

        # 加载书源
        book_source = self.load_book_source(book_source_json)
        if not book_source:
            logger.error("加载书源失败")
            return {}

        test_results = {
            "bookSourceName": book_source.get("bookSourceName", "未知"),
            "bookSourceUrl": book_source.get("bookSourceUrl", ""),
            "search": {},
            "bookInfo": {},
            "toc": {},
            "content": {}
        }

        # 测试搜索
        if "ruleSearch" in book_source and book_source["ruleSearch"]:
            test_results["search"] = self.test_search(book_source, keyword)

        # 测试书籍信息（使用搜索结果中的第一个）
        if test_results["search"].get("results") and test_results["search"]["results"][0].get("bookUrl"):
            book_url = test_results["search"]["results"][0]["bookUrl"]
            # 转换为绝对URL
            if not book_url.startswith("http"):
                base_url = book_source.get("bookSourceUrl", "")
                book_url = f"{base_url.rstrip('/')}/{book_url.lstrip('/')}"
            test_results["bookInfo"] = self.test_book_info(book_source, book_url)

            # 测试目录
            toc_url = book_url  # 假设目录页和详情页是同一个
            test_results["toc"] = self.test_toc(book_source, toc_url)

            # 测试正文
            if test_results["toc"].get("chapters") and test_results["toc"]["chapters"][0].get("url"):
                chapter_url = test_results["toc"]["chapters"][0]["url"]
                if not chapter_url.startswith("http"):
                    base_url = book_source.get("bookSourceUrl", "")
                    chapter_url = f"{base_url.rstrip('/')}/{chapter_url.lstrip('/')}"
                test_results["content"] = self.test_content(book_source, chapter_url)

        logger.info("\n" + "=" * 60)
        logger.info("测试完成")
        logger.info("=" * 60)

        return test_results


def test_book_source_debugger():
    """测试书源调试器"""
    print("=== 书源调试器测试 ===\n")

    # 测试书源JSON
    test_source = {
        "bookSourceName": "测试书源",
        "bookSourceUrl": "https://example.com",
        "searchUrl": "/search?q={{key}}",
        "ruleSearch": {
            "bookList": ".book-item",
            "name": ".title@text",
            "author": ".author@text",
            "bookUrl": "a@href",
            "coverUrl": "img@src"
        },
        "ruleBookInfo": {
            "name": "h1@text",
            "author": ".author@text",
            "coverUrl": ".cover img@src",
            "intro": ".intro@text"
        },
        "ruleToc": {
            "chapterList": ".chapter-list li",
            "chapterName": "a@text",
            "chapterUrl": "a@href"
        },
        "ruleContent": {
            "content": ".content@html",
            "nextContentUrl": "text.下一章@href"
        }
    }

    debugger = BookSourceDebugger()

    # 只测试搜索和书籍信息
    book_source_json = json.dumps([test_source])
    debugger.load_book_source(book_source_json)

    print("✅ 书源调试器测试完成")


if __name__ == "__main__":
    test_book_source_debugger()
