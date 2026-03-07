"""
书源JSON严格模式验证器
用于验证书源JSON是否符合严格模式的要求
"""

import json
from typing import Dict, List, Any, Tuple


class BookSourceValidator:
    """书源JSON严格模式验证器"""

    # 必填字段列表
    REQUIRED_FIELDS = {
        "bookSourceUrl": "书源地址",
        "bookSourceName": "书源名称",
        "searchUrl": "搜索URL",
    }

    # 必填规则字段
    REQUIRED_RULE_FIELDS = {
        "ruleSearch": {
            "bookList": "书籍列表选择器",
            "name": "书名提取规则",
            "bookUrl": "书籍URL提取规则",
        },
        "ruleToc": {
            "chapterList": "章节列表选择器",
            "chapterName": "章节名提取规则",
            "chapterUrl": "章节URL提取规则",
        },
        "ruleContent": {
            "content": "正文内容提取规则",
        }
    }

    # 可选规则字段
    OPTIONAL_RULE_FIELDS = {
        "ruleSearch": [
            "author", "kind", "wordCount", "lastChapter", "intro", "coverUrl"
        ],
        "ruleBookInfo": [
            "name", "author", "kind", "wordCount", "lastChapter",
            "intro", "coverUrl", "tocUrl"
        ],
        "ruleToc": [
            "preUpdateJs", "updateJs", "nextTocUrl"
        ],
        "ruleContent": [
            "nextContentUrl", "webJs", "sourceRegex", "replaceRegex"
        ]
    }

    def __init__(self):
        """初始化验证器"""
        self.errors = []
        self.warnings = []

    def validate(self, json_str: str) -> Tuple[bool, List[str], List[str]]:
        """
        验证书源JSON

        Args:
            json_str: JSON字符串

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        # 1. 检查JSON格式
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ JSON格式错误: {str(e)}")
            return False, self.errors, self.warnings

        # 2. 检查数组格式
        if not isinstance(data, list):
            self.errors.append("❌ 格式错误: 最外层必须是数组格式 [...]")
            return False, self.errors, self.warnings

        # 3. 检查数组是否为空
        if len(data) == 0:
            self.errors.append("❌ 数组为空: 必须包含至少一个书源对象")
            return False, self.errors, self.warnings

        # 4. 验证书源对象
        for idx, source in enumerate(data):
            self._validate_source(source, idx)

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_source(self, source: Dict[str, Any], index: int):
        """
        验证书源对象

        Args:
            source: 书源对象
            index: 索引
        """
        prefix = f"书源[{index}]"

        # 检查是否为对象
        if not isinstance(source, dict):
            self.errors.append(f"{prefix} 不是对象类型")
            return

        # 检查必填字段
        for field, desc in self.REQUIRED_FIELDS.items():
            if field not in source:
                self.errors.append(f"{prefix} 缺少必填字段: {field} ({desc})")
            elif not source[field]:
                self.errors.append(f"{prefix} 必填字段为空: {field} ({desc})")

        # 检查规则字段
        for rule_type, required_fields in self.REQUIRED_RULE_FIELDS.items():
            if rule_type not in source:
                self.errors.append(f"{prefix} 缺少规则字段: {rule_type}")
                continue

            rule = source[rule_type]
            if not isinstance(rule, dict):
                self.errors.append(f"{prefix}.{rule_type} 不是对象类型")
                continue

            # 检查必填规则字段
            for field, desc in required_fields.items():
                if field not in rule:
                    self.errors.append(f"{prefix}.{rule_type} 缺少必填字段: {field} ({desc})")
                elif not rule[field]:
                    self.errors.append(f"{prefix}.{rule_type} 必填字段为空: {field} ({desc})")

            # 检查未知字段（可选）
            for field in rule.keys():
                if field not in required_fields and field not in self.OPTIONAL_RULE_FIELDS.get(rule_type, []):
                    self.warnings.append(f"{prefix}.{rule_type} 包含未知字段: {field}")

        # 检查bookSourceType
        if "bookSourceType" in source:
            book_source_type = source["bookSourceType"]
            if not isinstance(book_source_type, int) or book_source_type not in [0, 1, 2, 3, 4]:
                self.warnings.append(f"{prefix} bookSourceType值异常: {book_source_type} (应为0-4的整数)")

        # 检查searchUrl格式
        if "searchUrl" in source:
            search_url = source["searchUrl"]
            if "," in search_url and not search_url.startswith("<js>"):
                # POST请求配置
                try:
                    parts = search_url.split(",")
                    if len(parts) == 2:
                        json_part = parts[1]
                        json.loads(json_part)  # 验证JSON格式
                except json.JSONDecodeError:
                    self.errors.append(f"{prefix} searchUrl的POST配置JSON格式错误: {search_url}")

    def print_report(self):
        """打印验证报告"""
        print("=" * 60)
        print("书源JSON严格模式验证报告")
        print("=" * 60)

        if len(self.errors) == 0:
            print("✅ 验证通过！书源JSON符合严格模式要求。")
        else:
            print(f"❌ 验证失败！发现 {len(self.errors)} 个错误：")
            for error in self.errors:
                print(f"  {error}")

        if len(self.warnings) > 0:
            print(f"\n⚠️  警告（共 {len(self.warnings)} 个）：")
            for warning in self.warnings:
                print(f"  {warning}")

        print("=" * 60)


def validate_book_source(json_str: str) -> Tuple[bool, List[str], List[str]]:
    """
    验证书源JSON（便捷函数）

    Args:
        json_str: JSON字符串

    Returns:
        (是否通过, 错误列表, 警告列表)
    """
    validator = BookSourceValidator()
    return validator.validate(json_str)


if __name__ == "__main__":
    # 测试用例
    print("测试用例1: 正确的书源JSON")
    test_json1 = """
    [
      {
        "bookSourceName": "测试书源",
        "bookSourceUrl": "https://www.example.com",
        "bookSourceType": 0,
        "searchUrl": "/search?q={{key}}",
        "ruleSearch": {
          "bookList": ".book-item",
          "name": ".title@text",
          "author": ".author@text",
          "coverUrl": "img@src",
          "bookUrl": "a@href"
        },
        "ruleToc": {
          "chapterList": "#chapter-list li",
          "chapterName": "a@text",
          "chapterUrl": "a@href"
        },
        "ruleContent": {
          "content": "#content@html"
        }
      }
    ]
    """
    validator = BookSourceValidator()
    passed, errors, warnings = validator.validate(test_json1)
    validator.print_report()

    print("\n测试用例2: 缺少必填字段的书源JSON")
    test_json2 = """
    [
      {
        "bookSourceName": "测试书源",
        "bookSourceUrl": "https://www.example.com"
      }
    ]
    """
    validator = BookSourceValidator()
    passed, errors, warnings = validator.validate(test_json2)
    validator.print_report()

    print("\n测试用例3: 格式错误的书源JSON")
    test_json3 = """
    {
      "bookSourceName": "测试书源",
      "bookSourceUrl": "https://www.example.com"
    }
    """
    validator = BookSourceValidator()
    passed, errors, warnings = validator.validate(test_json3)
    validator.print_report()
