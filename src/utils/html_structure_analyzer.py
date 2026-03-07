"""
HTML结构智能解析引擎 - AI驱动版
使用AI分析整个HTML结构，结合知识库生成正确的选择器
"""

from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ElementInfo:
    """元素信息"""
    selector: str
    tag: str
    classes: List[str]
    text: str
    text_length: int
    has_link: bool
    link_href: str
    child_count: int
    depth: int
    position: int
    confidence: float


class HTMLStructureAnalyzer:
    """HTML结构分析器 - AI驱动版"""
    
    def __init__(self, html: str, use_ai: bool = True):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.html = html
        self.use_ai = use_ai
        self.elements_info = []
        
    def analyze_structure(self) -> Dict[str, Any]:
        """分析整个HTML结构"""
        if self.use_ai:
            return self._ai_analyze_structure()
        else:
            return self._rule_analyze_structure()
    
    def _ai_analyze_structure(self) -> Dict[str, Any]:
        """
        使用AI分析整个HTML结构
        
        这个方法会将整个HTML交给AI，让AI：
        1. 分析HTML的整体结构
        2. 识别关键元素
        3. 推断CSS选择器
        4. 结合知识库生成推荐
        """
        # 获取HTML的关键信息
        html_summary = self._get_html_summary()
        
        # 使用AI分析（这里返回摘要，实际分析由LLM完成）
        return {
            'analysis_method': 'ai',
            'html_summary': html_summary,
            'suggestion': '请使用LLM工具分析此HTML',
            'html_sample': self._get_html_sample(2000)  # 前2000字符的HTML样本
        }
    
    def _rule_analyze_structure(self) -> Dict[str, Any]:
        """使用规则分析HTML结构（备用方案）"""
        return {
            'analysis_method': 'rule',
            'page_type': self._detect_page_type(),
            'key_elements': self._identify_key_elements(),
            'content_density': self._calculate_content_density()
        }
    
    def _get_html_summary(self) -> Dict[str, Any]:
        """获取HTML摘要信息"""
        return {
            'total_elements': len(list(self.soup.find_all())),
            'div_count': len(self.soup.find_all('div')),
            'link_count': len(self.soup.find_all('a')),
            'image_count': len(self.soup.find_all('img')),
            'title_count': len(self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'list_count': len(self.soup.find_all(['ul', 'ol'])),
            'html_size': len(self.html)
        }
    
    def _get_html_sample(self, max_length: int = 2000) -> str:
        """获取HTML样本（用于AI分析）"""
        # 获取body部分，如果不存在则返回整个HTML
        body = self.soup.find('body')
        if body:
            sample = str(body)
        else:
            sample = self.html
        
        # 截取前max_length个字符
        if len(sample) > max_length:
            sample = sample[:max_length]
        
        return sample
    
    def _detect_page_type(self) -> str:
        """检测页面类型"""
        page_signals = {
            'search': self._count_signals(['search', 'query', 'keyword']),
            'detail': self._count_signals(['book', 'novel', 'detail', 'info']),
            'toc': self._count_signals(['chapter', 'catalog', 'toc', 'list']),
            'content': self._count_signals(['content', 'read', 'chapter', 'article'])
        }
        
        max_signal = max(page_signals.items(), key=lambda x: x[1])
        return max_signal[0] if max_signal[1] > 0 else 'unknown'
    
    def _count_signals(self, keywords: List[str]) -> int:
        """计算关键词信号"""
        count = 0
        html_lower = self.html.lower()
        
        # 检查class属性
        for elem in self.soup.find_all(class_=True):
            for class_name in elem.get('class', []):
                if any(kw in class_name.lower() for kw in keywords):
                    count += 1
        
        # 检查id属性
        for elem in self.soup.find_all(id=True):
            elem_id = elem.get('id', '').lower()
            if any(kw in elem_id for kw in keywords):
                count += 2  # id权重更高
        
        # 检查文本内容
        for text in self.soup.stripped_strings:
            if any(kw in text.lower() for kw in keywords):
                count += 1
        
        return count
    
    def _identify_key_elements(self) -> Dict[str, List[ElementInfo]]:
        """识别关键元素"""
        elements = {
            'titles': self._find_titles(),
            'lists': self._find_lists(),
            'containers': self._find_containers(),
            'images': self._find_images(),
            'links': self._find_links()
        }
        
        return elements
    
    def _find_titles(self) -> List[ElementInfo]:
        """查找标题元素"""
        titles = []
        title_tags = ['h1', 'h2', 'h3']
        
        for i, tag in enumerate(title_tags):
            for elem in self.soup.find_all(tag):
                text = elem.get_text(strip=True)
                if text:
                    info = ElementInfo(
                        selector=self._generate_selector(elem),
                        tag=tag,
                        classes=elem.get('class', []),
                        text=text,
                        text_length=len(text),
                        has_link=False,
                        link_href='',
                        child_count=len(list(elem.children)),  # 修复：转换为list
                        depth=self._get_depth(elem),
                        position=i,
                        confidence=self._calculate_title_confidence(elem)
                    )
                    titles.append(info)
        
        return sorted(titles, key=lambda x: x.confidence, reverse=True)[:10]
    
    def _find_lists(self) -> List[ElementInfo]:
        """查找列表元素"""
        lists = []
        list_tags = ['ul', 'ol']
        
        for elem in self.soup.find_all(list_tags):
            items = elem.find_all('li', recursive=False)
            if len(items) >= 3:  # 至少3个列表项
                info = ElementInfo(
                    selector=self._generate_selector(elem),
                    tag=elem.name,
                    classes=elem.get('class', []),
                    text=f"{len(items)} items",
                    text_length=0,
                    has_link=False,
                    link_href='',
                    child_count=len(items),
                    depth=self._get_depth(elem),
                    position=0,
                    confidence=self._calculate_list_confidence(elem)
                )
                lists.append(info)
        
        return sorted(lists, key=lambda x: x.confidence, reverse=True)[:10]
    
    def _find_containers(self) -> List[ElementInfo]:
        """查找容器元素"""
        containers = []
        
        for elem in self.soup.find_all(['div', 'section', 'article', 'main']):
            # 转换children为list
            children = list(elem.children)
            child_count = len(children)
            
            if child_count > 0:
                info = ElementInfo(
                    selector=self._generate_selector(elem),
                    tag=elem.name,
                    classes=elem.get('class', []),
                    text=elem.get_text(strip=True)[:100],
                    text_length=len(elem.get_text(strip=True)),
                    has_link=False,
                    link_href='',
                    child_count=child_count,  # 修复：已经转换为list
                    depth=self._get_depth(elem),
                    position=0,
                    confidence=self._calculate_container_confidence(elem)
                )
                containers.append(info)
        
        return sorted(containers, key=lambda x: x.confidence, reverse=True)[:10]
    
    def _find_images(self) -> List[ElementInfo]:
        """查找图片元素"""
        images = []
        
        for elem in self.soup.find_all('img', src=True):
            info = ElementInfo(
                selector=self._generate_selector(elem),
                tag='img',
                classes=elem.get('class', []),
                text=elem.get('alt', ''),
                text_length=len(elem.get('alt', '')),
                has_link=False,
                link_href=elem.get('src', ''),
                child_count=0,
                depth=self._get_depth(elem),
                position=0,
                confidence=self._calculate_image_confidence(elem)
            )
            images.append(info)
        
        return sorted(images, key=lambda x: x.confidence, reverse=True)[:10]
    
    def _find_links(self) -> List[ElementInfo]:
        """查找链接元素"""
        links = []
        
        for elem in self.soup.find_all('a', href=True):
            text = elem.get_text(strip=True)
            if text:
                info = ElementInfo(
                    selector=self._generate_selector(elem),
                    tag='a',
                    classes=elem.get('class', []),
                    text=text,
                    text_length=len(text),
                    has_link=True,
                    link_href=elem.get('href', ''),
                    child_count=len(list(elem.children)),  # 修复：转换为list
                    depth=self._get_depth(elem),
                    position=0,
                    confidence=self._calculate_link_confidence(elem)
                )
                links.append(info)
        
        return sorted(links, key=lambda x: x.confidence, reverse=True)[:10]
    
    def _generate_selector(self, elem) -> str:
        """生成CSS选择器"""
        selector = elem.name
        
        # 添加class
        if elem.get('class'):
            classes = '.'.join(elem.get('class', []))
            selector += f'.{classes}'
        
        # 添加id
        if elem.get('id'):
            selector += f"#{elem.get('id')}"
        
        return selector
    
    def _get_depth(self, elem) -> int:
        """获取元素深度"""
        depth = 0
        parent = elem.parent
        while parent and parent.name:
            depth += 1
            parent = parent.parent
        return depth
    
    def _calculate_title_confidence(self, elem) -> float:
        """计算标题置信度"""
        confidence = 0.5
        
        # 标签权重
        tag_weights = {'h1': 1.0, 'h2': 0.9, 'h3': 0.8}
        confidence += tag_weights.get(elem.name, 0)
        
        # 文本长度
        text_length = len(elem.get_text(strip=True))
        if 5 <= text_length <= 50:
            confidence += 0.2
        elif 50 < text_length <= 100:
            confidence += 0.1
        
        # class名称
        classes = ' '.join(elem.get('class', [])).lower()
        for kw in ['title', 'name', 'book']:
            if kw in classes:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_list_confidence(self, elem) -> float:
        """计算列表置信度"""
        confidence = 0.5
        
        # 标签权重
        tag_weights = {'ul': 0.8, 'ol': 0.9, 'dl': 0.7}
        confidence += tag_weights.get(elem.name, 0)
        
        # class名称
        classes = ' '.join(elem.get('class', [])).lower()
        for kw in ['list', 'chapter', 'item', 'catalog']:
            if kw in classes:
                confidence += 0.1
        
        # 列表项数量
        items = elem.find_all('li', recursive=False)
        if len(items) >= 10:
            confidence += 0.2
        elif len(items) >= 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_container_confidence(self, elem) -> float:
        """计算容器置信度"""
        confidence = 0.3
        
        # 文本长度
        text_length = len(elem.get_text(strip=True))
        if text_length > 200:
            confidence += 0.2
        elif text_length > 100:
            confidence += 0.1
        
        # class名称
        classes = ' '.join(elem.get('class', [])).lower()
        for kw in ['content', 'info', 'detail', 'main']:
            if kw in classes:
                confidence += 0.2
        
        # 子元素数量
        children = list(elem.children)
        if len(children) > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_image_confidence(self, elem) -> float:
        """计算图片置信度"""
        confidence = 0.5
        
        # src属性
        src = elem.get('src', '')
        if src:
            confidence += 0.3
        
        # alt属性
        alt = elem.get('alt', '')
        if alt:
            confidence += 0.1
        
        # class名称
        classes = ' '.join(elem.get('class', [])).lower()
        for kw in ['cover', 'image', 'img', 'pic']:
            if kw in classes:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_link_confidence(self, elem) -> float:
        """计算链接置信度"""
        confidence = 0.5
        
        # href属性
        href = elem.get('href', '')
        if href:
            confidence += 0.2
        
        # 文本长度
        text_length = len(elem.get_text(strip=True))
        if 2 <= text_length <= 50:
            confidence += 0.2
        
        # class名称
        classes = ' '.join(elem.get('class', [])).lower()
        for kw in ['link', 'chapter', 'item']:
            if kw in classes:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_content_density(self) -> Dict[str, float]:
        """计算内容密度"""
        total_text = len(self.soup.get_text(strip=True))
        total_elements = len(list(self.soup.find_all()))
        
        if total_elements == 0:
            return {'text_ratio': 0.0, 'avg_text_per_element': 0.0}
        
        return {
            'text_ratio': total_text / len(self.html) if self.html else 0,
            'avg_text_per_element': total_text / total_elements
        }
    
    def _build_structure_tree(self) -> Dict[str, Any]:
        """构建结构树"""
        return {
            'depth': self._get_max_depth(),
            'branches': self._count_branches()
        }
    
    def _get_max_depth(self) -> int:
        """获取最大深度"""
        max_depth = 0
        for elem in self.soup.find_all():
            depth = self._get_depth(elem)
            if depth > max_depth:
                max_depth = depth
        return max_depth
    
    def _count_branches(self) -> int:
        """计算分支数"""
        return len(self.soup.find_all(lambda tag: len(list(tag.children)) > 1))
    
    def _identify_semantic_regions(self) -> List[Dict[str, Any]]:
        """识别语义区域"""
        regions = []
        
        semantic_tags = ['header', 'main', 'footer', 'nav', 'article', 'section', 'aside']
        for elem in self.soup.find_all(semantic_tags):
            regions.append({
                'tag': elem.name,
                'selector': self._generate_selector(elem),
                'text': elem.get_text(strip=True)[:100]
            })
        
        return regions
    
    def _analyze_navigation(self) -> Dict[str, Any]:
        """分析导航结构"""
        nav_elements = self.soup.find_all('nav')
        return {
            'nav_count': len(nav_elements),
            'has_nav': len(nav_elements) > 0
        }
