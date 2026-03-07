"""
规则验证和优化引擎
验证选择器和规则的正确性，优化性能，提供改进建议
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
from lxml import etree, html as lxml_html
from multi_mode_extractor import MultiModeExtractor


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: str  # error, warning, info
    type: str
    message: str
    location: str
    suggestion: str


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: str
    current_value: str
    suggested_value: str
    reason: str
    improvement: str


class RuleValidator:
    """规则验证器"""
    
    def __init__(self, html: str):
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.lxml_doc = lxml_html.fromstring(html)
        self.issues = []
        self.suggestions = []
    
    def validate_rule(
        self,
        rule_type: str,
        rule_value: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        验证规则
        
        Args:
            rule_type: 规则类型 (css/xpath/regex/replace/jsoup)
            rule_value: 规则值
            context: 上下文信息
        """
        context = context or {}
        
        validation_result = {
            'rule_type': rule_type,
            'rule_value': rule_value,
            'valid': True,
            'issues': [],
            'suggestions': [],
            'test_results': {}
        }
        
        # 根据规则类型验证
        if rule_type == 'css':
            validation_result.update(self._validate_css(rule_value, context))
        elif rule_type == 'xpath':
            validation_result.update(self._validate_xpath(rule_value, context))
        elif rule_type == 'regex':
            validation_result.update(self._validate_regex(rule_value, context))
        elif rule_type == 'replace':
            validation_result.update(self._validate_replace(rule_value, context))
        elif rule_type == 'jsoup':
            validation_result.update(self._validate_jsoup(rule_value, context))
        else:
            validation_result['valid'] = False
            validation_result['issues'].append({
                'severity': 'error',
                'type': 'unknown_type',
                'message': f'未知的规则类型: {rule_type}',
                'suggestion': '请使用支持的规则类型: css, xpath, regex, replace, jsoup'
            })
        
        # 生成优化建议
        if validation_result['valid']:
            optimization = self._generate_optimization(rule_type, rule_value, context)
            validation_result['suggestions'].extend(optimization)
        
        # 测试规则效果
        test_result = self._test_rule(rule_type, rule_value)
        validation_result['test_results'] = test_result
        
        # 综合判断有效性
        validation_result['valid'] = (
            validation_result['valid'] and
            not any(issue['severity'] == 'error' for issue in validation_result['issues']) and
            test_result.get('success', False)
        )
        
        return validation_result
    
    def _validate_css(self, selector: str, context: Dict) -> Dict:
        """验证CSS选择器"""
        result = {'valid': True, 'issues': []}
        
        # 基本语法检查
        if not selector or not selector.strip():
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'empty_selector',
                'message': 'CSS选择器不能为空',
                'suggestion': '请提供有效的CSS选择器'
            })
            return result
        
        # 检查语法错误
        try:
            elements = self.soup.select(selector)
        except Exception as e:
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'syntax_error',
                'message': f'CSS选择器语法错误: {str(e)}',
                'suggestion': '请检查选择器语法，确保使用正确的CSS选择器格式'
            })
            return result
        
        # 检查匹配结果
        if not elements:
            result['issues'].append({
                'severity': 'warning',
                'type': 'no_match',
                'message': '选择器未匹配到任何元素',
                'suggestion': '请检查选择器是否正确，或者尝试其他选择器'
            })
        elif len(elements) == 1:
            # 单个匹配，检查是否过于具体
            if len(selector) > 50:
                result['issues'].append({
                    'severity': 'info',
                    'type': 'too_specific',
                    'message': '选择器过于具体，可能不够通用',
                    'suggestion': '考虑简化选择器，提高通用性'
                })
        else:
            # 多个匹配，检查是否过于宽泛
            if len(elements) > 100:
                result['issues'].append({
                    'severity': 'warning',
                    'type': 'too_broad',
                    'message': f'选择器匹配了{len(elements)}个元素，可能过于宽泛',
                    'suggestion': '考虑添加更具体的限定条件'
                })
        
        # 检查选择器性能
        if selector.startswith('*'):
            result['issues'].append({
                'severity': 'warning',
                'type': 'performance',
                'message': '使用通配符选择器可能影响性能',
                'suggestion': '使用更具体的选择器替代通配符'
            })
        
        # 检查层级深度
        depth = selector.count('>') + selector.count(' ') + 1
        if depth > 5:
            result['issues'].append({
                'severity': 'info',
                'type': 'deep_nesting',
                'message': f'选择器层级深度为{depth}，可能影响性能',
                'suggestion': '考虑使用更平级的选择器或添加class/id'
            })
        
        return result
    
    def _validate_xpath(self, xpath: str, context: Dict) -> Dict:
        """验证XPath"""
        result = {'valid': True, 'issues': []}
        
        # 基本语法检查
        if not xpath or not xpath.strip():
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'empty_xpath',
                'message': 'XPath不能为空',
                'suggestion': '请提供有效的XPath表达式'
            })
            return result
        
        # 检查语法错误
        try:
            elements = self.lxml_doc.xpath(xpath)
        except Exception as e:
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'syntax_error',
                'message': f'XPath语法错误: {str(e)}',
                'suggestion': '请检查XPath语法，确保使用正确的XPath格式'
            })
            return result
        
        # 检查匹配结果
        if not elements:
            result['issues'].append({
                'severity': 'warning',
                'type': 'no_match',
                'message': 'XPath未匹配到任何元素',
                'suggestion': '请检查XPath是否正确'
            })
        
        # 检查使用//而非/
        if xpath.startswith('//') and xpath.count('//') > 2:
            result['issues'].append({
                'severity': 'info',
                'type': 'performance',
                'message': 'XPath中使用多个//可能影响性能',
                'suggestion': '考虑使用更精确的路径'
            })
        
        return result
    
    def _validate_regex(self, pattern: str, context: Dict) -> Dict:
        """验证正则表达式"""
        result = {'valid': True, 'issues': []}
        
        # 基本语法检查
        if not pattern or not pattern.strip():
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'empty_pattern',
                'message': '正则表达式不能为空',
                'suggestion': '请提供有效的正则表达式'
            })
            return result
        
        # 检查语法错误
        try:
            re.compile(pattern)
        except Exception as e:
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'syntax_error',
                'message': f'正则表达式语法错误: {str(e)}',
                'suggestion': '请检查正则表达式语法'
            })
            return result
        
        # 测试匹配
        matches = re.findall(pattern, self.html)
        if not matches:
            result['issues'].append({
                'severity': 'warning',
                'type': 'no_match',
                'message': '正则表达式未匹配到任何内容',
                'suggestion': '请检查正则表达式是否正确'
            })
        
        # 检查贪婪匹配
        if '.*' in pattern or '.+' in pattern:
            result['issues'].append({
                'severity': 'info',
                'type': 'greedy',
                'message': '正则表达式包含贪婪匹配',
                'suggestion': '考虑使用非贪婪匹配（.*?）'
            })
        
        return result
    
    def _validate_replace(self, rule_value: str, context: Dict) -> Dict:
        """验证替换规则"""
        result = {'valid': True, 'issues': []}
        
        # 检查格式
        parts = rule_value.split('@@')
        if len(parts) != 2:
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'invalid_format',
                'message': '替换规则格式错误，应使用: 模式@@替换值',
                'suggestion': '使用@@分隔模式和替换值'
            })
            return result
        
        pattern, replacement = parts
        
        # 验证正则部分
        try:
            re.compile(pattern)
        except Exception as e:
            result['valid'] = False
            result['issues'].append({
                'severity': 'error',
                'type': 'invalid_pattern',
                'message': f'替换规则中的模式无效: {str(e)}',
                'suggestion': '请检查正则表达式语法'
            })
            return result
        
        return result
    
    def _validate_jsoup(self, rule_value: str, context: Dict) -> Dict:
        """验证Jsoup规则（简化版）"""
        result = {'valid': True, 'issues': []}
        
        # Jsoup规则通常是CSS选择器
        return self._validate_css(rule_value, context)
    
    def _test_rule(self, rule_type: str, rule_value: str) -> Dict:
        """测试规则效果"""
        try:
            extractor = MultiModeExtractor(self.html)
            result = extractor.extract(
                selector=rule_value,
                method='auto',
                extract_all=True
            )
            
            return {
                'success': result.success,
                'confidence': result.confidence,
                'extracted_count': len(result.content) if isinstance(result.content, list) else 1,
                'sample_items': result.sample_items or []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_optimization(
        self,
        rule_type: str,
        rule_value: str,
        context: Dict
    ) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        
        if rule_type == 'css':
            # CSS优化建议
            if '#' in rule_value and '.' in rule_value:
                suggestions.append({
                    'type': 'performance',
                    'current': rule_value,
                    'suggested': rule_value.replace(' .', '#') if '#' in rule_value.split()[0] else rule_value,
                    'reason': '选择器混合使用id和class',
                    'improvement': '优先使用id选择器以提高性能'
                })
        
        elif rule_type == 'xpath':
            # XPath优化建议
            if rule_value.startswith('//'):
                suggestions.append({
                    'type': 'performance',
                    'current': rule_value,
                    'suggested': rule_value.replace('//', '/', 1),
                    'reason': '使用//从文档根搜索',
                    'improvement': '使用/指定精确路径提高性能'
                })
        
        elif rule_type == 'regex':
            # 正则优化建议
            if '.*' in rule_value:
                suggestions.append({
                    'type': 'accuracy',
                    'current': rule_value,
                    'suggested': rule_value.replace('.*', '.*?'),
                    'reason': '使用贪婪匹配',
                    'improvement': '使用非贪婪匹配提高精确度'
                })
        
        return suggestions


class RuleOptimizer:
    """规则优化器"""
    
    def __init__(self, html: str):
        self.validator = RuleValidator(html)
        self.optimization_history = []
    
    def optimize_rule(
        self,
        rule_type: str,
        rule_value: str,
        target_count: Optional[int] = None,
        auto_fix: bool = True
    ) -> Dict[str, Any]:
        """
        优化规则
        
        Args:
            rule_type: 规则类型
            rule_value: 规则值
            target_count: 目标匹配数量
            auto_fix: 是否自动修复
        """
        # 先验证规则
        validation = self.validator.validate_rule(rule_type, rule_value)
        
        optimization_result = {
            'original_rule': rule_value,
            'optimized_rule': rule_value,
            'validation': validation,
            'optimizations': [],
            'improvement': None
        }
        
        if not validation['valid'] or auto_fix:
            # 尝试优化
            optimized = self._apply_optimizations(
                rule_type,
                rule_value,
                validation,
                target_count
            )
            
            optimization_result['optimized_rule'] = optimized
            optimization_result['optimizations'] = self._get_applied_optimizations(
                rule_type,
                rule_value,
                optimized
            )
            
            # 重新验证优化后的规则
            if optimized != rule_value:
                new_validation = self.validator.validate_rule(rule_type, optimized)
                optimization_result['optimized_validation'] = new_validation
                
                # 计算改进
                original_count = validation['test_results'].get('extracted_count', 0)
                optimized_count = new_validation['test_results'].get('extracted_count', 0)
                
                if target_count:
                    improvement = abs(original_count - target_count) - abs(optimized_count - target_count)
                    optimization_result['improvement'] = improvement
        
        self.optimization_history.append(optimization_result)
        
        return optimization_result
    
    def _apply_optimizations(
        self,
        rule_type: str,
        rule_value: str,
        validation: Dict,
        target_count: Optional[int]
    ) -> str:
        """应用优化"""
        optimized = rule_value
        
        # 根据验证问题应用优化
        for issue in validation.get('issues', []):
            if issue['type'] == 'too_broad':
                # 添加更具体的限制
                optimized = self._make_more_specific(rule_type, optimized)
            elif issue['type'] == 'no_match':
                # 放宽限制
                optimized = self._make_more_general(rule_type, optimized)
        
        return optimized
    
    def _make_more_specific(self, rule_type: str, rule_value: str) -> str:
        """使规则更具体"""
        if rule_type == 'css':
            # 添加位置限制
            if not rule_value.endswith(':first-child'):
                return f"{rule_value}:first-child"
        elif rule_type == 'xpath':
            # 添加位置限制
            if not '[1]' in rule_value:
                return f"{rule_value}[1]"
        
        return rule_value
    
    def _make_more_general(self, rule_type: str, rule_value: str) -> str:
        """使规则更通用"""
        if rule_type == 'css':
            # 移除伪类
            rule_value = re.sub(r':\w+', '', rule_value)
            return rule_value
        elif rule_type == 'xpath':
            # 使用//而非/
            return rule_value.replace('/', '//', 1)
        
        return rule_value
    
    def _get_applied_optimizations(
        self,
        rule_type: str,
        original: str,
        optimized: str
    ) -> List[str]:
        """获取应用的优化"""
        optimizations = []
        
        if original != optimized:
            if ':first-child' in optimized:
                optimizations.append('添加:first-child限制')
            if '[1]' in optimized:
                optimizations.append('添加位置限制[1]')
            if ':' not in optimized and ':' in original:
                optimizations.append('移除伪类选择器')
            if '//' in optimized and '/' not in optimized.replace('//', ''):
                optimizations.append('使用相对路径')
        
        return optimizations
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """获取优化摘要"""
        if not self.optimization_history:
            return {
                'total_optimizations': 0,
                'successful_optimizations': 0,
                'avg_improvement': 0
            }
        
        successful = sum(
            1 for opt in self.optimization_history
            if opt.get('improvement', 0) > 0
        )
        
        improvements = [
            opt.get('improvement', 0)
            for opt in self.optimization_history
            if opt.get('improvement') is not None
        ]
        
        return {
            'total_optimizations': len(self.optimization_history),
            'successful_optimizations': successful,
            'avg_improvement': sum(improvements) / len(improvements) if improvements else 0,
            'optimization_details': self.optimization_history
        }
