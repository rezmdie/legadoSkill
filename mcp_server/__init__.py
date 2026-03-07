"""
Universal MCP Server Implementation
A comprehensive bridge between AI models and diverse external tools.
"""

__version__ = "1.0.0"
__author__ = "Kilo Code"

from .server import MCPServer
from .config_loader import ConfigLoader
from .system_prompt_injector import SystemPromptInjector
from .tool_registry import ToolRegistry

__all__ = [
    "MCPServer",
    "ConfigLoader",
    "SystemPromptInjector",
    "ToolRegistry",
]
