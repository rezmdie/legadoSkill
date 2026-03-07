#!/usr/bin/env python3
"""
分析真实书源知识库，提取关键模式
"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set

def extract_book_source_patterns(md_file: Path) -> Dict:
    """从md文件中提取书源模式"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    patterns = {
        'name': '',
        'url': '',
        'group': '',
        'search_rules': {},
        'bookinfo_rules': {},
        'toc_rules': {},
        'content_rules': {},
        'selector_patterns': set(),
        'extraction_types': set(),
        'special_features': set()
    }
    
    # 提取基本信息
    name_match = re.search(r'\*\*书源名称\*\*[:：]\s*(.+)', content)
    if name_match:
        patterns['name'] = name_match.group(1).strip()
    
    url_match = re.search(r'\*\*书源地址\*\*[:：]\s*(.+)', content)
    if url_match:
        patterns['url'] = url_match.group(1).strip()
    
    group_match = re.search(r'\*\*书源分组\*\*[:：]\s*(.+)', content)
    if group_match:
        patterns['group'] = group_match.group(1).strip()
    
    # 提取规则
    rules = {
        'search': r'### 搜索规则\s*```json\s*(\{.*?\})',
        'bookinfo': r'### 详情规则\s*```json\s*(\{.*?\})',
        'toc': r'### 目录规则\s*```json\s*(\{.*?\})',
        'content': r'### 正文规则\s*```json\s*(\{.*?\})'
    }
    
    for rule_type, pattern in rules.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                rule_json = json.loads(match.group(1))
                patterns[f'{rule_type}_rules'] = rule_json
                
                # 提取选择器模式
                for value in rule_json.values():
                    if isinstance(value, str):
                        # 提取CSS选择器
                        selector_matches = re.findall(r'([a-zA-Z][a-zA-Z0-9_\-\.\#\>\[\]\:\s,]+)@[a-z]+', value)
                        patterns['selector_patterns'].update(selector_matches)
                        
                        # 提取提取类型
                        extraction_matches = re.findall(r'@([a-z]+)', value)
                        patterns['extraction_types'].update(extraction_matches)
                        
                        # 检查特殊功能
                        if '<js>' in value:
                            patterns['special_features'].add('JavaScript处理')
                        if '##' in value:
                            patterns['special_features'].add('正则表达式')
                        if '$.' in value:
                            patterns['special_features'].add('JSONPath')
                        if 'xpath:' in value or '//' in value:
                            patterns['special_features'].add('XPath')
            except json.JSONDecodeError:
                pass
    
    patterns['selector_patterns'] = list(patterns['selector_patterns'])
    patterns['extraction_types'] = list(patterns['extraction_types'])
    patterns['special_features'] = list(patterns['special_features'])
    
    return patterns

def analyze_all_sources(knowledge_dir: Path) -> Dict:
    """分析所有书源"""
    all_patterns = {
        'total_sources': 0,
        'groups': {},
        'common_selectors': {},
        'common_extractions': {},
        'special_features': {},
        'example_sources': []
    }
    
    for md_file in sorted(knowledge_dir.glob('*.md')):
        patterns = extract_book_source_patterns(md_file)
        
        if not patterns['name']:
            continue
        
        all_patterns['total_sources'] += 1
        
        # 统计分组
        group = patterns['group'] or '未分类'
        all_patterns['groups'][group] = all_patterns['groups'].get(group, 0) + 1
        
        # 统计选择器
        for selector in patterns['selector_patterns']:
            all_patterns['common_selectors'][selector] = all_patterns['common_selectors'].get(selector, 0) + 1
        
        # 统计提取类型
        for ext in patterns['extraction_types']:
            all_patterns['common_extractions'][ext] = all_patterns['common_extractions'].get(ext, 0) + 1
        
        # 统计特殊功能
        for feature in patterns['special_features']:
            all_patterns['special_features'][feature] = all_patterns['special_features'].get(feature, 0) + 1
        
        # 保存示例
        if len(all_patterns['example_sources']) < 10:
            all_patterns['example_sources'].append({
                'name': patterns['name'],
                'url': patterns['url'],
                'group': patterns['group']
            })
    
    return all_patterns

def main():
    knowledge_dir = Path('/workspace/projects/assets/knowledge_base/book_sources')
    
    print(f"正在分析 {len(list(knowledge_dir.glob('*.md')))} 个书源文件...")
    all_patterns = analyze_all_sources(knowledge_dir)
    
    print(f"\n{'='*60}")
    print(f"分析结果")
    print(f"{'='*60}")
    print(f"\n总书源数: {all_patterns['total_sources']}")
    
    print(f"\n{'='*60}")
    print(f"书源分组统计")
    print(f"{'='*60}")
    for group, count in sorted(all_patterns['groups'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {group}: {count}")
    
    print(f"\n{'='*60}")
    print(f"最常用的CSS选择器 (Top 20)")
    print(f"{'='*60}")
    for selector, count in sorted(all_patterns['common_selectors'].items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {selector}: {count}")
    
    print(f"\n{'='*60}")
    print(f"最常用的提取类型")
    print(f"{'='*60}")
    for ext, count in sorted(all_patterns['common_extractions'].items(), key=lambda x: x[1], reverse=True):
        print(f"  @{ext}: {count}")
    
    print(f"\n{'='*60}")
    print(f"特殊功能使用统计")
    print(f"{'='*60}")
    for feature, count in sorted(all_patterns['special_features'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {count}")
    
    print(f"\n{'='*60}")
    print(f"示例书源")
    print(f"{'='*60}")
    for source in all_patterns['example_sources']:
        print(f"  {source['name']} ({source['group']}) - {source['url']}")
    
    # 保存结果
    output_file = Path('/workspace/projects/assets/真实书源分析结果.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_patterns, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存到: {output_file}")

if __name__ == '__main__':
    main()
