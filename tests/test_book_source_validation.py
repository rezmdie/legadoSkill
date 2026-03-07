#!/usr/bin/env python3
"""
歌书网书源测试脚本
用于验证智能体生成的书源是否包含所有必需字段
"""

import json

def validate_book_source(source_json):
    """
    验证书源JSON是否包含所有必需字段
    
    Args:
        source_json: 书源JSON对象
    
    Returns:
        dict: 包含验证结果和缺失字段的字典
    """
    errors = []
    warnings = []
    
    # 检查ruleContent
    if 'ruleContent' in source_json:
        rule_content = source_json['ruleContent']
        
        # 必填字段
        if 'content' not in rule_content:
            errors.append("ruleContent缺少content字段")
        
        # 检查是否有分页字段
        # 查找content字段中的分页提示
        content_rule = rule_content.get('content', '')
        if '下一页' in content_rule or '下一章' in content_rule or '继续阅读' in content_rule:
            if 'nextContentUrl' not in rule_content:
                errors.append("ruleContent包含分页提示，但缺少nextContentUrl字段")
    
    # 检查ruleToc
    if 'ruleToc' in source_json:
        rule_toc = source_json['ruleToc']
        
        # 必填字段
        required_toc_fields = ['chapterList', 'chapterName', 'chapterUrl']
        for field in required_toc_fields:
            if field not in rule_toc:
                errors.append(f"ruleToc缺少{field}字段")
    
    # 检查ruleSearch
    if 'ruleSearch' in source_json:
        rule_search = source_json['ruleSearch']
        
        # 必填字段
        required_search_fields = ['bookList', 'name', 'bookUrl']
        for field in required_search_fields:
            if field not in rule_search:
                errors.append(f"ruleSearch缺少{field}字段")
    
    # 检查正则表达式完整性
    if 'ruleContent' in source_json:
        content_rule = source_json['ruleContent'].get('content', '')
        # 检查是否以##结尾
        if not content_rule.endswith('##'):
            warnings.append("ruleContent.content正则表达式未以##结尾")
        
        # 检查是否有多个清理规则
        if content_rule.count('|') > 0:
            # 检查每个规则之间是否正确分隔
            parts = content_rule.split('|')
            for i, part in enumerate(parts):
                if i > 0 and not part.endswith('##'):
                    warnings.append(f"ruleContent.content正则表达式第{i+1}个规则未以##结尾")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def test_standard_answer():
    """测试标准答案"""
    print("=" * 80)
    print("测试标准答案")
    print("=" * 80)
    
    standard_answer = {
      "bookSourceName": "歌书网",
      "bookSourceType": 0,
      "bookSourceUrl": "",
      "customButton": False,
      "customOrder": 0,
      "enabled": True,
      "enabledCookieJar": True,
      "enabledExplore": True,
      "eventListener": False,
      "lastUpdateTime": 1771405564950,
      "respondTime": 180000,
      "ruleBookInfo": {
        "author": ".author@text##作者：##",
        "coverUrl": ".synopsisArea_detail img@src",
        "intro": ".review@text",
        "kind": ".sort@text##类别：##",
        "lastChapter": ".directoryArea p:first-child a@text",
        "name": ".synopsisArea_detail img@alt"
      },
      "ruleContent": {
        "content": "#chaptercontent@html##<div id=\"content_tip\">[\\s\\S]*?</div>|本章节未完，点击下一页继续阅读|歌书网.*com##",
        "nextContentUrl": "text.下一@href"
      },
      "ruleExplore": {},
      "ruleSearch": {
        "author": ".author.0@text##.*作者：(.*)##$1",
        "bookList": ".hot_sale",
        "bookUrl": "a@href",
        "kind": ".author.0@text&&.author.1@text##\\|.*：##,",
        "lastChapter": ".author:last-child@text##.*更新：##",
        "name": ".title@text"
      },
      "ruleToc": {
        "chapterList": ".directoryArea p",
        "chapterName": "a@text",
        "chapterUrl": "a@href",
        "nextTocUrl": "option@value"
      },
      "searchUrl": "/s.php,{\"method\":\"POST\",\"body\":\"keyword={{key}}&t=1\"}",
      "weight": 0
    }
    
    result = validate_book_source(standard_answer)
    
    if result['valid']:
        print("✅ 标准答案验证通过")
    else:
        print("❌ 标准答案验证失败")
        print(f"错误: {result['errors']}")
    
    if result['warnings']:
        print(f"⚠️ 警告: {result['warnings']}")
    
    print()
    return result

def test_wrong_answer():
    """测试错误答案"""
    print("=" * 80)
    print("测试错误答案")
    print("=" * 80)
    
    wrong_answer = {
      "bookSourceName": "歌书网",
      "bookSourceType": 0,
      "bookSourceUrl": "",
      "customButton": False,
      "customOrder": 0,
      "enabled": True,
      "enabledCookieJar": True,
      "enabledExplore": True,
      "eventListener": False,
      "lastUpdateTime": 1771405491509,
      "respondTime": 180000,
      "ruleBookInfo": {
        "author": ".author@text##作者：##",
        "coverUrl": ".synopsisArea_detail img@src",
        "intro": ".review@text",
        "kind": ".sort@text##类别：##",
        "lastChapter": ".directoryArea p:first-child a@text",
        "name": ".synopsisArea_detail img@alt"
      },
      "ruleContent": {
        "content": "#chaptercontent@html##<div id=\"content_tip\">[\\s\\S]*?</div>|本章节未完，点击下一页继续阅读##"
      },
      "ruleExplore": {},
      "ruleSearch": {
        "author": ".author.0@text##.*作者：(.*)##$1",
        "bookList": ".hot_sale",
        "bookUrl": "a@href",
        "kind": ".author.0@text&&.author.1@text##\\|.*：##,",
        "lastChapter": ".author:last-child@text##.*更新：##",
        "name": ".title@text"
      },
      "ruleToc": {
        "chapterList": ".directoryArea p",
        "chapterName": "a@text",
        "chapterUrl": "a@href"
      },
      "searchUrl": "/s.php,{\"method\":\"POST\",\"body\":\"keyword={{key}}&t=1\"}",
      "weight": 0
    }
    
    result = validate_book_source(wrong_answer)
    
    if result['valid']:
        print("✅ 错误答案验证通过（不应该通过）")
    else:
        print("❌ 错误答案验证失败（符合预期）")
        print(f"错误: {result['errors']}")
    
    if result['warnings']:
        print(f"⚠️ 警告: {result['warnings']}")
    
    print()
    return result

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("歌书网书源验证测试")
    print("=" * 80 + "\n")
    
    # 测试标准答案
    std_result = test_standard_answer()
    
    # 测试错误答案
    wrong_result = test_wrong_answer()
    
    # 总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"标准答案: {'✅ 通过' if std_result['valid'] else '❌ 失败'}")
    print(f"错误答案: {'❌ 未检测到错误（有问题）' if wrong_result['valid'] else '✅ 正确检测到错误'}")
    print()
    
    # 退出码
    if std_result['valid'] and not wrong_result['valid']:
        print("所有测试通过！")
        exit(0)
    else:
        print("测试失败！")
        exit(1)
