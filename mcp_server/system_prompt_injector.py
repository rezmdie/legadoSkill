"""
MCP Server System Prompt Injector Module
自动检索并加载系统级指令，将其作为关键上下文信息注入到AI会话中
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import re

from .exceptions import ConfigError
from .logger import get_logger


@dataclass
class SystemPrompt:
    """系统提示词数据结构"""
    content: str
    path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    last_modified: Optional[float] = None


@dataclass
class PromptContext:
    """提示词上下文"""
    system_prompt: SystemPrompt
    tool_descriptions: List[str] = field(default_factory=list)
    operational_params: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    scope: Dict[str, Any] = field(default_factory=dict)


class SystemPromptInjector:
    """系统提示词注入器"""
    
    def __init__(self, prompt_path: Optional[str] = None):
        """初始化系统提示词注入器
        
        Args:
            prompt_path: 系统提示词文件路径，默认为config/system/prompt.md
        """
        self.prompt_path = Path(prompt_path) if prompt_path else Path("config/system/prompt.md")
        self.system_prompt: Optional[SystemPrompt] = None
        self.logger = get_logger("prompt_injector")
        self._cache: Dict[str, SystemPrompt] = {}
        self._watchers: List[asyncio.Task] = []
    
    async def load(self) -> SystemPrompt:
        """加载系统提示词文件
        
        Returns:
            SystemPrompt实例
            
        Raises:
            ConfigError: 提示词文件不存在或读取失败
        """
        try:
            if not self.prompt_path.exists():
                self.logger.warning(f"System prompt file not found: {self.prompt_path}")
                # 创建默认提示词
                self.system_prompt = self._create_default_prompt()
                return self.system_prompt
            
            self.logger.info(f"Loading system prompt from: {self.prompt_path}")
            
            # 读取文件内容
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析元数据（从YAML frontmatter或注释中提取）
            metadata = self._parse_metadata(content)
            
            # 获取文件修改时间
            last_modified = self.prompt_path.stat().st_mtime
            
            # 创建SystemPrompt对象
            self.system_prompt = SystemPrompt(
                content=content,
                path=str(self.prompt_path),
                metadata=metadata,
                version=metadata.get("version", "1.0"),
                last_modified=last_modified
            )
            
            # 缓存提示词
            self._cache[str(self.prompt_path)] = self.system_prompt
            
            self.logger.info(f"System prompt loaded successfully (version: {self.system_prompt.version})")
            return self.system_prompt
            
        except Exception as e:
            raise ConfigError(f"Failed to load system prompt: {e}")
    
    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """从提示词内容中解析元数据
        
        Args:
            content: 提示词内容
            
        Returns:
            元数据字典
        """
        metadata = {}
        
        # 尝试解析YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        # 尝试解析注释中的元数据
        comment_pattern = r'<!--\s*(\w+):\s*(.*?)\s*-->'
        for match in re.finditer(comment_pattern, content):
            metadata[match.group(1)] = match.group(2)
        
        return metadata
    
    def _create_default_prompt(self) -> SystemPrompt:
        """创建默认系统提示词
        
        Returns:
            默认SystemPrompt实例
        """
        default_content = """# System Instructions

You are an AI assistant with access to various tools through the Model Context Protocol (MCP).

## Operational Parameters

- Tool execution timeout: 30 seconds
- Maximum retry attempts: 3
- Concurrent tool calls: Enabled
- Error handling: Automatic

## Scope Definition

You have access to the following tool categories:
- Python tools: Execute Python code and scripts
- Google API services: Access Google services
- Custom adapters: Extended functionality through adapters

## Constraints

1. Always validate tool parameters before execution
2. Handle errors gracefully and provide meaningful feedback
3. Respect rate limits and timeouts
4. Log all tool calls for debugging purposes
5. Return results in a structured format

## Best Practices

- Use tools efficiently and minimize unnecessary calls
- Cache results when appropriate
- Provide clear explanations of tool usage
- Handle edge cases and unexpected responses
"""
        
        return SystemPrompt(
            content=default_content,
            path="default",
            metadata={"version": "1.0", "generated": True},
            version="1.0"
        )
    
    async def reload(self) -> SystemPrompt:
        """重新加载系统提示词
        
        Returns:
            重新加载的SystemPrompt实例
        """
        self.logger.info("Reloading system prompt...")
        self.system_prompt = await self.load()
        return self.system_prompt
    
    def get(self) -> Optional[SystemPrompt]:
        """获取当前系统提示词
        
        Returns:
            当前SystemPrompt实例，如果未加载则返回None
        """
        return self.system_prompt
    
    def build_context(
        self,
        tool_descriptions: Optional[List[str]] = None,
        operational_params: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
        scope: Optional[Dict[str, Any]] = None
    ) -> PromptContext:
        """构建完整的提示词上下文
        
        Args:
            tool_descriptions: 工具描述列表
            operational_params: 运营参数
            constraints: 约束条件列表
            scope: 范围定义
            
        Returns:
            PromptContext实例
        """
        if not self.system_prompt:
            raise ConfigError("System prompt not loaded")
        
        return PromptContext(
            system_prompt=self.system_prompt,
            tool_descriptions=tool_descriptions or [],
            operational_params=operational_params or {},
            constraints=constraints or [],
            scope=scope or {}
        )
    
    def format_for_injection(self, context: Optional[PromptContext] = None) -> str:
        """格式化提示词以便注入到AI会话中
        
        Args:
            context: 提示词上下文，如果为None则使用当前系统提示词
            
        Returns:
            格式化后的提示词字符串
        """
        if context is None:
            if not self.system_prompt:
                return ""
            context = PromptContext(system_prompt=self.system_prompt)
        
        # 构建完整的提示词
        parts = []
        
        # 系统提示词
        parts.append(context.system_prompt.content)
        
        # 工具描述
        if context.tool_descriptions:
            parts.append("\n## Available Tools\n")
            for desc in context.tool_descriptions:
                parts.append(f"- {desc}\n")
        
        # 运营参数
        if context.operational_params:
            parts.append("\n## Operational Parameters\n")
            for key, value in context.operational_params.items():
                parts.append(f"- {key}: {value}\n")
        
        # 约束条件
        if context.constraints:
            parts.append("\n## Constraints\n")
            for constraint in context.constraints:
                parts.append(f"- {constraint}\n")
        
        # 范围定义
        if context.scope:
            parts.append("\n## Scope\n")
            for key, value in context.scope.items():
                parts.append(f"- {key}: {value}\n")
        
        return "\n".join(parts)
    
    def extract_sections(self, content: Optional[str] = None) -> Dict[str, str]:
        """从提示词中提取各个章节
        
        Args:
            content: 提示词内容，如果为None则使用当前系统提示词
            
        Returns:
            章节字典，键为章节名称，值为章节内容
        """
        if content is None:
            if not self.system_prompt:
                return {}
            content = self.system_prompt.content
        
        sections = {}
        current_section = "main"
        current_content = []
        
        for line in content.split('\n'):
            # 检测章节标题
            if line.startswith('## '):
                # 保存上一个章节
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # 开始新章节
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def validate(self) -> bool:
        """验证系统提示词是否有效
        
        Returns:
            是否有效
        """
        if not self.system_prompt:
            return False
        
        # 检查内容是否为空
        if not self.system_prompt.content.strip():
            return False
        
        # 检查是否包含必要的章节
        sections = self.extract_sections()
        required_sections = ["operational_parameters", "scope_definition", "constraints"]
        
        for section in required_sections:
            if section not in sections:
                self.logger.warning(f"Missing required section: {section}")
        
        return True
    
    async def watch(self, callback: callable):
        """监视提示词文件变化
        
        Args:
            callback: 文件变化时的回调函数
        """
        # 这里可以实现文件监视逻辑
        # 由于跨平台兼容性，可以使用watchdog库或轮询
        pass


# 全局系统提示词注入器实例
_prompt_injector: Optional[SystemPromptInjector] = None


def get_prompt_injector(prompt_path: Optional[str] = None) -> SystemPromptInjector:
    """获取全局系统提示词注入器实例
    
    Args:
        prompt_path: 系统提示词文件路径
        
    Returns:
        SystemPromptInjector实例
    """
    global _prompt_injector
    if _prompt_injector is None:
        _prompt_injector = SystemPromptInjector(prompt_path)
    return _prompt_injector
