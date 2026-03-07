#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复src/tools目录下所有Python文件中的emoji编码问题
将emoji替换为纯文本，避免Windows GBK环境下的编码错误
"""

import os
import re
from pathlib import Path

# emoji替换映射
EMOJI_REPLACEMENTS = {
    '🌐': '[WEB]',
    '📋': '[INFO]',
    '💻': '[CODE]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '🔧': '[CONFIG]',
    '🎯': '[TARGET]',
    '💡': '[TIP]',
    '🧪': '[TEST]',
    '📄': '[DOC]',
    '🔬': '[ANALYZE]',
    '💾': '[SAVE]',
    '🔒': '[SECURE]',
    '🚀': '[START]',
    '📊': '[STATS]',
    '🔍': '[SEARCH]',
    '📝': '[NOTE]',
    '🎨': '[STYLE]',
    '⏰': '[TIME]',
    '📦': '[PACKAGE]',
    '🔗': '[LINK]',
    '📈': '[CHART]',
    '🌟': '[STAR]',
    '💬': '[COMMENT]',
    '🎉': '[SUCCESS]',
    '🔥': '[HOT]',
    '⭐': '[STAR]',
    '🎁': '[GIFT]',
}

def fix_emoji_in_file(file_path):
    """修复单个文件中的emoji"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换所有emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    tools_dir = Path('src/tools')
    
    if not tools_dir.exists():
        print(f"Error: {tools_dir} does not exist")
        return
    
    print("Starting emoji fix process...")
    print(f"Scanning directory: {tools_dir}")
    print("-" * 60)
    
    fixed_count = 0
    total_count = 0
    
    # 遍历所有Python文件
    for py_file in tools_dir.glob('*.py'):
        total_count += 1
        print(f"Processing: {py_file.name}...", end=' ')
        
        if fix_emoji_in_file(py_file):
            print("[FIXED]")
            fixed_count += 1
        else:
            print("[SKIP]")
    
    print("-" * 60)
    print(f"Total files processed: {total_count}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files skipped: {total_count - fixed_count}")
    print("\nEmoji fix process completed!")

if __name__ == '__main__':
    main()
