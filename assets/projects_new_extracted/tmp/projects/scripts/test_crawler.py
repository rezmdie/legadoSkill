"""
测试爬虫 - 执行一次后退出
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legado_source_crawler import LegadoSourceCrawler

def test_crawler():
    """测试爬虫"""
    print("=" * 50)
    print("测试Legado订阅源爬虫")
    print("=" * 50)
    
    # 创建爬虫实例
    crawler = LegadoSourceCrawler()
    
    # 执行一次爬取
    print("\n开始执行爬取...")
    crawler.crawl_all_categories()
    
    print("\n测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    test_crawler()
