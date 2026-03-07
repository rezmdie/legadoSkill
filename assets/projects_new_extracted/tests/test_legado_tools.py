"""
测试Legado调试工具
验证所有功能是否正常工作
"""

import sys
sys.path.insert(0, 'src')

from tools.legado_debug_tools import test_legado_rule, debug_book_source, format_debug_result, quick_test

# 验证书源的底层函数
def validate_book_source_json(book_source_json: str) -> str:
    """验证书源JSON的底层函数"""
    import json

    try:
        # 解析JSON
        try:
            sources = json.loads(book_source_json)
            if isinstance(sources, list):
                source = sources[0]
            else:
                source = sources
        except json.JSONDecodeError as e:
            return f"❌ JSON解析失败: {str(e)}"

        # 检查必填字段
        required_fields = ["bookSourceName", "bookSourceUrl", "searchUrl"]
        missing_fields = [f for f in required_fields if f not in source]

        if missing_fields:
            return f"❌ 缺少必填字段: {', '.join(missing_fields)}"

        # 验证规则字段
        report = []
        report.append("✅ 书源基本信息验证通过")
        report.append(f"  书源名称: {source.get('bookSourceName')}")
        report.append(f"  书源地址: {source.get('bookSourceUrl')}")

        # 检查规则字段
        rule_types = ["ruleSearch", "ruleBookInfo", "ruleToc", "ruleContent"]
        for rule_type in rule_types:
            if rule_type in source:
                rule = source[rule_type]
                if isinstance(rule, dict):
                    report.append(f"✅ {rule_type} 存在")
                else:
                    report.append(f"⚠️ {rule_type} 格式不正确，应为对象")

        return "\n".join(report)

    except Exception as e:
        return f"❌ 验证失败: {str(e)}"


def test_test_legado_rule():
    """测试规则测试功能"""
    print("=" * 60)
    print("测试 1: test_legado_rule")
    print("=" * 60)

    html = """
    <div class="book">
        <h1 class="title">斗破苍穹</h1>
        <p class="author">作者：天蚕土豆</p>
        <div class="nav">
            <a href="/chapter/1_2.html">下一页</a>
            <a href="/chapter/2.html">下一章</a>
        </div>
    </div>
    """

    # 测试1: CSS选择器@text
    print("\n测试 1.1: CSS选择器@text")
    result = test_legado_rule(html, ".title@text")
    print(result)

    # 测试2: text.文本@href
    print("\n测试 1.2: text.文本@href")
    result = test_legado_rule(html, "text.下一章@href")
    print(result)

    # 测试3: 正则替换
    print("\n测试 1.3: 正则替换")
    result = test_legado_rule(html, ".author@text##.*作者：##")
    print(result)

    # 测试4: 快速测试
    print("\n测试 1.4: 快速测试")
    result = quick_test(html, ".title@text")
    print(result)


def test_validate_legado_rules():
    """测试规则验证功能"""
    print("\n" + "=" * 60)
    print("测试 2: validate_legado_rules")
    print("=" * 60)

    book_source = [
        {
            "bookSourceName": "测试书源",
            "bookSourceUrl": "https://example.com",
            "searchUrl": "/search?q={{key}}",
            "ruleSearch": {
                "bookList": ".book-item",
                "name": ".title@text",
                "author": ".author@text",
                "bookUrl": "a@href"
            },
            "ruleBookInfo": {
                "name": "h1@text",
                "author": ".author@text"
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
    ]

    book_source_json = '{"bookSourceName": "测试书源", "bookSourceUrl": "https://example.com"}'

    print("\n测试 2.1: 验证书源JSON")
    result = validate_legado_rules(book_source_json)
    print(result)


def test_debug_legado_book_source():
    """测试书源调试功能"""
    print("\n" + "=" * 60)
    print("测试 3: debug_legado_book_source")
    print("=" * 60)

    # 创建一个简单的测试书源
    book_source = [
        {
            "bookSourceName": "测试书源",
            "bookSourceUrl": "https://www.sudugu.org",
            "searchUrl": "/i/sor.aspx?key={{key}}",
            "ruleSearch": {
                "bookList": ".result-item",
                "name": ".title@text",
                "author": ".author@text",
                "bookUrl": "a@href"
            }
        }
    ]

    book_source_json = json.dumps(book_source)

    print("\n测试 3.1: 调试搜索规则")
    print("注意: 此测试需要网络连接，如果失败是正常的")
    try:
        result = debug_book_source(book_source_json, "斗破苍穹", "search")
        formatted = format_debug_result(result)
        print(formatted)
    except Exception as e:
        print(f"⚠️ 测试失败（预期行为）: {str(e)}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Legado调试工具测试")
    print("=" * 60)

    try:
        test_test_legado_rule()
        test_validate_legado_rules()
        test_debug_legado_book_source()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import json
    main()
