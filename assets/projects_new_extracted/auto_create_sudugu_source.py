#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化书源创建脚本 - 智能循环版本
不断尝试创建书源，遇到错误自动修复，直到成功为止
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

# 设置环境变量
os.environ['MCP_MODE'] = 'false'

from src.tools.smart_fetcher import smart_fetch_html
from src.tools.smart_web_analyzer import smart_analyze_website
from src.tools.smart_full_analyzer import analyze_complete_book_source


class AutoBookSourceCreator:
    """自动书源创建器"""
    
    def __init__(self, url):
        self.url = url
        self.max_retries = 10
        self.retry_count = 0
        self.errors_log = []
        
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        # 安全打印，避免GBK编码错误
        try:
            print(log_msg)
        except UnicodeEncodeError:
            # 如果包含无法编码的字符，替换为ASCII
            safe_msg = log_msg.encode('ascii', errors='replace').decode('ascii')
            print(safe_msg)
        self.errors_log.append(log_msg)
        
    def save_result(self, result, filename):
        """保存结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(result, dict):
                    json.dump(result, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(result))
            self.log(f"结果已保存到: {filename}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"保存结果失败: {e}", "ERROR")
            return False
    
    def fix_encoding_issues(self):
        """修复编码问题"""
        self.log("检查并修复编码问题...", "FIX")
        try:
            # 运行emoji修复脚本
            import subprocess
            result = subprocess.run(
                ['python', 'fix_emoji_encoding.py'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if result.returncode == 0:
                self.log("编码问题已修复", "SUCCESS")
                return True
            else:
                self.log(f"编码修复失败: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"编码修复异常: {e}", "ERROR")
            return False
    
    async def step1_fetch_html(self):
        """步骤1: 获取网页HTML"""
        self.log(f"步骤1: 获取网页HTML - {self.url}", "STEP")
        try:
            result = await smart_fetch_html.ainvoke({
                "url": self.url,
                "method": "GET",
                "headers": "",
                "data": ""
            })
            
            # smart_fetch_html 返回的是字符串报告，不是字典
            if result and isinstance(result, str):
                if "[ERROR]" in result:
                    self.log("获取HTML失败", "ERROR")
                    self.log(result[:500], "DEBUG")
                    return None
                else:
                    self.log(f"成功获取HTML报告，大小: {len(result)} 字符", "SUCCESS")
                    self.save_result(result, 'sudugu_step1_html_report.txt')
                    return result
            else:
                self.log("获取HTML失败，返回结果为空", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"获取HTML异常: {e}", "ERROR")
            self.log(traceback.format_exc(), "DEBUG")
            return None
    
    async def step2_analyze_website(self):
        """步骤2: 分析网站结构"""
        self.log(f"步骤2: 分析网站结构 - {self.url}", "STEP")
        try:
            result = await smart_analyze_website.ainvoke({
                "url": self.url,
                "page_type": "all"
            })
            
            # 工具返回字符串报告
            if result and isinstance(result, str):
                # 检查是否是真正的错误（整个分析失败）
                # 报告中可能包含 [ERROR] 标记，但这只是说明某些功能未找到，不代表整个分析失败
                if result.startswith("[ERROR]") or "智能分析失败" in result:
                    self.log("网站分析失败", "ERROR")
                    self.log(result[:500], "DEBUG")
                    return None
                else:
                    self.log("网站结构分析完成", "SUCCESS")
                    self.save_result(result, 'sudugu_step2_analysis.txt')
                    return result
            else:
                self.log("网站分析失败，返回结果为空", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"网站分析异常: {e}", "ERROR")
            self.log(traceback.format_exc(), "DEBUG")
            return None
    
    async def step3_create_book_source(self):
        """步骤3: 创建完整书源"""
        self.log(f"步骤3: 创建完整书源 - {self.url}", "STEP")
        try:
            # 尝试使用完整分析工具
            result = await analyze_complete_book_source.ainvoke({
                "url": self.url,
                "source_name": "速读谷"
            })
            
            # 工具返回字符串报告或JSON
            if result:
                if isinstance(result, str) and "[ERROR]" in result:
                    self.log("书源创建失败", "ERROR")
                    self.log(result[:500], "DEBUG")
                    return None
                else:
                    self.log("书源创建完成", "SUCCESS")
                    # 尝试解析为JSON，如果失败就保存为文本
                    try:
                        if isinstance(result, str):
                            json_result = json.loads(result)
                            self.save_result(json_result, 'sudugu_book_source_final.json')
                        else:
                            self.save_result(result, 'sudugu_book_source_final.json')
                    except:
                        self.save_result(result, 'sudugu_book_source_final.txt')
                    return result
            else:
                self.log("书源创建失败，返回结果为空", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"书源创建异常: {e}", "ERROR")
            self.log(traceback.format_exc(), "DEBUG")
            return None
    
    async def create_with_retry(self):
        """带重试的创建流程"""
        self.log("="*60, "INFO")
        self.log(f"开始为 {self.url} 创建书源", "INFO")
        self.log("="*60, "INFO")
        
        while self.retry_count < self.max_retries:
            self.retry_count += 1
            self.log(f"\n第 {self.retry_count} 次尝试 (最多 {self.max_retries} 次)", "INFO")
            
            try:
                # 步骤1: 获取HTML
                html_result = await self.step1_fetch_html()
                if not html_result:
                    self.log("步骤1失败，尝试修复...", "WARNING")
                    self.fix_encoding_issues()
                    time.sleep(2)
                    continue
                
                # 步骤2: 分析网站
                analysis_result = await self.step2_analyze_website()
                if not analysis_result:
                    self.log("步骤2失败，尝试修复...", "WARNING")
                    self.fix_encoding_issues()
                    time.sleep(2)
                    continue
                
                # 步骤3: 创建书源
                book_source = await self.step3_create_book_source()
                if not book_source:
                    self.log("步骤3失败，尝试修复...", "WARNING")
                    self.fix_encoding_issues()
                    time.sleep(2)
                    continue
                
                # 成功！
                self.log("="*60, "SUCCESS")
                self.log("书源创建成功！", "SUCCESS")
                self.log("="*60, "SUCCESS")
                
                # 保存错误日志
                self.save_result('\n'.join(self.errors_log), 'sudugu_creation_log.txt')
                
                return book_source
                
            except UnicodeEncodeError as e:
                self.log(f"编码错误: {e}", "ERROR")
                self.log("检测到编码问题，执行修复...", "FIX")
                self.fix_encoding_issues()
                time.sleep(2)
                continue
                
            except Exception as e:
                self.log(f"未知错误: {e}", "ERROR")
                self.log(traceback.format_exc(), "DEBUG")
                time.sleep(2)
                continue
        
        # 达到最大重试次数
        self.log("="*60, "ERROR")
        self.log(f"已达到最大重试次数 ({self.max_retries})，创建失败", "ERROR")
        self.log("="*60, "ERROR")
        
        # 保存错误日志
        self.save_result('\n'.join(self.errors_log), 'sudugu_creation_error_log.txt')
        
        return None


async def main():
    """主函数"""
    url = "https://www.sudugu.org"
    
    creator = AutoBookSourceCreator(url)
    result = await creator.create_with_retry()
    
    if result:
        print("\n" + "="*60)
        print("创建成功！书源已保存到: sudugu_book_source_final.json")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("创建失败！请查看日志文件了解详情")
        print("="*60)
        return 1


if __name__ == '__main__':
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
