"""
MCP Server Google API Adapter Module
支持谷歌API服务的适配器
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..tool_registry import ToolAdapter, ToolDefinition, ToolMetadata, ToolParameter
from ..exceptions import AdapterError, ToolExecutionError, ConnectionError, AuthenticationError, RateLimitError
from ..logger import get_logger


@dataclass
class GoogleAPIConfig:
    """Google API配置"""
    api_key: str
    base_url: str = "https://www.googleapis.com"
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit: int = 100  # 每分钟请求数
    services: List[str] = None


class GoogleAPIAdapter(ToolAdapter):
    """Google API适配器"""
    
    def __init__(self, name: str = "google", config: Optional[Dict[str, Any]] = None):
        """初始化Google API适配器
        
        Args:
            name: 适配器名称
            config: 适配器配置
        """
        super().__init__(name, config)
        self._api_config: Optional[GoogleAPIConfig] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_count: int = 0
        self._request_window_start: Optional[datetime] = None
        self._rate_limit_lock = asyncio.Lock()
    
    async def initialize(self):
        """初始化适配器"""
        if self._initialized:
            return
        
        self.logger.info(f"Initializing Google API adapter: {self.name}")
        
        # 解析配置
        api_key = self.config.get("api_key")
        if not api_key:
            raise AdapterError(self.name, "API key is required")
        
        self._api_config = GoogleAPIConfig(
            api_key=api_key,
            base_url=self.config.get("base_url", "https://www.googleapis.com"),
            timeout=self.config.get("timeout", 30.0),
            max_retries=self.config.get("max_retries", 3),
            rate_limit=self.config.get("rate_limit", 100),
            services=self.config.get("services", [])
        )
        
        # 创建HTTP会话
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self._api_config.timeout),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MCP-Server/1.0"
            }
        )
        
        self._initialized = True
        self.logger.info("Google API adapter initialized")
    
    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具执行结果
        """
        # 检查速率限制
        await self._check_rate_limit()
        
        # 解析工具名称
        parts = tool_name.split(".")
        if len(parts) < 2:
            raise ToolExecutionError(tool_name, "Invalid tool name format")
        
        service = parts[1]
        method = parts[2] if len(parts) > 2 else "execute"
        
        try:
            # 根据服务类型执行相应的API调用
            if service == "search":
                return await self._execute_search(params)
            elif service == "translate":
                return await self._execute_translate(params)
            elif service == "maps":
                return await self._execute_maps(params)
            elif service == "youtube":
                return await self._execute_youtube(params)
            elif service == "calendar":
                return await self._execute_calendar(params)
            elif service == "drive":
                return await self._execute_drive(params)
            else:
                raise ToolExecutionError(tool_name, f"Unsupported service: {service}")
                
        except aiohttp.ClientError as e:
            raise ConnectionError("Google API", str(e))
        except Exception as e:
            raise ToolExecutionError(tool_name, str(e))
    
    async def _check_rate_limit(self):
        """检查并执行速率限制"""
        async with self._rate_limit_lock:
            now = datetime.utcnow()
            
            # 重置计数器
            if (self._request_window_start is None or
                now - self._request_window_start > timedelta(minutes=1)):
                self._request_count = 0
                self._request_window_start = now
            
            # 检查是否超过限制
            if self._request_count >= self._api_config.rate_limit:
                wait_time = timedelta(minutes=1) - (now - self._request_window_start)
                raise RateLimitError("Google API", self._api_config.rate_limit)
            
            self._request_count += 1
    
    async def _execute_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Google搜索
        
        Args:
            params: 搜索参数
            
        Returns:
            搜索结果
        """
        query = params.get("query")
        if not query:
            raise ToolExecutionError("google.search", "Query parameter is required")
        
        num_results = params.get("num", 10)
        start = params.get("start", 1)
        
        url = f"{self._api_config.base_url}/customsearch/v1"
        params = {
            "key": self._api_config.api_key,
            "cx": params.get("cx", ""),  # Custom Search Engine ID
            "q": query,
            "num": num_results,
            "start": start
        }
        
        return await self._make_request("GET", url, params)
    
    async def _execute_translate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Google翻译
        
        Args:
            params: 翻译参数
            
        Returns:
            翻译结果
        """
        text = params.get("text")
        if not text:
            raise ToolExecutionError("google.translate", "Text parameter is required")
        
        source = params.get("source", "auto")
        target = params.get("target", "en")
        
        url = f"{self._api_config.base_url}/language/translate/v2"
        params = {
            "key": self._api_config.api_key,
            "q": text,
            "source": source,
            "target": target
        }
        
        return await self._make_request("POST", url, params)
    
    async def _execute_maps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Google Maps API
        
        Args:
            params: Maps参数
            
        Returns:
            Maps结果
        """
        endpoint = params.get("endpoint", "geocode")
        
        if endpoint == "geocode":
            address = params.get("address")
            if not address:
                raise ToolExecutionError("google.maps.geocode", "Address parameter is required")
            
            url = f"{self._api_config.base_url}/maps/api/geocode/json"
            params = {
                "key": self._api_config.api_key,
                "address": address
            }
        elif endpoint == "places":
            query = params.get("query")
            if not query:
                raise ToolExecutionError("google.maps.places", "Query parameter is required")
            
            url = f"{self._api_config.base_url}/maps/api/place/textsearch/json"
            params = {
                "key": self._api_config.api_key,
                "query": query
            }
        else:
            raise ToolExecutionError("google.maps", f"Unsupported endpoint: {endpoint}")
        
        return await self._make_request("GET", url, params)
    
    async def _execute_youtube(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行YouTube API
        
        Args:
            params: YouTube参数
            
        Returns:
            YouTube结果
        """
        endpoint = params.get("endpoint", "search")
        
        if endpoint == "search":
            query = params.get("query")
            if not query:
                raise ToolExecutionError("google.youtube.search", "Query parameter is required")
            
            url = f"{self._api_config.base_url}/youtube/v3/search"
            params = {
                "key": self._api_config.api_key,
                "part": "snippet",
                "q": query,
                "maxResults": params.get("max_results", 10)
            }
        elif endpoint == "video":
            video_id = params.get("video_id")
            if not video_id:
                raise ToolExecutionError("google.youtube.video", "Video ID parameter is required")
            
            url = f"{self._api_config.base_url}/youtube/v3/videos"
            params = {
                "key": self._api_config.api_key,
                "part": "snippet,contentDetails,statistics",
                "id": video_id
            }
        else:
            raise ToolExecutionError("google.youtube", f"Unsupported endpoint: {endpoint}")
        
        return await self._make_request("GET", url, params)
    
    async def _execute_calendar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Calendar API
        
        Args:
            params: Calendar参数
            
        Returns:
            Calendar结果
        """
        endpoint = params.get("endpoint", "events")
        
        if endpoint == "events":
            calendar_id = params.get("calendar_id", "primary")
            
            url = f"{self._api_config.base_url}/calendar/v3/calendars/{calendar_id}/events"
            params = {
                "key": self._api_config.api_key,
                "timeMin": params.get("time_min"),
                "timeMax": params.get("time_max"),
                "maxResults": params.get("max_results", 10)
            }
        else:
            raise ToolExecutionError("google.calendar", f"Unsupported endpoint: {endpoint}")
        
        return await self._make_request("GET", url, params)
    
    async def _execute_drive(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行Drive API
        
        Args:
            params: Drive参数
            
        Returns:
            Drive结果
        """
        endpoint = params.get("endpoint", "files")
        
        if endpoint == "files":
            url = f"{self._api_config.base_url}/drive/v3/files"
            params = {
                "key": self._api_config.api_key,
                "q": params.get("query", ""),
                "pageSize": params.get("page_size", 10)
            }
        else:
            raise ToolExecutionError("google.drive", f"Unsupported endpoint: {endpoint}")
        
        return await self._make_request("GET", url, params)
    
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """发起HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: 查询参数
            data: 请求体数据
            retry_count: 重试次数
            
        Returns:
            响应数据
        """
        try:
            async with self._session.request(
                method=method,
                url=url,
                params=params,
                json=data
            ) as response:
                # 检查响应状态
                if response.status == 401:
                    raise AuthenticationError("Google API", "Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Google API", self._api_config.rate_limit)
                elif response.status >= 400:
                    error_text = await response.text()
                    raise AdapterError(self.name, f"API error: {response.status} - {error_text}")
                
                # 解析响应
                return await response.json()
                
        except (AuthenticationError, RateLimitError):
            raise
        except aiohttp.ClientError as e:
            # 重试逻辑
            if retry_count < self._api_config.max_retries:
                await asyncio.sleep(2 ** retry_count)  # 指数退避
                return await self._make_request(method, url, params, data, retry_count + 1)
            raise ConnectionError("Google API", str(e))
    
    async def list_tools(self) -> List[ToolDefinition]:
        """列出适配器支持的所有工具
        
        Returns:
            工具定义列表
        """
        tools = []
        
        # 搜索工具
        tools.append(ToolDefinition(
            metadata=ToolMetadata(
                name="google.search",
                description="Search the web using Google Custom Search API",
                version="1.0.0",
                author="Google Adapter",
                category="search",
                tags=["google", "search", "web"],
                timeout=30.0
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="num",
                    type="integer",
                    description="Number of results",
                    required=False,
                    default=10,
                    min=1,
                    max=100
                ),
                ToolParameter(
                    name="cx",
                    type="string",
                    description="Custom Search Engine ID",
                    required=False
                )
            ]
        ))
        
        # 翻译工具
        tools.append(ToolDefinition(
            metadata=ToolMetadata(
                name="google.translate",
                description="Translate text using Google Translate API",
                version="1.0.0",
                author="Google Adapter",
                category="translation",
                tags=["google", "translate", "language"],
                timeout=30.0
            ),
            parameters=[
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text to translate",
                    required=True
                ),
                ToolParameter(
                    name="source",
                    type="string",
                    description="Source language code",
                    required=False,
                    default="auto"
                ),
                ToolParameter(
                    name="target",
                    type="string",
                    description="Target language code",
                    required=False,
                    default="en"
                )
            ]
        ))
        
        # Maps工具
        tools.append(ToolDefinition(
            metadata=ToolMetadata(
                name="google.maps.geocode",
                description="Geocode an address using Google Maps API",
                version="1.0.0",
                author="Google Adapter",
                category="maps",
                tags=["google", "maps", "geocode"],
                timeout=30.0
            ),
            parameters=[
                ToolParameter(
                    name="address",
                    type="string",
                    description="Address to geocode",
                    required=True
                )
            ]
        ))
        
        # YouTube工具
        tools.append(ToolDefinition(
            metadata=ToolMetadata(
                name="google.youtube.search",
                description="Search YouTube videos",
                version="1.0.0",
                author="Google Adapter",
                category="video",
                tags=["google", "youtube", "video"],
                timeout=30.0
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results",
                    required=False,
                    default=10,
                    min=1,
                    max=50
                )
            ]
        ))
        
        return tools
    
    async def shutdown(self):
        """关闭适配器"""
        self.logger.info(f"Shutting down Google API adapter: {self.name}")
        
        # 关闭HTTP会话
        if self._session:
            await self._session.close()
            self._session = None
        
        self._initialized = False
