"""
Legado订阅源爬虫工具
用于定期爬取订阅源中的书源，并保存到本地数据库
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

# 获取工作区路径
WORKSPACE_PATH = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
DATA_DIR = os.path.join(WORKSPACE_PATH, "data")
BOOK_SOURCE_DIR = os.path.join(DATA_DIR, "book_sources")


@tool
def crawl_subscription_source(subscription_url: str, category: str = "书源", runtime: ToolRuntime = None) -> str:
    """
    爬取订阅源中的书源列表
    
    参数:
        subscription_url: 订阅源URL（JSON格式）
        category: 分类名称（书源、订阅源、书源合集等）
    
    返回:
        爬取结果摘要
    """
    ctx = runtime.context if runtime else new_context(method="crawl_subscription_source")
    
    try:
        # 读取订阅源配置
        import requests
        response = requests.get(subscription_url, timeout=30)
        response.raise_for_status()
        
        subscription_data = response.json()
        
        if not subscription_data:
            return "❌ 订阅源数据为空"
        
        source = subscription_data[0]
        source_url = source.get("sourceUrl", "")
        
        if not source_url:
            return "❌ 订阅源缺少sourceUrl"
        
        # 解析sortUrl获取分类URL
        sort_urls = source.get("sortUrl", "")
        category_url = _extract_category_url(sort_urls, category)
        
        if not category_url:
            return f"❌ 未找到分类: {category}"
        
        # 爬取书源列表
        result = _crawl_book_sources(source_url, category_url, source)
        
        return result
        
    except Exception as e:
        return f"❌ 爬取失败: {str(e)}"


@tool
def extract_book_sources(subscription_url: str, category: str = "书源", max_pages: int = 5, runtime: ToolRuntime = None) -> str:
    """
    从订阅源中提取书源并保存到本地
    
    参数:
        subscription_url: 订阅源URL
        category: 分类名称
        max_pages: 最大爬取页数
    
    返回:
        提取结果摘要
    """
    ctx = runtime.context if runtime else new_context(method="extract_book_sources")
    
    try:
        # 确保数据目录存在
        os.makedirs(BOOK_SOURCE_DIR, exist_ok=True)
        
        # 读取订阅源配置
        import requests
        response = requests.get(subscription_url, timeout=30)
        response.raise_for_status()
        
        subscription_data = response.json()
        source = subscription_data[0]
        source_url = source.get("sourceUrl", "")
        
        # 解析sortUrl获取分类URL
        sort_urls = source.get("sortUrl", "")
        category_url = _extract_category_url(sort_urls, category)
        
        # 爬取多页书源
        all_sources = []
        for page in range(1, max_pages + 1):
            page_url = category_url.replace("{{page}}", str(page))
            sources = _fetch_book_source_page(source_url, page_url, source)
            if not sources:
                break
            all_sources.extend(sources)
            time.sleep(1)  # 避免请求过快
        
        # 保存书源到本地
        saved_count = _save_book_sources(all_sources, category)
        
        return f"✅ 成功提取 {saved_count} 个书源到 {category} 分类"
        
    except Exception as e:
        return f"❌ 提取失败: {str(e)}"


@tool
def save_book_source_to_db(source_json: str, category: str = "书源", runtime: ToolRuntime = None) -> str:
    """
    保存单个书源到数据库
    
    参数:
        source_json: 书源JSON字符串
        category: 分类
    
    返回:
        保存结果
    """
    ctx = runtime.context if runtime else new_context(method="save_book_source_to_db")
    
    try:
        # 解析书源JSON
        sources = json.loads(source_json)
        if isinstance(sources, dict):
            sources = [sources]
        
        # 保存书源
        os.makedirs(BOOK_SOURCE_DIR, exist_ok=True)
        saved_count = _save_book_sources(sources, category)
        
        return f"✅ 成功保存 {saved_count} 个书源"
        
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"


@tool
def list_saved_sources(category: str = "书源", runtime: ToolRuntime = None) -> str:
    """
    列出已保存的书源
    
    参数:
        category: 分类名称
    
    返回:
        书源列表
    """
    ctx = runtime.context if runtime else new_context(method="list_saved_sources")
    
    try:
        category_dir = os.path.join(BOOK_SOURCE_DIR, category)
        if not os.path.exists(category_dir):
            return f"❌ 分类 {category} 不存在"
        
        # 获取所有书源文件
        files = [f for f in os.listdir(category_dir) if f.endswith('.json')]
        
        if not files:
            return f"📁 分类 {category} 中暂无书源"
        
        result = f"📚 分类 {category} 共有 {len(files)} 个书源：\n\n"
        
        for i, filename in enumerate(files[:20], 1):  # 最多显示20个
            filepath = os.path.join(category_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                source = json.load(f)
            
            source_name = source.get("bookSourceName", "未命名")
            source_url = source.get("bookSourceUrl", "")
            enabled = "✅" if source.get("enabled", True) else "❌"
            
            result += f"{i}. {enabled} {source_name}\n"
            result += f"   URL: {source_url}\n"
            result += f"   文件: {filename}\n\n"
        
        if len(files) > 20:
            result += f"... 还有 {len(files) - 20} 个书源未显示"
        
        return result
        
    except Exception as e:
        return f"❌ 列出书源失败: {str(e)}"


@tool
def check_update(subscription_url: str, category: str = "书源", runtime: ToolRuntime = None) -> str:
    """
    检查订阅源是否有更新
    
    参数:
        subscription_url: 订阅源URL
        category: 分类名称
    
    返回:
        更新检查结果
    """
    ctx = runtime.context if runtime else new_context(method="check_update")
    
    try:
        # 获取本地保存的书源URL列表
        category_dir = os.path.join(BOOK_SOURCE_DIR, category)
        local_urls = set()
        
        if os.path.exists(category_dir):
            for filename in os.listdir(category_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(category_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = json.load(f)
                    local_urls.add(source.get("bookSourceUrl", ""))
        
        # 获取远程书源列表
        import requests
        response = requests.get(subscription_url, timeout=30)
        response.raise_for_status()
        
        subscription_data = response.json()
        source = subscription_data[0]
        source_url = source.get("sourceUrl", "")
        
        sort_urls = source.get("sortUrl", "")
        category_url = _extract_category_url(sort_urls, category)
        
        remote_sources = _fetch_book_source_page(source_url, category_url, source)
        remote_urls = {s.get("bookSourceUrl", "") for s in remote_sources}
        
        # 对比找出更新
        new_sources = remote_urls - local_urls
        removed_sources = local_urls - remote_urls
        
        result = f"📊 更新检查结果（{category}）：\n\n"
        result += f"📦 本地书源数量: {len(local_urls)}\n"
        result += f"🌐 远程书源数量: {len(remote_urls)}\n"
        result += f"➕ 新增书源: {len(new_sources)}\n"
        result += f"➖ 移除书源: {len(removed_sources)}\n\n"
        
        if new_sources:
            result += "🆕 新增书源列表：\n"
            for url in list(new_sources)[:10]:
                result += f"  - {url}\n"
            if len(new_sources) > 10:
                result += f"  ... 还有 {len(new_sources) - 10} 个\n"
        
        return result
        
    except Exception as e:
        return f"❌ 检查更新失败: {str(e)}"


# 辅助函数

def _extract_category_url(sort_urls: str, category: str) -> Optional[str]:
    """从sortUrl中提取指定分类的URL"""
    for line in sort_urls.split('\n'):
        if line.strip():
            parts = line.split('::', 1)
            if len(parts) == 2 and category in parts[0]:
                return parts[1].strip()
    return None


def _crawl_book_sources(source_url: str, category_url: str, source_config: dict) -> str:
    """爬取书源列表"""
    sources = _fetch_book_source_page(source_url, category_url, source_config)
    
    if not sources:
        return "❌ 未找到书源"
    
    # 保存书源
    os.makedirs(BOOK_SOURCE_DIR, exist_ok=True)
    saved_count = _save_book_sources(sources, "书源")
    
    return f"✅ 成功爬取 {saved_count} 个书源"


def _fetch_book_source_page(source_url: str, page_url: str, source_config: dict) -> List[dict]:
    """获取单页书源数据"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        # 获取页面内容
        response = requests.get(page_url, timeout=30)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用配置中的规则提取书源链接
        rule_articles = source_config.get("ruleArticles", "")
        rule_link = source_config.get("ruleLink", "a@href")
        
        # 提取书源列表
        book_links = _extract_links(soup, rule_articles, rule_link)
        
        # 提取书源详情
        sources = []
        for link in book_links:
            if link.startswith('/'):
                full_url = source_url.rstrip('/') + link
            elif link.startswith('http'):
                full_url = link
            else:
                continue
            
            # 获取书源JSON
            if 'json/id' in full_url:
                try:
                    source_response = requests.get(full_url, timeout=10)
                    source_response.raise_for_status()
                    source_data = source_response.json()
                    if isinstance(source_data, list):
                        sources.extend(source_data)
                    else:
                        sources.append(source_data)
                    time.sleep(0.5)  # 避免请求过快
                except:
                    pass
        
        return sources
        
    except Exception as e:
        return []


def _extract_links(soup, rule_articles: str, rule_link: str) -> List[str]:
    """从HTML中提取链接"""
    links = []
    
    # 简化实现，实际应该按照规则解析
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'json/id' in href:
            links.append(href)
    
    return links


def _save_book_sources(sources: List[dict], category: str) -> int:
    """保存书源到本地"""
    count = 0
    category_dir = os.path.join(BOOK_SOURCE_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        # 生成文件名（使用URL的hash作为文件名）
        import hashlib
        source_url = source.get("bookSourceUrl", "")
        if not source_url:
            continue
        
        filename = hashlib.md5(source_url.encode('utf-8')).hexdigest() + '.json'
        filepath = os.path.join(category_dir, filename)
        
        # 保存书源
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(source, f, ensure_ascii=False, indent=2)
        
        count += 1
    
    return count
