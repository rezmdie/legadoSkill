#!/usr/bin/env python3
"""
书源学习工具

支持多种输入方式学习书源：
1. 原始ID：从源仓库下载并学习
2. 链接：从URL下载JSON文件并学习
3. JSON字符串：直接学习提供的JSON
4. JSON文件：从文件读取并学习

智能判断逻辑：
- 如果JSON包含书源特征字段，则学习
- 否则当作用户要处理的数据返回
"""

import os
import sys
import json
import argparse
import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from reference_learning_module import ReferenceLearningModule
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/learning.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 源仓库配置
BASE_URL = "https://www.yck2026.top"


class BookSourceLearner:
    """书源学习工具"""
    
    def __init__(self):
        """初始化"""
        self.learning_module = ReferenceLearningModule()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_book_source(self, data: Any) -> Tuple[bool, str]:
        """
        智能判断是否是书源
        
        Args:
            data: 要判断的数据
        
        Returns:
            (是否是书源, 原因说明)
        """
        if not data:
            return False, "数据为空"
        
        # 如果是数组，检查第一个元素
        if isinstance(data, list):
            if len(data) == 0:
                return False, "空数组"
            
            # 检查是否是书源数组（所有元素都是书源）
            first_element = data[0]
            if isinstance(first_element, dict):
                is_source, reason = self._check_book_source_dict(first_element)
                if is_source:
                    # 检查其他元素
                    all_sources = all(
                        self._check_book_source_dict(item)[0] 
                        for item in data 
                        if isinstance(item, dict)
                    )
                    if all_sources:
                        return True, "书源数组"
                    else:
                        return False, "混合数组（包含非书源）"
        
        # 如果是字典，检查是否是单个书源
        elif isinstance(data, dict):
            return self._check_book_source_dict(data)
        
        return False, "未知数据类型"
    
    def _check_book_source_dict(self, data: Dict) -> Tuple[bool, str]:
        """
        检查字典是否是书源
        
        Args:
            data: 字典数据
        
        Returns:
            (是否是书源, 原因说明)
        """
        # 必备字段检查（至少包含一个）
        required_fields = [
            'bookSourceName',    # 书源名称
            'bookSourceUrl',     # 书源地址
            'ruleSearch',        # 搜索规则
            'ruleBookInfo',      # 详情规则
            'ruleToc',           # 目录规则
            'ruleContent',       # 正文规则
        ]
        
        has_required = any(field in data for field in required_fields)
        
        if has_required:
            # 检查规则字段是否有效
            rule_fields = ['ruleSearch', 'ruleBookInfo', 'ruleToc', 'ruleContent']
            has_rules = any(
                field in data and data[field] and isinstance(data[field], dict)
                for field in rule_fields
            )
            
            if has_rules:
                return True, "包含书源规则字段"
            else:
                return False, "缺少有效规则字段"
        
        return False, "不包含书源特征字段"
    
    def learn_from_id(self, source_id: str, category: str = "书源") -> Tuple[bool, str]:
        """
        从原始ID学习书源
        
        Args:
            source_id: 书源ID
            category: 分类
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 构造下载URL
            download_url = f"{BASE_URL}/yuedu/shuyuan/json/id/{source_id}.json"
            
            logger.info(f"从ID下载书源: {source_id}")
            logger.info(f"下载URL: {download_url}")
            
            # 下载JSON
            response = self.session.get(download_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # 判断是否是书源
            is_source, reason = self.is_book_source(data)
            if not is_source:
                return False, f"下载的数据不是书源: {reason}"
            
            # 构造书源信息
            source_info = {
                'source_id': source_id,
                'link': f"/yuedu/shuyuan/content/id/{source_id}.html",
                'pub_time': '未知',
                'description': f'从ID {source_id} 下载'
            }
            
            # 学习书源
            success = self.learning_module.learn_book_source(data, source_info, category)
            
            if success:
                return True, f"成功学习书源ID: {source_id}"
            else:
                return False, f"学习失败: {source_id}"
            
        except Exception as e:
            logger.error(f"从ID学习失败: {e}")
            return False, f"从ID学习失败: {str(e)}"
    
    def learn_from_url(self, url: str, category: str = "书源") -> Tuple[bool, str]:
        """
        从URL学习书源
        
        Args:
            url: 书源JSON文件的URL
            category: 分类
        
        Returns:
            (是否成功, 消息)
        """
        try:
            logger.info(f"从URL下载书源: {url}")
            
            # 下载JSON
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # 判断是否是书源
            is_source, reason = self.is_book_source(data)
            if not is_source:
                return False, f"下载的数据不是书源: {reason}"
            
            # 构造书源信息
            source_info = {
                'source_id': self._extract_id_from_url(url),
                'link': url,
                'pub_time': '未知',
                'description': f'从URL下载'
            }
            
            # 学习书源
            success = self.learning_module.learn_book_source(data, source_info, category)
            
            if success:
                return True, f"成功学习书源: {url}"
            else:
                return False, f"学习失败: {url}"
            
        except Exception as e:
            logger.error(f"从URL学习失败: {e}")
            return False, f"从URL学习失败: {str(e)}"
    
    def learn_from_json(self, json_data: Any, category: str = "书源", 
                       source_id: str = None) -> Tuple[bool, str]:
        """
        从JSON数据学习书源
        
        Args:
            json_data: JSON数据（可以是字典、列表、JSON字符串）
            category: 分类
            source_id: 原始ID（可选）
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 如果是字符串，尝试解析
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # 判断是否是书源
            is_source, reason = self.is_book_source(data)
            if not is_source:
                return False, f"提供的数据不是书源: {reason}\n当作用户要处理的数据返回"
            
            # 构造书源信息
            source_info = {
                'source_id': source_id or 'user_provided',
                'link': '',
                'pub_time': str(datetime.now()),
                'description': '用户提供'
            }
            
            # 学习书源
            success = self.learning_module.learn_book_source(data, source_info, category)
            
            if success:
                return True, "成功学习用户提供的书源"
            else:
                return False, "学习用户提供的书源失败"
            
        except json.JSONDecodeError as e:
            return False, f"JSON解析失败: {str(e)}"
        except Exception as e:
            logger.error(f"从JSON学习失败: {e}")
            return False, f"从JSON学习失败: {str(e)}"
    
    def learn_from_file(self, file_path: str, category: str = "书源", delete_original: bool = True) -> Tuple[bool, str]:
        """
        从文件学习书源

        Args:
            file_path: JSON文件路径
            category: 分类
            delete_original: 是否删除原始文件（默认True）

        Returns:
            (是否成功, 消息)
        """
        try:
            logger.info(f"从文件学习书源: {file_path}")

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 判断是否是书源
            is_source, reason = self.is_book_source(data)
            if not is_source:
                return False, f"文件内容不是书源: {reason}\n当作用户要处理的数据返回"

            # 提取ID（从文件名）
            source_id = self._extract_id_from_filename(file_path)

            # 构造书源信息
            source_info = {
                'source_id': source_id,
                'link': file_path,
                'pub_time': str(datetime.now()),
                'description': f'从文件读取: {os.path.basename(file_path)}',
                'original_file': file_path if delete_original else None
            }

            # 学习书源
            success = self.learning_module.learn_book_source(data, source_info, category)

            if success:
                message = f"成功学习文件: {file_path}"
                if delete_original:
                    # 注意：文件删除会在mark_as_learned中自动执行
                    message += "（原始文件已删除）"
                return True, message
            else:
                return False, f"学习文件失败: {file_path}"

        except FileNotFoundError:
            return False, f"文件不存在: {file_path}"
        except json.JSONDecodeError as e:
            return False, f"文件JSON解析失败: {str(e)}"
        except Exception as e:
            logger.error(f"从文件学习失败: {e}")
            return False, f"从文件学习失败: {str(e)}"
    
    def _extract_id_from_url(self, url: str) -> str:
        """从URL中提取ID"""
        import re
        # 尝试匹配ID模式
        patterns = [
            r'/id/(\d+)\.json',
            r'id=(\d+)',
            r'/(\d+)\.json',
            r'(\d{4,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def _extract_id_from_filename(self, file_path: str) -> str:
        """从文件名中提取ID"""
        import re
        filename = os.path.basename(file_path)
        
        # 尝试匹配ID模式
        patterns = [
            r'^(\d{4,})_',
            r'_(\d{4,})_',
            r'id(\d{4,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def process_data(self, data: Any) -> Tuple[bool, str, Any]:
        """
        处理用户数据（如果不是书源）
        
        Args:
            data: 用户数据
        
        Returns:
            (已处理, 消息, 原始数据)
        """
        is_source, reason = self.is_book_source(data)
        
        if is_source:
            return False, "检测到书源，应该使用学习功能而不是数据处理", data
        
        return True, f"已识别为用户要处理的数据: {reason}", data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='书源学习工具')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='学习方式')
    
    # 从ID学习
    id_parser = subparsers.add_parser('id', help='从原始ID学习书源')
    id_parser.add_argument('source_id', type=str, help='书源ID')
    id_parser.add_argument('--category', type=str, default='书源', help='分类（默认：书源）')
    
    # 从URL学习
    url_parser = subparsers.add_parser('url', help='从URL学习书源')
    url_parser.add_argument('url', type=str, help='书源JSON文件的URL')
    url_parser.add_argument('--category', type=str, default='书源', help='分类（默认：书源）')
    
    # 从JSON字符串学习
    json_parser = subparsers.add_parser('json', help='从JSON字符串学习书源')
    json_parser.add_argument('json_data', type=str, help='JSON字符串或文件路径')
    json_parser.add_argument('--category', type=str, default='书源', help='分类（默认：书源）')
    json_parser.add_argument('--source-id', type=str, help='原始ID（可选）')
    json_parser.add_argument('--file', action='store_true', help='将json_data作为文件路径处理')
    
    # 检查数据类型
    check_parser = subparsers.add_parser('check', help='检查数据是否是书源')
    check_parser.add_argument('data', type=str, help='JSON字符串或文件路径')
    check_parser.add_argument('--file', action='store_true', help='将data作为文件路径处理')
    
    args = parser.parse_args()
    
    # 创建学习器
    learner = BookSourceLearner()
    
    # 根据命令执行
    if args.command == 'id':
        success, message = learner.learn_from_id(args.source_id, args.category)
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
    
    elif args.command == 'url':
        success, message = learner.learn_from_url(args.url, args.category)
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
    
    elif args.command == 'json':
        if args.file:
            # 从文件学习
            success, message = learner.learn_from_file(args.json_data, args.category)
        else:
            # 从JSON字符串学习
            success, message = learner.learn_from_json(
                args.json_data, 
                args.category, 
                args.source_id
            )
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
    
    elif args.command == 'check':
        # 检查数据类型
        try:
            if args.file:
                with open(args.data, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = json.loads(args.data)
            
            is_source, reason = learner.is_book_source(data)
            
            if is_source:
                print(f"✓ 检测到书源: {reason}")
                print("   可以使用学习功能学习此书源")
                sys.exit(0)
            else:
                print(f"✗ 不是书源: {reason}")
                print("   当作用户要处理的数据")
                sys.exit(1)
        
        except Exception as e:
            print(f"✗ 检查失败: {str(e)}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
