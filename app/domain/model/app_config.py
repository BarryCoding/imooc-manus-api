from pydantic import BaseModel, ConfigDict, Field, HttpUrl


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


class AppConfig(BaseModel):
    """应用配置信息: 包含LLM提供商, Agent配置, A2A网络, MCP服务配置等"""

    llm_config: LLMConfig
    agent_config: AgentConfig

    # 允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
