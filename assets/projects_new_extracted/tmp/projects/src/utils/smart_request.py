"""
智能请求工具
支持各种HTTP请求方法，确保用正确的方式获取真实内容
"""

import requests
import json
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlencode


class SmartRequest:
    """智能请求工具"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        初始化智能请求工具
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 默认headers
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """
        发送HTTP请求（支持所有方法）
        
        Args:
            url: 请求URL
            method: HTTP方法（GET, POST, PUT, DELETE, HEAD, OPTIONS等）
            params: URL参数
            data: 请求体（表单数据）
            json_data: JSON请求体
            headers: 自定义headers
            cookies: Cookies
            allow_redirects: 是否允许重定向
            verify_ssl: 是否验证SSL证书
        
        Returns:
            请求结果
        """
        # 合并headers
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)
        
        # 尝试多次请求
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # 发送请求
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=final_headers,
                    cookies=cookies,
                    allow_redirects=allow_redirects,
                    verify=verify_ssl,
                    timeout=self.timeout
                )
                
                # 返回结果
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'url': response.url,
                    'method': method.upper(),
                    'headers': dict(response.headers),
                    'cookies': dict(response.cookies),
                    'encoding': response.encoding or 'utf-8',
                    'html': response.text,
                    'content': response.content,
                    'size': len(response.content),
                    'redirect_count': len(response.history),
                    'final_url': response.url,
                    'is_real': True
                }
                
            except requests.exceptions.Timeout:
                last_error = f"请求超时（{self.timeout}秒）"
                print(f"⚠️  请求超时，重试 {attempt + 1}/{self.max_retries}")
            except requests.exceptions.ConnectionError:
                last_error = "连接错误"
                print(f"⚠️  连接错误，重试 {attempt + 1}/{self.max_retries}")
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  请求失败: {e}，重试 {attempt + 1}/{self.max_retries}")
        
        # 所有重试都失败
        return {
            'success': False,
            'error': last_error,
            'url': url,
            'method': method.upper()
        }
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        GET请求
        
        Args:
            url: 请求URL
            params: URL参数
            headers: 自定义headers
            cookies: Cookies
        
        Returns:
            请求结果
        """
        return self.fetch(
            url=url,
            method='GET',
            params=params,
            headers=headers,
            cookies=cookies
        )
    
    def post(
        self,
        url: str,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        POST请求
        
        Args:
            url: 请求URL
            data: 请求体（表单数据）
            json_data: JSON请求体
            headers: 自定义headers
            cookies: Cookies
        
        Returns:
            请求结果
        """
        return self.fetch(
            url=url,
            method='POST',
            data=data,
            json_data=json_data,
            headers=headers,
            cookies=cookies
        )
    
    def put(
        self,
        url: str,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        PUT请求
        
        Args:
            url: 请求URL
            data: 请求体（表单数据）
            json_data: JSON请求体
            headers: 自定义headers
            cookies: Cookies
        
        Returns:
            请求结果
        """
        return self.fetch(
            url=url,
            method='PUT',
            data=data,
            json_data=json_data,
            headers=headers,
            cookies=cookies
        )
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        DELETE请求
        
        Args:
            url: 请求URL
            headers: 自定义headers
            cookies: Cookies
        
        Returns:
            请求结果
        """
        return self.fetch(
            url=url,
            method='DELETE',
            headers=headers,
            cookies=cookies
        )
    
    def with_custom_headers(
        self,
        headers: Dict[str, str]
    ) -> 'SmartRequest':
        """
        设置自定义headers
        
        Args:
            headers: 自定义headers
        
        Returns:
            返回自身，支持链式调用
        """
        self.default_headers.update(headers)
        return self
    
    def with_cookie(
        self,
        cookie: Dict[str, str]
    ) -> 'SmartRequest':
        """
        添加Cookie
        
        Args:
            cookie: Cookie字典
        
        Returns:
            返回自身，支持链式调用
        """
        # 将cookie转换为Cookie字符串
        cookie_str = '; '.join([f"{k}={v}" for k, v in cookie.items()])
        self.default_headers['Cookie'] = cookie_str
        return self
    
    def with_referer(
        self,
        referer: str
    ) -> 'SmartRequest':
        """
        设置Referer
        
        Args:
            referer: Referer URL
        
        Returns:
            返回自身，支持链式调用
        """
        self.default_headers['Referer'] = referer
        return self
    
    def with_authorization(
        self,
        token: str,
        auth_type: str = 'Bearer'
    ) -> 'SmartRequest':
        """
        设置Authorization
        
        Args:
            token: 认证token
            auth_type: 认证类型（Bearer, Basic等）
        
        Returns:
            返回自身，支持链式调用
        """
        self.default_headers['Authorization'] = f"{auth_type} {token}"
        return self


# 全局请求器实例
_global_requester = None


def get_smart_request(timeout: int = 30, max_retries: int = 3) -> SmartRequest:
    """
    获取全局智能请求器实例
    
    Args:
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
    
    Returns:
        SmartRequest实例
    """
    global _global_requester
    
    if _global_requester is None:
        _global_requester = SmartRequest(timeout=timeout, max_retries=max_retries)
    
    return _global_requester


def fetch_real_html(
    url: str,
    method: str = 'GET',
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    cookies: Optional[Dict] = None
) -> str:
    """
    获取真实HTML（便捷方法）
    
    Args:
        url: 请求URL
        method: HTTP方法
        params: URL参数
        data: 请求体
        headers: 自定义headers
        cookies: Cookies
    
    Returns:
        HTML字符串
    
    Raises:
        Exception: 如果请求失败
    """
    requester = get_smart_request()
    result = requester.fetch(
        url=url,
        method=method,
        params=params,
        data=data,
        headers=headers,
        cookies=cookies
    )
    
    if not result['success']:
        raise Exception(result.get('error', '请求失败'))
    
    if result['status_code'] != 200:
        raise Exception(f"HTTP状态码: {result['status_code']}")
    
    return result['html']
