#!/usr/bin/env python3
"""
参考学习模块爬取脚本

功能：
1. 定时运行（每天晨运行）
2. 检测更新并运行
3. 从原仓库网站采集并学习书源
4. 智能更新检测
"""

import os
import sys
import json
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/learning_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
BASE_URL = "https://www.yck2026.top"
UPDATE_CHECK_FILE = "scripts/learning_update_check.json"
LEARNING_LOG_FILE = "scripts/learning_log.json"

# 分类配置
CATEGORIES = {
    "书源": {
        "url": "/yuedu/shuyuan/index.html",
        "subdir": "book_sources"
    },
    "书源合集": {
        "url": "/yuedu/shuyuan/heji/index.html",
        "subdir": "book_source_collections"
    },
    "订阅源": {
        "url": "/yuedu/rssyuan/index.html",
        "subdir": "rss_sources"
    },
    "订阅源合集": {
        "url": "/yuedu/rssyuan/heji/index.html",
        "subdir": "rss_source_collections"
    }
}


class LearningCrawler:
    """参考学习模块爬虫"""
    
    def __init__(self):
        """初始化"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 加载更新检测数据
        self.update_check_data = self._load_update_check()
        
        # 加载学习日志
        self.learning_log = self._load_learning_log()
    
    def _load_update_check(self) -> Dict:
        """加载更新检测数据"""
        try:
            if os.path.exists(UPDATE_CHECK_FILE):
                with open(UPDATE_CHECK_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载更新检测数据失败: {e}")
        
        return {
            'last_check': {},
            'last_check_time': None
        }
    
    def _save_update_check(self):
        """保存更新检测数据"""
        try:
            os.makedirs(os.path.dirname(UPDATE_CHECK_FILE), exist_ok=True)
            with open(UPDATE_CHECK_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.update_check_data, f, indent=2, ensure_ascii=False)
            logger.info("更新检测数据已保存")
        except Exception as e:
            logger.error(f"保存更新检测数据失败: {e}")
    
    def _load_learning_log(self) -> Dict:
        """加载学习日志"""
        try:
            if os.path.exists(LEARNING_LOG_FILE):
                with open(LEARNING_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载学习日志失败: {e}")
        
        return {
            'learning_history': [],
            'statistics': {
                'total_learned': 0,
                'success_count': 0,
                'fail_count': 0
            }
        }
    
    def _save_learning_log(self):
        """保存学习日志"""
        try:
            with open(LEARNING_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.learning_log, f, indent=2, ensure_ascii=False)
            logger.info("学习日志已保存")
        except Exception as e:
            logger.error(f"保存学习日志失败: {e}")
    
    def _log_learning(self, source_id: str, title: str, success: bool, message: str):
        """记录学习日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_id': source_id,
            'title': title,
            'success': success,
            'message': message
        }
        
        self.learning_log['learning_history'].append(log_entry)
        
        # 更新统计
        self.learning_log['statistics']['total_learned'] += 1
        if success:
            self.learning_log['statistics']['success_count'] += 1
        else:
            self.learning_log['statistics']['fail_count'] += 1
        
        self._save_learning_log()
    
    def _get_page(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None
    
    def _parse_source_list(self, html: str) -> List[Dict]:
        """解析书源列表"""
        soup = BeautifulSoup(html, 'html.parser')
        sources = []
        
        # 查找所有链接
        for a_tag in soup.find_all('a', href=True):
            try:
                href = a_tag['href']
                title = a_tag.get_text(strip=True)
                
                if not title or not href:
                    continue
                
                # 提取描述文本
                info_text = ""
                parent = a_tag.parent
                if parent:
                    info_text = parent.get_text(strip=True)
                    info_text = info_text.replace(title, '', 1).strip()
                
                # 提取原始ID
                import re
                source_id = None
                pattern = r'/yuedu/(\w+)/content/id/(\d+)\.html'
                match = re.search(pattern, href)
                if match:
                    source_id = match.group(2)
                
                # 提取JSON URL
                json_url = self._extract_json_url(href)
                
                if not json_url:
                    continue
                
                sources.append({
                    'title': title,
                    'link': href,
                    'pub_time': info_text,
                    'source_id': source_id,
                    'json_url': json_url,
                    'hash': self._compute_hash(title + href)
                })
                
            except Exception as e:
                logger.error(f"解析书源失败: {e}")
                continue
        
        logger.info(f"成功解析 {len(sources)} 个书源")
        return sources
    
    def _extract_json_url(self, link: str) -> Optional[str]:
        """从链接中提取JSON URL"""
        if not link:
            return None
        
        try:
            import re
            pattern = r'/yuedu/(\w+)/content/id/(\d+)\.html'
            match = re.search(pattern, link)
            
            if match:
                source_type = match.group(1)
                source_id = match.group(2)
                json_url = f"/yuedu/{source_type}/json/id/{source_id}.json"
                return urljoin(BASE_URL, json_url)
            
            return None
            
        except Exception as e:
            logger.error(f"提取JSON URL失败: {e}")
            return None
    
    def _compute_hash(self, content: str) -> str:
        """计算内容的哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _download_source(self, json_url: str) -> Optional[Dict]:
        """下载书源JSON文件"""
        if not json_url:
            return None
        
        try:
            response = self.session.get(json_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"下载书源失败 {json_url}: {e}")
            return None
    
    def _is_book_source(self, data: Any) -> bool:
        """判断是否是书源"""
        if not data:
            return False
        
        if isinstance(data, list) and len(data) > 0:
            first_element = data[0]
            if isinstance(first_element, dict):
                return self._check_book_source_dict(first_element)
        elif isinstance(data, dict):
            return self._check_book_source_dict(data)
        
        return False
    
    def _check_book_source_dict(self, data: Dict) -> bool:
        """检查字典是否是书源"""
        required_fields = [
            'bookSourceName', 'bookSourceUrl', 'ruleSearch', 
            'ruleBookInfo', 'ruleToc', 'ruleContent'
        ]
        
        has_required = any(field in data for field in required_fields)
        
        if has_required:
            rule_fields = ['ruleSearch', 'ruleBookInfo', 'ruleToc', 'ruleContent']
            has_rules = any(
                field in data and data[field] and isinstance(data[field], dict)
                for field in rule_fields
            )
            return has_rules
        
        return False
    
    def _check_updates(self, category: str, sources: List[Dict]) -> Tuple[int, List[Dict]]:
        """检查更新"""
        if 'last_check' not in self.update_check_data:
            self.update_check_data['last_check'] = {}
        
        last_check = self.update_check_data['last_check'].get(category, {})
        new_sources = []
        
        for source in sources:
            source_hash = source['hash']
            
            if source_hash not in last_check:
                new_sources.append(source)
                logger.info(f"发现新书源: {source['title']} (ID: {source['source_id']})")
        
        if new_sources:
            for source in new_sources:
                if category not in self.update_check_data['last_check']:
                    self.update_check_data['last_check'][category] = {}
                self.update_check_data['last_check'][category][source['hash']] = {
                    'title': source['title'],
                    'link': source['link'],
                    'source_id': source['source_id'],
                    'first_seen': datetime.now().isoformat()
                }
            self.update_check_data['last_check_time'] = datetime.now().isoformat()
            self._save_update_check()
        
        return len(new_sources), new_sources
    
    def _learn_source(self, source_data: Dict, source_info: Dict, category: str) -> bool:
        """学习单个书源"""
        try:
            from reference_learning_module import ReferenceLearningModule
            learning_module = ReferenceLearningModule()

            # 检查是否已学习
            source_id = source_info.get('source_id')
            if source_id and learning_module.is_learned(source_id=source_id):
                logger.info(f"书源已学习过，跳过: {source_id}")
                return True

            success = learning_module.learn_book_source(source_data, source_info, category)
            return success
        except Exception as e:
            logger.error(f"学习书源失败: {e}")
            return False
    
    def crawl_and_learn_category(self, category_name: str, force_update: bool = False) -> int:
        """爬取并学习指定分类"""
        logger.info(f"开始爬取并学习分类: {category_name}")
        
        if category_name not in CATEGORIES:
            logger.error(f"未知分类: {category_name}")
            return 0
        
        config = CATEGORIES[category_name]
        url = urljoin(BASE_URL, config['url'])
        
        # 获取列表页面
        html = self._get_page(url)
        if not html:
            logger.error(f"获取列表页面失败: {url}")
            return 0
        
        # 解析书源列表
        sources = self._parse_source_list(html)
        logger.info(f"共找到 {len(sources)} 个书源")
        
        if len(sources) == 0:
            logger.info("未找到书源，跳过处理")
            return 0
        
        # 检查更新（除非强制更新）
        if not force_update:
            new_count, new_sources = self._check_updates(category_name, sources)
            
            if new_count == 0:
                logger.info(f"分类 {category_name} 没有新书源，跳过处理")
                return 0
            
            logger.info(f"分类 {category_name} 发现 {new_count} 个新书源")
            sources = new_sources
        
        # 下载并学习
        success_count = 0
        for source in sources:
            # 下载书源
            source_data = self._download_source(source['json_url'])
            if source_data:
                # 判断是否是书源
                if not self._is_book_source(source_data):
                    logger.info(f"跳过非书源数据: {source['title']} (ID: {source['source_id']})")
                    continue
                
                # 构造书源信息
                source_info = {
                    'source_id': source['source_id'],
                    'link': source['link'],
                    'pub_time': source['pub_time'],
                    'description': source.get('description', '')
                }
                
                # 学习书源
                success = self._learn_source(source_data, source_info, category_name)
                
                # 记录日志
                self._log_learning(
                    source['source_id'],
                    source['title'],
                    success,
                    "学习成功" if success else "学习失败"
                )
                
                if success:
                    success_count += 1
                    logger.info(f"✓ 成功学习: {source['title']} (ID: {source['source_id']})")
                else:
                    logger.warning(f"✗ 学习失败: {source['title']} (ID: {source['source_id']})")
                
                time.sleep(1)  # 避免请求过快
            else:
                logger.warning(f"下载失败: {source['title']} (ID: {source['source_id']})")
        
        logger.info(f"分类 {category_name} 爬取并学习完成，成功 {success_count} 个书源")
        return success_count
    
    def crawl_and_learn_all(self, force_update: bool = False) -> int:
        """爬取并学习所有分类"""
        logger.info("开始爬取并学习所有分类...")
        
        total_success = 0
        for category_name in CATEGORIES.keys():
            try:
                success_count = self.crawl_and_learn_category(category_name, force_update)
                total_success += success_count
                time.sleep(2)  # 分类之间间隔
            except Exception as e:
                logger.error(f"爬取分类 {category_name} 失败: {e}")
                continue
        
        logger.info(f"所有分类爬取并学习完成，总共成功 {total_success} 个书源")
        
        # 导出学习摘要
        try:
            from reference_learning_module import ReferenceLearningModule
            learning_module = ReferenceLearningModule()
            summary = learning_module.export_learning_summary()
            logger.info("学习摘要已导出")
        except Exception as e:
            logger.error(f"导出学习摘要失败: {e}")
        
        return total_success
    
    def smart_crawl_and_learn(self) -> bool:
        """智能爬取并学习：仅在有更新时才运行"""
        logger.info("执行智能爬取并学习...")
        
        has_updates = False
        update_details = {}
        
        for category_name in CATEGORIES.keys():
            config = CATEGORIES[category_name]
            url = urljoin(BASE_URL, config['url'])
            
            html = self._get_page(url)
            if html:
                sources = self._parse_source_list(html)
                new_count, _ = self._check_updates(category_name, sources)
                
                if new_count > 0:
                    has_updates = True
                    update_details[category_name] = new_count
        
        if has_updates:
            logger.info(f"检测到更新: {update_details}")
            total_success = self.crawl_and_learn_all(force_update=False)
            logger.info(f"智能爬取并学习完成，成功 {total_success} 个书源")
            return True
        else:
            logger.info("未检测到更新，跳过爬取")
            return False
    
    def run_daily(self, use_smart_mode: bool = True):
        """每日定时任务"""
        logger.info(f"开始执行每日定时学习任务: {datetime.now()}")
        logger.info(f"模式: {'智能模式（仅在有更新时运行）' if use_smart_mode else '完整模式'}")
        
        if use_smart_mode:
            has_updates = self.smart_crawl_and_learn()
            if has_updates:
                logger.info("检测到更新并完成学习")
            else:
                logger.info("没有更新，本次任务完成")
        else:
            self.crawl_and_learn_all(force_update=False)
        
        logger.info(f"每日定时学习任务完成: {datetime.now()}")


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("参考学习模块爬虫启动")
    logger.info("=" * 50)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='参考学习模块爬虫')
    parser.add_argument('--force', action='store_true', help='强制更新所有书源')
    parser.add_argument('--no-smart', action='store_true', help='禁用智能模式')
    parser.add_argument('--category', type=str, help='只学习指定分类')
    parser.add_argument('--once', action='store_true', help='只执行一次，不启动定时任务')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = LearningCrawler()
    
    # 执行学习
    if args.category:
        # 只学习指定分类
        logger.info(f"只学习分类: {args.category}")
        success_count = crawler.crawl_and_learn_category(args.category, force_update=args.force)
        logger.info(f"分类 {args.category} 学习完成，成功 {success_count} 个书源")
    else:
        # 学习所有分类
        logger.info("开始执行学习任务...")
        if args.no_smart or args.force:
            logger.info("使用完整模式")
            crawler.crawl_and_learn_all(force_update=args.force)
        else:
            logger.info("使用智能模式（仅在有更新时运行）")
            crawler.smart_crawl_and_learn()
    
    # 如果不是只执行一次，则启动定时任务
    if not args.once:
        # 设置定时任务（每天早上8点执行）
        schedule.every().day.at("08:00").do(
            crawler.run_daily, 
            use_smart_mode=not args.no_smart
        )
        
        logger.info("定时任务已设置，每天早上8点执行")
        logger.info("按 Ctrl+C 停止程序")
        
        # 保持运行
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("用户中断，程序退出")
    else:
        logger.info("任务完成，程序退出")


if __name__ == "__main__":
    main()
