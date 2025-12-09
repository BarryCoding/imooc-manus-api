from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class LLMConfig(BaseModel):
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(8192, ge=0)


class AgentConfig(BaseModel):
    max_iterations: int = Field(default=100, gt=0, lt=1000)  # Agent最大迭代次数
    max_retries: int = Field(default=3, gt=1, lt=10)  # 最大重试次数
    max_search_results: int = Field(default=10, gt=1, lt=30)  # 最大搜索结果条数


class MCPTransport(str, Enum):
    """MCP传输类型枚举"""

    STDIO = "stdio"  # 本地输入输出
    SSE = "sse"  # 流式事件 deprecated in MCP
    STREAMABLE_HTTP = "streamable_http"  # 流式HTTP


class MCPServerConfig(BaseModel):
    """MCP服务配置"""

    # 通用配置字段
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP  # 传输协议
    enabled: bool = True  # 是否开启，默认为True
    description: str | None = None  # 服务器描述
    env: dict[str, str] | None = None  # 环境变量配置

    # stdio配置
    command: str | None = None  # 启用命令
    args: list[str] | None = None  # 命令参数

    # streamable_http & sse配置
    url: str | None = None  # MCP服务URL地址
    headers: dict[str, Any] | None = None  # MCP服务请求头

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_mcp_server_config(self):
        """校验mcp_server_config的相关信息, 包含url+command的校验"""

        # 1.判断transport是否为sse/streamable_http
        if self.transport in [MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP]:
            # 2.这两种模式需要传递url
            if not self.url:
                raise ValueError("在sse或streamable_http模式下必须传递url")

        # 3.判断transport是否为stdio类型
        if self.transport == MCPTransport.STDIO:
            # 4.stdio类型必须传递command
            if not self.command:
                raise ValueError("在stdio模式下必须传递command")

        return self


class MCPConfig(BaseModel):
    """应用MCP配置"""

    mcpServers: dict[str, MCPServerConfig] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class AppConfig(BaseModel):
    """应用配置信息: 包含LLM提供商配置, Agent配置, MCP服务配置"""

    llm_config: LLMConfig
    agent_config: AgentConfig
    mcp_config: MCPConfig  # MCP服务配置

    # 允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
