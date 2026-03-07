"""
Legado订阅源爬虫 v2.0
定期检查"源仓库"订阅源的更新，自动下载书源并学习到知识库
新增功能：
1. 智能更新检测 - 仅在有更新时运行
2. 自动学习 - 自动将新书源导入知识库
3. 定时调度 - 每天凌晨自动运行
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import schedule

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入参考学习模块
from scripts.reference_learning_module import ReferenceLearningModule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置常量
BASE_URL = "https://www.yck2026.top"
CONFIG_FILE = "scripts/crawler_config.json"
DATABASE_DIR = "assets/book_source_database"
REFERENCE_DIR = "assets/book_source_reference"
METADATA_FILE = "assets/metadata.json"
UPDATE_CHECK_FILE = "scripts/update_check.json"

# 分类配置
CATEGORIES = {
    "书源": {
        "url": "/yuedu/shuyuan/index.html",
        "subdir": "book_sources"
    },
    "书源合集": {
        "url": "/yuedu/shuyuans/index.html",
        "subdir": "book_source_collections"
    },
    "订阅源": {
        "url": "/yuedu/rss/index.html",
        "subdir": "rss_sources"
    },
    "订阅源合集": {
        "url": "/yuedu/rsss/index.html",
        "subdir": "rss_source_collections"
    }
}


class LegadoSourceCrawler:
    """Legado订阅源爬虫"""
    
    def __init__(self, enable_learning=True):
        """
        初始化爬虫
        
        Args:
            enable_learning: 是否启用参考学习模块
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.metadata = self._load_metadata()
        self.update_check_data = self._load_update_check()
        self._init_directories()
        
        # 初始化参考学习模块
        self.enable_learning = enable_learning
        if enable_learning:
            try:
                self.learning_module = ReferenceLearningModule()
                logger.info("参考学习模块已启用")
            except Exception as e:
                logger.error(f"初始化参考学习模块失败: {e}")
                self.enable_learning = False
                self.learning_module = None
        else:
            self.learning_module = None
    
    def _init_directories(self):
        """初始化目录结构"""
        directories = [
            DATABASE_DIR,
            REFERENCE_DIR,
            os.path.join(DATABASE_DIR, "book_sources"),
            os.path.join(DATABASE_DIR, "book_source_collections"),
            os.path.join(DATABASE_DIR, "rss_sources"),
            os.path.join(DATABASE_DIR, "rss_source_collections"),
            os.path.join(REFERENCE_DIR, "book_count_refs"),
            os.path.join(REFERENCE_DIR, "other_refs")
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"确保目录存在: {directory}")
    
    def _load_metadata(self) -> Dict:
        """加载元数据"""
        if os.path.exists(METADATA_FILE):
            try:
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载元数据失败: {e}")
                return {}
        return {}
    
    def _load_update_check(self) -> Dict:
        """加载更新检测数据"""
        if os.path.exists(UPDATE_CHECK_FILE):
            try:
                with open(UPDATE_CHECK_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载更新检测数据失败: {e}")
                return {}
        return {}
    
    def _save_update_check(self):
        """保存更新检测数据"""
        try:
            os.makedirs(os.path.dirname(UPDATE_CHECK_FILE), exist_ok=True)
            with open(UPDATE_CHECK_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.update_check_data, f, indent=2, ensure_ascii=False)
            logger.info("更新检测数据已保存")
        except Exception as e:
            logger.error(f"保存更新检测数据失败: {e}")
    
    def _check_updates(self, category: str, sources: List[Dict]) -> Tuple[int, List[Dict]]:
        """
        检查更新
        
        Args:
            category: 分类名称
            sources: 书源列表
        
        Returns:
            (新增数量, 新增书源列表)
        """
        if 'last_check' not in self.update_check_data:
            self.update_check_data['last_check'] = {}
        
        last_check = self.update_check_data['last_check'].get(category, {})
        new_sources = []
        
        for source in sources:
            source_hash = source['hash']
            
            # 检查是否是新书源
            if source_hash not in last_check:
                new_sources.append(source)
                logger.info(f"发现新书源: {source['title']}")
        
        # 只在检测到更新时更新检测数据
        if new_sources:
            # 更新检测数据，只添加新书源
            for source in new_sources:
                if category not in self.update_check_data['last_check']:
                    self.update_check_data['last_check'][category] = {}
                self.update_check_data['last_check'][category][source['hash']] = {
                    'title': source['title'],
                    'link': source['link'],
                    'pub_time': source['pub_time'],
                    'source_id': source.get('source_id'),
                    'first_seen': datetime.now().isoformat()
                }
            self.update_check_data['last_check_time'] = datetime.now().isoformat()
            self._save_update_check()
        
        return len(new_sources), new_sources
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info("元数据已保存")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
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
        
        # 直接查找所有的链接
        links = soup.find_all('a', href=True)
        
        logger.info(f"找到 {len(links)} 个链接")
        
        for link in links:
            try:
                href = link.get('href')
                
                # 只处理书源相关的链接
                if not href or '/yuedu/shuyuan/content/id/' not in href:
                    continue
                
                title = link.get_text(strip=True)
                
                # 跳过空标题或特殊标题
                if not title or len(title) < 2:
                    continue
                
                # 获取链接后面的信息
                info_text = ""
                next_sibling = link.find_next_sibling()
                while next_sibling and next_sibling.name != 'br' and next_sibling.name != 'a':
                    info_text += next_sibling.get_text(strip=True) + " "
                    next_sibling = next_sibling.find_next_sibling()
                
                # 解析发布时间
                pub_time = "未知"
                if '小时前' in info_text:
                    pub_time = info_text
                elif '天前' in info_text:
                    pub_time = info_text
                
                # 解析JSON导入链接
                json_url = self._extract_json_url(href)
                
                # 提取原始ID
                import re
                source_id = None
                pattern = r'/yuedu/(\w+)/content/id/(\d+)\.html'
                match = re.search(pattern, href)
                if match:
                    source_id = match.group(2)
                
                sources.append({
                    'title': title,
                    'link': href,
                    'pub_time': pub_time,
                    'description': info_text,
                    'source_id': source_id,  # 添加原始ID
                    'json_url': json_url,
                    'hash': self._compute_hash(title + href)
                })
                
                logger.info(f"解析书源: {title} - {json_url} (ID: {source_id})")
                
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
            # 匹配模式: /yuedu/{type}/content/id/{id}.html
            # 转换为: /yuedu/{type}/json/id/{id}.json
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
            
            # 尝试解析JSON
            if response.text.strip().startswith('['):
                sources = json.loads(response.text)
                return sources
            else:
                logger.warning(f"返回的不是JSON数组: {json_url}")
                return None
                
        except Exception as e:
            logger.error(f"下载书源失败 {json_url}: {e}")
            return None
    
    def _save_source(self, source_data: Dict, category: str, source_id: str, title: str, source_info: dict = None):
        """
        保存书源文件并自动学习
        
        Args:
            source_data: 书源数据
            category: 分类
            source_id: 原始书源ID
            title: 书源标题
            source_info: 书源信息（用于学习）
        """
        try:
            # 判断是否是书源数量参考文件
            is_count_ref = self._is_count_reference(source_data, title)
            
            # 选择保存目录
            if is_count_ref:
                save_dir = os.path.join(REFERENCE_DIR, "book_count_refs")
                logger.info(f"识别为书源数量参考文件，保存到: {save_dir}")
            else:
                save_dir = os.path.join(DATABASE_DIR, CATEGORIES[category]["subdir"])
                logger.info(f"保存到数据库目录: {save_dir}")
            
            # 生成文件名（使用原始ID）
            filename = self._generate_filename(source_id, title, is_count_ref)
            filepath = os.path.join(save_dir, filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(source_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"书源已保存: {filepath}")
            
            # 自动学习（如果不是参考文件）
            if not is_count_ref and self.enable_learning and self.learning_module and source_info:
                try:
                    success = self.learning_module.learn_book_source(source_data, source_info, category)
                    if success:
                        logger.info(f"✓ 书源已学习到知识库: {title} (ID: {source_id})")
                    else:
                        logger.warning(f"✗ 书源学习失败: {title} (ID: {source_id})")
                except Exception as e:
                    logger.error(f"学习书源时出错: {e}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存书源失败: {e}")
            return None
    
    def _is_count_reference(self, source_data: Dict, title: str) -> bool:
        """
        判断是否是书源数量参考文件
        
        Args:
            source_data: 书源数据
            title: 书源标题
        
        Returns:
            是否是统计参考文件
        """
        # 首先检查标题中的关键词（必须包含）
        count_keywords = ['数量', '统计', '排行', 'count', 'number', 'rank']
        title_lower = title.lower()
        
        has_title_keyword = False
        for keyword in count_keywords:
            if keyword in title_lower:
                has_title_keyword = True
                break
        
        # 如果标题不包含关键词，肯定不是统计参考文件
        if not has_title_keyword:
            return False
        
        # 如果标题包含关键词，还需要验证数据结构
        # 统计参考文件通常是列表，包含多个书源的统计信息
        if isinstance(source_data, list) and len(source_data) > 1:
            # 检查是否多个元素都包含统计相关的字段
            stats_keywords = ['count', 'total', 'number', 'weight', 'respondTime']
            stats_count = 0
            
            for source in source_data:
                if isinstance(source, dict):
                    for key in source:
                        if any(keyword in key.lower() for keyword in stats_keywords):
                            stats_count += 1
                            break
            
            # 如果超过一半的元素包含统计字段，认为是统计参考文件
            return stats_count > len(source_data) / 2
        
        return False
    
    def _generate_filename(self, source_id: str, title: str, is_count_ref: bool) -> str:
        """
        生成文件名
        
        Args:
            source_id: 原始书源ID
            title: 书源标题
            is_count_ref: 是否是参考文件
        
        Returns:
            文件名
        """
        # 清理标题（用于显示）
        title_clean = title.replace('/', '-').replace('\\', '-').replace(':', '-')
        title_clean = title_clean.replace('*', '').replace('?', '').replace('"', '')
        title_clean = title_clean.replace('<', '').replace('>', '').replace('|', '')
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 使用原始ID作为文件名的主要部分
        if is_count_ref:
            return f"{source_id}_{title_clean}_统计_{timestamp}.json"
        else:
            return f"{source_id}_{title_clean}_{timestamp}.json"
    
    def _check_update(self, source_hash: str) -> bool:
        """检查是否已存在"""
        return source_hash in self.metadata.get('processed_hashes', set())
    
    def _mark_processed(self, source_hash: str, source_info: Dict):
        """标记为已处理"""
        if 'processed_hashes' not in self.metadata:
            self.metadata['processed_hashes'] = {}
        
        self.metadata['processed_hashes'][source_hash] = {
            'timestamp': datetime.now().isoformat(),
            'title': source_info.get('title'),
            'json_url': source_info.get('json_url'),
            'source_id': source_info.get('source_id')
        }
        
        self._save_metadata()
    
    def crawl_category(self, category_name: str, force_update: bool = False):
        """
        爬取指定分类
        
        Args:
            category_name: 分类名称
            force_update: 是否强制更新（忽略更新检测）
        
        Returns:
            新增书源数量
        """
        logger.info(f"开始爬取分类: {category_name}")
        
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
        
        # 下载并保存
        success_count = 0
        for source in sources:
            # 检查是否已处理（强制更新时跳过此检查）
            if not force_update and self._check_update(source['hash']):
                logger.info(f"跳过已处理的书源: {source['title']}")
                continue

            # 检查是否已学习（避免重复下载已学习的书源）
            if self.enable_learning and self.learning_module:
                source_id = source.get('source_id')
                if source_id and self.learning_module.is_learned(source_id=source_id):
                    logger.info(f"跳过已学习的书源: {source['title']} (ID: {source_id})")
                    # 标记为已处理（避免下次重复检查）
                    self._mark_processed(source['hash'], source)
                    continue

            # 下载书源
            source_data = self._download_source(source['json_url'])
            if source_data:
                # 保存书源（包含自动学习）
                source_info = {
                    'link': source['link'],
                    'pub_time': source['pub_time'],
                    'description': source['description'],
                    'source_id': source['source_id']
                }
                filepath = self._save_source(source_data, category_name, source['source_id'], source['title'], source_info)

                if filepath:
                    # 标记为已处理
                    self._mark_processed(source['hash'], source)
                    success_count += 1
                    time.sleep(1)  # 避免请求过快
            else:
                logger.warning(f"下载失败: {source['title']}")
        
        logger.info(f"分类 {category_name} 爬取完成，新增 {success_count} 个书源")
        return success_count
    
    def crawl_all_categories(self, force_update: bool = False):
        """
        爬取所有分类
        
        Args:
            force_update: 是否强制更新所有分类
        
        Returns:
            总新增数量
        """
        logger.info("开始爬取所有分类...")
        
        total_new = 0
        for category_name in CATEGORIES.keys():
            try:
                new_count = self.crawl_category(category_name, force_update=force_update)
                total_new += new_count
                time.sleep(2)  # 分类之间间隔
            except Exception as e:
                logger.error(f"爬取分类 {category_name} 失败: {e}")
                continue
        
        logger.info(f"所有分类爬取完成，总共新增 {total_new} 个书源")
        
        # 导出学习摘要（如果启用了学习模块）
        if self.enable_learning and self.learning_module:
            try:
                summary = self.learning_module.export_learning_summary()
                logger.info("学习摘要已导出")
            except Exception as e:
                logger.error(f"导出学习摘要失败: {e}")
        
        return total_new
    
    def smart_crawl(self):
        """
        智能爬取：仅在有更新时才运行
        
        Returns:
            是否执行了爬取
        """
        logger.info("执行智能爬取...")
        
        # 快速检查是否有更新
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
            total_new = self.crawl_all_categories(force_update=False)
            logger.info(f"智能爬取完成，新增 {total_new} 个书源")
            return True
        else:
            logger.info("未检测到更新，跳过爬取")
            return False
    
    def run_daily(self, use_smart_mode: bool = True):
        """
        每日定时任务
        
        Args:
            use_smart_mode: 是否使用智能模式（仅在有更新时运行）
        """
        logger.info(f"开始执行每日定时任务: {datetime.now()}")
        logger.info(f"模式: {'智能模式（仅在有更新时运行）' if use_smart_mode else '完整模式'}")
        
        if use_smart_mode:
            has_updates = self.smart_crawl()
            if has_updates:
                logger.info("检测到更新并完成爬取")
            else:
                logger.info("没有更新，本次任务完成")
        else:
            self.crawl_all_categories(force_update=False)
        
        logger.info(f"每日定时任务完成: {datetime.now()}")


def main():
    """
    主函数
    支持命令行参数：
        --force: 强制更新所有书源（忽略更新检测）
        --no-smart: 禁用智能模式（完整爬取）
        --category <name>: 只爬取指定分类
        --once: 只执行一次，不启动定时任务
    """
    logger.info("=" * 50)
    logger.info("Legado订阅源爬虫启动")
    logger.info("=" * 50)
    
    # 解析命令行参数
    force_update = '--force' in sys.argv
    use_smart_mode = '--no-smart' not in sys.argv
    run_once = '--once' in sys.argv
    
    # 获取指定分类（如果有）
    category_name = None
    if '--category' in sys.argv:
        try:
            idx = sys.argv.index('--category')
            if idx + 1 < len(sys.argv):
                category_name = sys.argv[idx + 1]
        except:
            pass
    
    # 创建爬虫实例
    crawler = LegadoSourceCrawler()
    
    # 执行爬取
    if category_name:
        # 只爬取指定分类
        logger.info(f"只爬取分类: {category_name}")
        new_count = crawler.crawl_category(category_name, force_update=force_update)
        logger.info(f"分类 {category_name} 爬取完成，新增 {new_count} 个书源")
    else:
        # 爬取所有分类
        logger.info("开始执行爬取任务...")
        if use_smart_mode and not force_update:
            logger.info("使用智能模式（仅在有更新时运行）")
            has_updates = crawler.smart_crawl()
            if has_updates:
                logger.info("检测到更新并完成爬取")
            else:
                logger.info("没有更新，本次任务完成")
        else:
            logger.info("使用完整模式")
            crawler.crawl_all_categories(force_update=force_update)
    
    # 如果不是只执行一次，则启动定时任务
    if not run_once:
        # 设置定时任务（每天凌晨2点执行）
        schedule.every().day.at("02:00").do(crawler.run_daily, use_smart_mode=use_smart_mode)
        
        logger.info("定时任务已设置，每天凌晨2点执行")
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
