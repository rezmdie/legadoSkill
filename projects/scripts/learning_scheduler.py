#!/usr/bin/env python3
"""
学习调度器

功能：
1. 管理多个学习任务
2. 支持优先级队列
3. 定时调度
4. 任务重试
"""

import os
import sys
import json
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from queue import PriorityQueue, Empty
from dataclasses import dataclass, field
from enum import Enum
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass(order=True)
class LearningTask:
    """学习任务"""
    priority: int  # 优先级（数字越小优先级越高）
    task_id: str = field(compare=False)  # 任务ID
    task_type: str = field(compare=False)  # 任务类型
    task_data: dict = field(compare=False)  # 任务数据
    created_at: str = field(compare=False)  # 创建时间
    max_retries: int = field(compare=False, default=3)  # 最大重试次数
    retry_count: int = field(compare=False, default=0)  # 当前重试次数
    callback: Optional[Callable] = field(compare=False, default=None)  # 回调函数


class LearningScheduler:
    """学习调度器"""
    
    def __init__(self):
        """初始化"""
        self.task_queue = PriorityQueue()
        self.running_tasks = {}  # 正在运行的任务
        self.completed_tasks = {}  # 已完成的任务
        self.failed_tasks = {}  # 失败的任务
        self.is_running = False
        self.worker_thread = None
        self.lock = threading.Lock()
        
        # 加载任务历史
        self.task_history = self._load_task_history()
    
    def _load_task_history(self) -> Dict:
        """加载任务历史"""
        try:
            history_file = "scripts/scheduler_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载任务历史失败: {e}")
        
        return {
            'completed': [],
            'failed': [],
            'statistics': {
                'total_completed': 0,
                'total_failed': 0
            }
        }
    
    def _save_task_history(self):
        """保存任务历史"""
        try:
            history_file = "scripts/scheduler_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存任务历史失败: {e}")
    
    def add_task(self, task_type: str, task_data: dict, 
                 priority: TaskPriority = TaskPriority.NORMAL,
                 callback: Optional[Callable] = None) -> str:
        """
        添加任务
        
        Args:
            task_type: 任务类型（'id', 'url', 'json', 'file', 'crawl'）
            task_data: 任务数据
            priority: 优先级
            callback: 回调函数
        
        Returns:
            任务ID
        """
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        
        task = LearningTask(
            priority=priority.value,
            task_id=task_id,
            task_type=task_type,
            task_data=task_data,
            created_at=datetime.now().isoformat(),
            callback=callback
        )
        
        with self.lock:
            self.task_queue.put(task)
            logger.info(f"任务已添加: {task_id} (类型: {task_type}, 优先级: {priority.name})")
        
        return task_id
    
    def add_crawl_task(self, category: str = None, force_update: bool = False,
                      priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """添加爬取学习任务"""
        task_data = {
            'category': category,
            'force_update': force_update
        }
        return self.add_task('crawl', task_data, priority)
    
    def add_id_task(self, source_id: str, category: str = "书源",
                   priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """添加ID学习任务"""
        task_data = {
            'source_id': source_id,
            'category': category
        }
        return self.add_task('id', task_data, priority)
    
    def add_url_task(self, url: str, category: str = "书源",
                    priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """添加URL学习任务"""
        task_data = {
            'url': url,
            'category': category
        }
        return self.add_task('url', task_data, priority)
    
    def add_json_task(self, json_data: str, category: str = "书源",
                     source_id: str = None, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """添加JSON学习任务"""
        task_data = {
            'json_data': json_data,
            'category': category,
            'source_id': source_id
        }
        return self.add_task('json', task_data, priority)
    
    def add_file_task(self, file_path: str, category: str = "书源",
                     priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """添加文件学习任务"""
        task_data = {
            'file_path': file_path,
            'category': category
        }
        return self.add_task('file', task_data, priority)
    
    def _execute_task(self, task: LearningTask) -> bool:
        """执行任务"""
        logger.info(f"开始执行任务: {task.task_id} (类型: {task.task_type})")
        
        try:
            from book_source_learner import BookSourceLearner
            learner = BookSourceLearner()
            
            success = False
            message = ""
            
            if task.task_type == 'id':
                success, message = learner.learn_from_id(
                    task.task_data['source_id'],
                    task.task_data['category']
                )
            
            elif task.task_type == 'url':
                success, message = learner.learn_from_url(
                    task.task_data['url'],
                    task.task_data['category']
                )
            
            elif task.task_type == 'json':
                success, message = learner.learn_from_json(
                    task.task_data['json_data'],
                    task.task_data['category'],
                    task.task_data.get('source_id')
                )
            
            elif task.task_type == 'file':
                success, message = learner.learn_from_file(
                    task.task_data['file_path'],
                    task.task_data['category']
                )
            
            elif task.task_type == 'crawl':
                from learning_crawler import LearningCrawler
                crawler = LearningCrawler()
                
                if task.task_data.get('category'):
                    success_count = crawler.crawl_and_learn_category(
                        task.task_data['category'],
                        task.task_data.get('force_update', False)
                    )
                    success = success_count > 0
                    message = f"成功学习 {success_count} 个书源"
                else:
                    success_count = crawler.crawl_and_learn_all(
                        task.task_data.get('force_update', False)
                    )
                    success = success_count > 0
                    message = f"成功学习 {success_count} 个书源"
            
            # 记录结果
            result = {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'success': success,
                'message': message,
                'completed_at': datetime.now().isoformat()
            }
            
            with self.lock:
                if success:
                    self.completed_tasks[task.task_id] = result
                    self.task_history['completed'].append(result)
                    self.task_history['statistics']['total_completed'] += 1
                else:
                    self.failed_tasks[task.task_id] = result
                    self.task_history['failed'].append(result)
                    self.task_history['statistics']['total_failed'] += 1
                
                self._save_task_history()
            
            # 调用回调函数
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    logger.error(f"回调函数执行失败: {e}")
            
            logger.info(f"任务执行{'成功' if success else '失败'}: {task.task_id} - {message}")
            return success
        
        except Exception as e:
            error_msg = f"任务执行异常: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            result = {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'success': False,
                'message': error_msg,
                'completed_at': datetime.now().isoformat()
            }
            
            with self.lock:
                self.failed_tasks[task.task_id] = result
                self._save_task_history()
            
            return False
    
    def _worker(self):
        """工作线程"""
        logger.info("工作线程已启动")
        
        while self.is_running:
            try:
                # 从队列获取任务
                task = self.task_queue.get(timeout=1)
                
                # 标记为正在运行
                with self.lock:
                    self.running_tasks[task.task_id] = task
                
                # 执行任务
                success = self._execute_task(task)
                
                # 如果失败且未超过重试次数，重新加入队列
                if not success and task.retry_count < task.max_retries:
                    task.retry_count += 1
                    # 降低优先级重新加入
                    time.sleep(5 * task.retry_count)  # 延迟重试
                    self.task_queue.put(task)
                    logger.warning(f"任务重试 ({task.retry_count}/{task.max_retries}): {task.task_id}")
                
                # 从运行中移除
                with self.lock:
                    self.running_tasks.pop(task.task_id, None)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程异常: {e}")
                continue
        
        logger.info("工作线程已停止")
    
    def start(self, max_workers: int = 1):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行")
            return
        
        self.is_running = True
        
        # 启动工作线程
        for i in range(max_workers):
            worker = threading.Thread(target=self._worker, name=f"Worker-{i}")
            worker.daemon = True
            worker.start()
        
        logger.info(f"调度器已启动 (工作线程数: {max_workers})")
    
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            logger.warning("调度器未运行")
            return
        
        self.is_running = False
        logger.info("调度器已停止")
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        with self.lock:
            return {
                'is_running': self.is_running,
                'queue_size': self.task_queue.qsize(),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'task_history': self.task_history
            }
    
    def print_status(self):
        """打印状态"""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("学习调度器状态")
        print("=" * 50)
        print(f"运行状态: {'运行中' if status['is_running'] else '已停止'}")
        print(f"队列大小: {status['queue_size']}")
        print(f"正在运行: {status['running_tasks']}")
        print(f"已完成: {status['completed_tasks']}")
        print(f"已失败: {status['failed_tasks']}")
        print(f"总计完成: {status['task_history']['statistics']['total_completed']}")
        print(f"总计失败: {status['task_history']['statistics']['total_failed']}")
        print("=" * 50 + "\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='学习调度器')
    parser.add_argument('--start', action='store_true', help='启动调度器')
    parser.add_argument('--stop', action='store_true', help='停止调度器')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--add-id', type=str, help='添加ID学习任务')
    parser.add_argument('--add-url', type=str, help='添加URL学习任务')
    parser.add_argument('--add-file', type=str, help='添加文件学习任务')
    parser.add_argument('--add-crawl', action='store_true', help='添加爬取学习任务')
    parser.add_argument('--category', type=str, default='书源', help='分类')
    parser.add_argument('--priority', type=str, default='NORMAL', 
                       choices=['LOW', 'NORMAL', 'HIGH', 'URGENT'], help='优先级')
    
    args = parser.parse_args()
    
    # 创建调度器
    scheduler = LearningScheduler()
    
    if args.start:
        scheduler.start()
        
        # 设置定时任务
        def morning_crawl():
            scheduler.add_crawl_task(priority=TaskPriority.NORMAL)
        
        def evening_crawl():
            scheduler.add_crawl_task(priority=TaskPriority.LOW)
        
        schedule.every().day.at("08:00").do(morning_crawl)
        schedule.every().day.at("20:00").do(evening_crawl)
        
        logger.info("定时任务已设置：每天8:00和20:00执行爬取学习")
        
        # 保持运行
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
                
                # 每小时打印一次状态
                if datetime.now().minute == 0:
                    scheduler.print_status()
        
        except KeyboardInterrupt:
            logger.info("用户中断，停止调度器")
            scheduler.stop()
    
    elif args.stop:
        scheduler.stop()
    
    elif args.status:
        scheduler.print_status()
    
    elif args.add_id:
        priority = TaskPriority[args.priority]
        scheduler.add_id_task(args.add_id, args.category, priority)
        print(f"已添加ID学习任务: {args.add_id}")
    
    elif args.add_url:
        priority = TaskPriority[args.priority]
        scheduler.add_url_task(args.add_url, args.category, priority)
        print(f"已添加URL学习任务: {args.add_url}")
    
    elif args.add_file:
        priority = TaskPriority[args.priority]
        scheduler.add_file_task(args.add_file, args.category, priority)
        print(f"已添加文件学习任务: {args.add_file}")
    
    elif args.add_crawl:
        priority = TaskPriority[args.priority]
        scheduler.add_crawl_task(priority=priority)
        print("已添加爬取学习任务")
        scheduler.start()
        
        # 等待任务完成
        while True:
            status = scheduler.get_status()
            if status['queue_size'] == 0 and status['running_tasks'] == 0:
                logger.info("所有任务已完成")
                break
            time.sleep(1)
        
        scheduler.stop()
        scheduler.print_status()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
