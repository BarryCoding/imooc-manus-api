from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class LLMConfig(BaseModel):
    base_url: HttpUrl = "https://api.deepseek.com"
    api_key: str = ""
    model_name: str = "deepseek-reasoner"
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(8192, ge=0)


class AppConfig(BaseModel):
    """应用配置信息: 包含Agent配置, LLM提供商, A2A网络, MCP服务配置等"""

    llm_config: LLMConfig

    # 允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")
