"""
多模式提取引擎
支持CSS选择器、XPath、正则表达式、JSONPath等多种提取方式
智能选择最优提取策略，提供准确的内容提取
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from bs4 import BeautifulSoup
from lxml import etree, html as lxml_html


@dataclass
class ExtractionResult:
    """提取结果"""
    content: Union[str, List[str]]
    method: str
    selector: str
    success: bool
    confidence: float
    error_message: Optional[str] = None
    sample_items: List[str] = None
    extracted_count: int = 0


class MultiModeExtractor:
    """多模式提取器"""
    
    def __init__(self, html: str):
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.lxml_doc = lxml_html.fromstring(html)
        self.results = {}
    
    def extract(
        self,
        selector: str,
        method: str = 'auto',
        extract_attr: str = None,
        extract_all: bool = True
    ) -> ExtractionResult:
        """
        提取内容
        
        Args:
            selector: 选择器（CSS、XPath或正则）
            method: 提取方法 (css/xpath/regex/auto)
            extract_attr: 提取的属性名（None表示提取文本）
            extract_all: 是否提取所有匹配项
        """
        # 自动检测方法
        if method == 'auto':
            method = self._detect_method(selector)
        
        # 根据方法提取
        if method == 'css':
            return self._extract_css(selector, extract_attr, extract_all)
        elif method == 'xpath':
            return self._extract_xpath(selector, extract_attr, extract_all)
        elif method == 'regex':
            return self._extract_regex(selector, extract_all)
        elif method == 'json':
            return self._extract_json(selector, extract_attr)
        else:
            return ExtractionResult(
                content='',
                method=method,
                selector=selector,
                success=False,
                confidence=0.0,
                error_message=f'不支持的提取方法: {method}',
                extracted_count=0
            )
    
    def _detect_method(self, selector: str) -> str:
        """自动检测提取方法"""
        # XPath检测
        if selector.startswith('//') or selector.startswith('/'):
            return 'xpath'
        
        # 正则检测
        if selector.startswith('regex:') or selector.startswith('re:'):
            return 'regex'
        
        # JSONPath检测
        if selector.startswith('json:') or selector.startswith('jsonPath:'):
            return 'json'
        
        # 默认CSS
        return 'css'
    
    def _extract_css(
        self,
        selector: str,
        extract_attr: str = None,
        extract_all: bool = True
    ) -> ExtractionResult:
        """使用CSS选择器提取"""
        try:
            if extract_all:
                elements = self.soup.select(selector)
            else:
                element = self.soup.select_one(selector)
                elements = [element] if element else []
            
            if not elements:
                return ExtractionResult(
                    content=[],
                    method='css',
                    selector=selector,
                    success=True,
                    confidence=0.0,
                    extracted_count=0
                )

            # 提取内容
            if extract_attr:
                contents = [elem.get(extract_attr, '') for elem in elements if elem.get(extract_attr)]
            else:
                contents = [elem.get_text(strip=True) for elem in elements]

            # 过滤空内容
            contents = [c for c in contents if c]
            extracted_count = len(contents)

            return ExtractionResult(
                content=contents if extract_all else (contents[0] if contents else ''),
                method='css',
                selector=selector,
                success=True,
                confidence=min(extracted_count / max(1, len(elements)), 1.0),
                sample_items=contents[:5],
                extracted_count=extracted_count
            )
            
        except Exception as e:
            return ExtractionResult(
                content=[],
                method='css',
                selector=selector,
                success=False,
                confidence=0.0,
                error_message=str(e)
            )
    
    def _extract_xpath(
        self,
        selector: str,
        extract_attr: str = None,
        extract_all: bool = True
    ) -> ExtractionResult:
        """使用XPath提取"""
        try:
            if extract_all:
                elements = self.lxml_doc.xpath(selector)
            else:
                elements = self.lxml_doc.xpath(f'{selector}[1]')
            
            if not elements:
                return ExtractionResult(
                    content=[],
                    method='xpath',
                    selector=selector,
                    success=True,
                    confidence=0.0,
                    extracted_count=0
                )

            # 提取内容
            if extract_attr:
                contents = [elem.get(extract_attr, '') for elem in elements if hasattr(elem, 'get')]
            else:
                contents = [elem.text_content().strip() for elem in elements if hasattr(elem, 'text_content')]

            # 过滤空内容
            contents = [c for c in contents if c]
            extracted_count = len(contents)

            return ExtractionResult(
                content=contents if extract_all else (contents[0] if contents else ''),
                method='xpath',
                selector=selector,
                success=True,
                confidence=min(extracted_count / max(1, len(elements)), 1.0),
                sample_items=contents[:5],
                extracted_count=extracted_count
            )
            
        except Exception as e:
            return ExtractionResult(
                content=[],
                method='xpath',
                selector=selector,
                success=False,
                confidence=0.0,
                error_message=str(e)
            )
    
    def _extract_regex(
        self,
        selector: str,
        extract_all: bool = True
    ) -> ExtractionResult:
        """使用正则表达式提取"""
        try:
            # 移除regex:前缀
            pattern = selector.replace('regex:', '').replace('re:', '')
            
            matches = re.findall(pattern, self.html)
            
            if not matches:
                return ExtractionResult(
                    content=[],
                    method='regex',
                    selector=pattern,
                    success=True,
                    confidence=0.0,
                    extracted_count=0
                )

            # 处理匹配结果
            if extract_all:
                contents = matches
                extracted_count = len(matches) if isinstance(matches, list) else 1
            else:
                contents = matches[0]
                extracted_count = 1

            return ExtractionResult(
                content=contents,
                method='regex',
                selector=pattern,
                success=True,
                confidence=1.0,
                sample_items=matches[:5] if isinstance(matches, list) else [str(matches)],
                extracted_count=extracted_count
            )
            
        except Exception as e:
            return ExtractionResult(
                content=[],
                method='regex',
                selector=selector,
                success=False,
                confidence=0.0,
                error_message=str(e)
            )
    
    def _extract_json(
        self,
        selector: str,
        extract_attr: str = None
    ) -> ExtractionResult:
        """从JSON数据提取"""
        try:
            # 移除json:前缀
            json_path = selector.replace('json:', '').replace('jsonPath:', '')
            
            # 查找JSON数据
            json_pattern = r'<script[^>]*>\s*(var\s+\w+\s*=\s*)?({.*?})\s*(;)?\s*</script>'
            json_matches = re.findall(json_pattern, self.html, re.DOTALL)
            
            if not json_matches:
                return ExtractionResult(
                    content='',
                    method='json',
                    selector=json_path,
                    success=False,
                    confidence=0.0,
                    error_message='未找到JSON数据'
                )
            
            # 解析JSON
            json_str = json_matches[0][1]
            data = json.loads(json_str)
            
            # 简化的JSONPath提取（实际应用中可以使用jsonpath库）
            if '.' in json_path:
                keys = json_path.split('.')
                for key in keys:
                    if key.isdigit():
                        data = data[int(key)]
                    else:
                        data = data.get(key, '')
            
            return ExtractionResult(
                content=str(data),
                method='json',
                selector=json_path,
                success=True,
                confidence=1.0,
                sample_items=[str(data)[:50]],
                extracted_count=1
            )
            
        except Exception as e:
            return ExtractionResult(
                content='',
                method='json',
                selector=selector,
                success=False,
                confidence=0.0,
                error_message=str(e)
            )


class SmartExtractionStrategy:
    """智能提取策略"""
    
    def __init__(self, html: str):
        self.html = html
        self.extractor = MultiModeExtractor(html)
        self.strategy_results = {}
    
    def extract_with_strategy(
        self,
        element_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        使用智能策略提取
        
        Args:
            element_type: 元素类型 (title/list/content/image/link)
            context: 上下文信息
        """
        context = context or {}
        
        # 根据元素类型选择策略
        if element_type == 'title':
            return self._extract_title_strategy(context)
        elif element_type == 'list':
            return self._extract_list_strategy(context)
        elif element_type == 'content':
            return self._extract_content_strategy(context)
        elif element_type == 'image':
            return self._extract_image_strategy(context)
        elif element_type == 'link':
            return self._extract_link_strategy(context)
        else:
            return self._extract_generic_strategy(context)
    
    def _extract_title_strategy(self, context: Dict) -> Dict[str, Any]:
        """标题提取策略"""
        strategies = [
            # 策略1: h1标签
            {
                'name': 'h1标签提取',
                'method': 'css',
                'selector': 'h1',
                'extract_attr': None
            },
            # 策略2: class包含title的元素
            {
                'name': 'class包含title',
                'method': 'css',
                'selector': '[class*="title"]',
                'extract_attr': None
            },
            # 策略3: 正则匹配title标签
            {
                'name': '正则匹配title',
                'method': 'regex',
                'selector': r'<title>(.*?)</title>',
                'extract_attr': None
            },
            # 策略4: id包含title的元素
            {
                'name': 'id包含title',
                'method': 'css',
                'selector': '[id*="title"]',
                'extract_attr': None
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _extract_list_strategy(self, context: Dict) -> Dict[str, Any]:
        """列表提取策略"""
        strategies = [
            # 策略1: ul列表
            {
                'name': 'ul列表提取',
                'method': 'css',
                'selector': 'ul li a',
                'extract_attr': 'href'
            },
            # 策略2: class包含list或chapter的元素
            {
                'name': 'class包含list/chapter',
                'method': 'css',
                'selector': '[class*="list"] a, [class*="chapter"] a',
                'extract_attr': 'href'
            },
            # 策略3: XPath路径提取
            {
                'name': 'XPath路径提取',
                'method': 'xpath',
                'selector': '//ul//a | //ol//a',
                'extract_attr': 'href'
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _extract_content_strategy(self, context: Dict) -> Dict[str, Any]:
        """正文提取策略"""
        strategies = [
            # 策略1: class包含content的元素
            {
                'name': 'class包含content',
                'method': 'css',
                'selector': '[class*="content"]',
                'extract_attr': None
            },
            # 策略2: id包含content的元素
            {
                'name': 'id包含content',
                'method': 'css',
                'selector': '[id*="content"]',
                'extract_attr': None
            },
            # 策略3: article标签
            {
                'name': 'article标签',
                'method': 'css',
                'selector': 'article',
                'extract_attr': None
            },
            # 策略4: main标签
            {
                'name': 'main标签',
                'method': 'css',
                'selector': 'main',
                'extract_attr': None
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _extract_image_strategy(self, context: Dict) -> Dict[str, Any]:
        """图片提取策略"""
        strategies = [
            # 策略1: class包含cover的图片
            {
                'name': 'class包含cover',
                'method': 'css',
                'selector': 'img[class*="cover"]',
                'extract_attr': 'src'
            },
            # 策略2: 第一个img标签
            {
                'name': '第一个图片',
                'method': 'css',
                'selector': 'img:first-of-type',
                'extract_attr': 'src'
            },
            # 策略3: data-src属性
            {
                'name': 'data-src属性',
                'method': 'css',
                'selector': 'img[data-src]',
                'extract_attr': 'data-src'
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _extract_link_strategy(self, context: Dict) -> Dict[str, Any]:
        """链接提取策略"""
        strategies = [
            # 策略1: class包含item或link的链接
            {
                'name': 'class包含item/link',
                'method': 'css',
                'selector': 'a[class*="item"], a[class*="link"]',
                'extract_attr': 'href'
            },
            # 策略2: 所有a标签
            {
                'name': '所有a标签',
                'method': 'css',
                'selector': 'a',
                'extract_attr': 'href'
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _extract_generic_strategy(self, context: Dict) -> Dict[str, Any]:
        """通用提取策略"""
        strategies = [
            # 策略1: CSS选择器
            {
                'name': 'CSS选择器',
                'method': 'css',
                'selector': context.get('selector', '*'),
                'extract_attr': context.get('attr')
            },
            # 策略2: XPath
            {
                'name': 'XPath',
                'method': 'xpath',
                'selector': context.get('xpath', '//*'),
                'extract_attr': context.get('attr')
            }
        ]
        
        return self._try_strategies(strategies)
    
    def _try_strategies(self, strategies: List[Dict]) -> Dict[str, Any]:
        """尝试多个策略，返回最优结果"""
        results = []
        
        for strategy in strategies:
            result = self.extractor.extract(
                selector=strategy['selector'],
                method=strategy['method'],
                extract_attr=strategy.get('extract_attr'),
                extract_all=True
            )
            
            if result.success and result.confidence > 0:
                results.append({
                    'strategy': strategy['name'],
                    'selector': result.selector,
                    'method': result.method,
                    'content': result.content,
                    'confidence': result.confidence,
                    'sample_items': result.sample_items,
                    'item_count': len(result.content) if isinstance(result.content, list) else 1
                })
        
        # 按置信度排序
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'best_result': results[0] if results else None,
            'all_results': results,
            'strategy_count': len(strategies),
            'success_count': len(results)
        }
    
    def validate_extraction(
        self,
        selector: str,
        expected_count: Optional[int] = None,
        expected_content: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        验证提取结果
        
        Args:
            selector: 选择器
            expected_count: 期望的结果数量
            expected_content: 期望包含的内容列表
        """
        result = self.extractor.extract(selector, method='auto')
        
        validation = {
            'selector': selector,
            'success': result.success,
            'confidence': result.confidence,
            'extracted_count': len(result.content) if isinstance(result.content, list) else 1,
            'extracted_content': result.content[:10] if isinstance(result.content, list) else [result.content],
            'validations': []
        }
        
        # 验证数量
        if expected_count is not None:
            extracted_count = validation['extracted_count']
            if extracted_count == expected_count:
                validation['validations'].append({
                    'type': 'count',
                    'passed': True,
                    'message': f'✓ 数量匹配: {extracted_count} == {expected_count}'
                })
            else:
                validation['validations'].append({
                    'type': 'count',
                    'passed': False,
                    'message': f'✗ 数量不匹配: {extracted_count} != {expected_count}'
                })
        
        # 验证内容
        if expected_content:
            extracted = validation['extracted_content']
            extracted_text = ' '.join(str(c) for c in extracted).lower()
            
            for expected in expected_content:
                if expected.lower() in extracted_text:
                    validation['validations'].append({
                        'type': 'content',
                        'passed': True,
                        'message': f'✓ 包含期望内容: "{expected}"'
                    })
                else:
                    validation['validations'].append({
                        'type': 'content',
                        'passed': False,
                        'message': f'✗ 缺少期望内容: "{expected}"'
                    })
        
        # 整体验证结果
        validation['all_passed'] = all(v['passed'] for v in validation['validations'])
        
        return validation
