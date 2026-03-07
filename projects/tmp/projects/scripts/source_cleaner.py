"""
Legado订阅源清理脚本
清理过期的书源文件，释放磁盘空间
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 配置
DATABASE_DIR = "assets/book_source_database"
REFERENCE_DIR = "assets/book_source_reference"
METADATA_FILE = "assets/metadata.json"
RETENTION_DAYS = 30  # 保留天数

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SourceCleaner:
    """书源清理器"""
    
    def __init__(self, retention_days=RETENTION_DAYS):
        """初始化清理器"""
        self.retention_days = retention_days
        self.cutoff_time = datetime.now() - timedelta(days=retention_days)
        self.metadata = self._load_metadata()
    
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
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info("元数据已保存")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
    def _get_file_mtime(self, filepath: str) -> datetime:
        """获取文件修改时间"""
        return datetime.fromtimestamp(os.path.getmtime(filepath))
    
    def _is_old_file(self, filepath: str) -> bool:
        """判断文件是否过期"""
        mtime = self._get_file_mtime(filepath)
        return mtime < self.cutoff_time
    
    def clean_directory(self, directory: str):
        """清理指定目录"""
        logger.info(f"开始清理目录: {directory}")
        
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return
        
        deleted_count = 0
        total_size = 0
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                if self._is_old_file(filepath):
                    file_size = os.path.getsize(filepath)
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        total_size += file_size
                        logger.info(f"已删除: {filename} ({file_size / 1024:.2f} KB)")
                    except Exception as e:
                        logger.error(f"删除失败 {filename}: {e}")
        
        logger.info(f"目录清理完成: {directory}")
        logger.info(f"删除文件数: {deleted_count}")
        logger.info(f"释放空间: {total_size / 1024 / 1024:.2f} MB")
        
        return deleted_count, total_size
    
    def clean_metadata(self):
        """清理元数据中的过期记录"""
        logger.info("开始清理元数据...")
        
        if 'processed_hashes' not in self.metadata:
            logger.info("元数据中没有处理记录")
            return
        
        processed = self.metadata['processed_hashes']
        initial_count = len(processed)
        
        # 删除超过保留期限的记录
        for source_hash, info in list(processed.items()):
            if 'timestamp' in info:
                try:
                    timestamp = datetime.fromisoformat(info['timestamp'])
                    if timestamp < self.cutoff_time:
                        del processed[source_hash]
                except Exception as e:
                    logger.warning(f"解析时间戳失败 {info}: {e}")
        
        deleted_count = initial_count - len(processed)
        
        if deleted_count > 0:
            self._save_metadata()
            logger.info(f"元数据清理完成，删除 {deleted_count} 条记录")
        else:
            logger.info("元数据清理完成，没有删除记录")
    
    def clean_all(self):
        """清理所有目录和元数据"""
        logger.info("=" * 50)
        logger.info(f"开始清理，保留最近 {self.retention_days} 天的文件")
        logger.info("=" * 50)
        
        total_deleted = 0
        total_size = 0
        
        # 清理数据库目录
        database_subdirs = [
            os.path.join(DATABASE_DIR, "book_sources"),
            os.path.join(DATABASE_DIR, "book_source_collections"),
            os.path.join(DATABASE_DIR, "rss_sources"),
            os.path.join(DATABASE_DIR, "rss_source_collections"),
        ]
        
        for subdir in database_subdirs:
            deleted, size = self.clean_directory(subdir)
            total_deleted += deleted
            total_size += size
        
        # 清理参考目录
        reference_subdirs = [
            os.path.join(REFERENCE_DIR, "book_count_refs"),
            os.path.join(REFERENCE_DIR, "other_refs"),
        ]
        
        for subdir in reference_subdirs:
            deleted, size = self.clean_directory(subdir)
            total_deleted += deleted
            total_size += size
        
        # 清理元数据
        self.clean_metadata()
        
        logger.info("=" * 50)
        logger.info("清理完成")
        logger.info(f"总删除文件数: {total_deleted}")
        logger.info(f"总释放空间: {total_size / 1024 / 1024:.2f} MB")
        logger.info("=" * 50)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Legado订阅源清理脚本')
    parser.add_argument('--days', type=int, default=RETENTION_DAYS,
                       help=f'保留天数 (默认: {RETENTION_DAYS})')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行模式，不实际删除文件')
    
    args = parser.parse_args()
    
    logger.info("=" * 50)
    logger.info("Legado订阅源清理脚本")
    logger.info("=" * 50)
    
    if args.dry_run:
        logger.info("试运行模式: 不会实际删除文件")
        # TODO: 实现试运行模式
        return
    
    cleaner = SourceCleaner(retention_days=args.days)
    cleaner.clean_all()


if __name__ == "__main__":
    main()
