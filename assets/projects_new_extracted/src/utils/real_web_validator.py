"""
真实网页验证器
强制要求访问真实网页，获取真实HTML，禁止任何Mock
确保所有分析都基于真实网页信息
"""

import requests
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re


class RealWebValidator:
    """真实网页验证器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def fetch_real_html(self, url: str) -> Dict[str, Any]:
        """
        获取真实HTML，绝对禁止Mock
        
        Args:
            url: 网页URL
        
        Returns:
            包含真实HTML和元数据的字典
        
        Raises:
            Exception: 如果无法获取真实网页
        """
        if not url:
            raise ValueError("URL不能为空！")
        
        print(f"🌐 正在访问真实网页: {url}")
        
        try:
            # 访问真实网页
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            # 检查响应状态
            if response.status_code != 200:
                raise Exception(f"网页访问失败，HTTP状态码: {response.status_code}")
            
            # 获取真实HTML
            html = response.text
            encoding = response.encoding or 'utf-8'
            
            # 验证HTML不为空
            if not html or len(html) < 100:
                raise Exception("获取的HTML内容为空或过短，可能无法访问真实网页")
            
            # 解析HTML验证有效性
            soup = BeautifulSoup(html, 'html.parser')
            if not soup.find('body'):
                print("⚠️  警告：HTML中未找到body标签，可能内容不完整")
            
            # 返回真实HTML
            return {
                'success': True,
                'url': url,
                'html': html,
                'encoding': encoding,
                'status_code': response.status_code,
                'size': len(html),
                'is_real': True,  # 标记这是真实网页
                'timestamp': __import__('time').time()
            }
            
        except requests.exceptions.Timeout:
            raise Exception(f"访问网页超时（{self.timeout}秒），请检查网络或URL是否正确")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到网页，请检查URL是否正确或网络连接")
        except Exception as e:
            raise Exception(f"获取真实网页失败: {str(e)}")
    
    def validate_selector_on_real_html(
        self,
        selector: str,
        html: str,
        expect_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        在真实HTML上验证选择器
        
        Args:
            selector: CSS选择器
            html: 真实HTML（必须是从真实网页获取的）
            expect_count: 期望匹配的数量（可选）
        
        Returns:
            验证结果
        
        Raises:
            Exception: 如果HTML不是真实的
        """
        # 验证HTML是真实的
        if not html or len(html) < 100:
            raise ValueError("HTML内容无效或过短，可能不是真实网页的HTML")
        
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 测试选择器
        try:
            elements = soup.select(selector)
        except Exception as e:
            return {
                'valid': False,
                'error': f'选择器语法错误: {str(e)}',
                'extracted_count': 0,
                'is_real_test': True
            }
        
        # 提取结果
        results = []
        for elem in elements[:10]:  # 只取前10个用于展示
            text = elem.get_text(strip=True)
            results.append({
                'text': text[:100],
                'tag': elem.name,
                'classes': elem.get('class', [])
            })
        
        # 验证数量
        is_valid = True
        validation_message = "✅ 选择器有效"
        
        if expect_count is not None:
            if len(elements) != expect_count:
                is_valid = False
                validation_message = f"❌ 数量不匹配: 期望{expect_count}个，实际{len(elements)}个"
        
        if len(elements) == 0:
            is_valid = False
            validation_message = "❌ 选择器未匹配到任何元素"
        
        return {
            'valid': is_valid,
            'selector': selector,
            'extracted_count': len(elements),
            'sample_results': results,
            'message': validation_message,
            'is_real_test': True,  # 标记这是在真实HTML上的测试
            'html_length': len(html)
        }
    
    def extract_from_real_html(
        self,
        selector: str,
        html: str,
        extract_attr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从真实HTML提取内容
        
        Args:
            selector: CSS选择器
            html: 真实HTML
            extract_attr: 提取的属性
        
        Returns:
            提取结果
        """
        # 验证HTML
        if not html:
            raise ValueError("HTML为空，无法提取内容")
        
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 选择元素
        elements = soup.select(selector)
        
        if not elements:
            return {
                'success': False,
                'message': '选择器未匹配到任何元素',
                'extracted': [],
                'count': 0,
                'is_real': True
            }
        
        # 提取内容
        extracted = []
        for elem in elements:
            if extract_attr:
                value = elem.get(extract_attr, '')
            else:
                value = elem.get_text(strip=True)
            
            extracted.append(value)
        
        return {
            'success': True,
            'message': f'成功提取 {len(extracted)} 个元素',
            'extracted': extracted[:20],  # 最多返回20个
            'count': len(extracted),
            'is_real': True,
            'selector': selector
        }
    
    def verify_knowledge_reference(
        self,
        selector: str,
        html: str,
        knowledge_source: str
    ) -> Dict[str, Any]:
        """
        验证知识库中的选择器在真实HTML上是否有效
        
        Args:
            selector: 知识库中的选择器
            html: 真实HTML
            knowledge_source: 知识来源
        
        Returns:
            验证结果
        """
        # 在真实HTML上测试
        test_result = self.validate_selector_on_real_html(selector, html)
        
        # 判断知识是否适用于当前网页
        result = {
            'selector': selector,
            'knowledge_source': knowledge_source,
            'applicable': test_result['valid'],
            'extracted_count': test_result['extracted_count'],
            'message': test_result['message'],
            'real_test': True,
            'recommendation': ''
        }
        
        if test_result['valid']:
            result['recommendation'] = f"✅ 知识库中的选择器在真实网页上有效，可以使用"
        else:
            result['recommendation'] = f"❌ 知识库中的选择器在真实网页上无效，需要重新分析"
        
        return result


# 全局验证器实例
_global_validator = None


def get_real_web_validator(timeout: int = 30) -> RealWebValidator:
    """获取全局真实网页验证器实例"""
    global _global_validator
    
    if _global_validator is None:
        _global_validator = RealWebValidator(timeout=timeout)
    
    return _global_validator


def fetch_real_html_strict(url: str) -> str:
    """
    严格获取真实HTML，禁止任何Mock
    
    Args:
        url: 网页URL
    
    Returns:
        真实HTML字符串
    
    Raises:
        Exception: 如果无法获取真实网页
    """
    validator = get_real_web_validator()
    result = validator.fetch_real_html(url)
    
    if not result['success']:
        raise Exception(result.get('error', '获取真实HTML失败'))
    
    return result['html']


def validate_real_html_required(html: str) -> bool:
    """
    验证HTML是否是真实的
    
    Args:
        html: HTML内容
    
    Returns:
        是否是真实HTML
    """
    if not html:
        return False
    
    # 真实HTML应该包含常见的HTML标签
    common_tags = ['<html', '<head', '<body', '<div']
    has_common_tags = any(tag in html.lower() for tag in common_tags)
    
    # 真实HTML应该有足够的内容
    has_content = len(html) > 500
    
    # 真实HTML不应该包含Mock标记
    no_mock = 'mock' not in html.lower() and 'example' not in html.lower()[:50]
    
    return has_common_tags and has_content and no_mock
