from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MoocManus后端中控配置信息 从.env或者环境变量中加载数据"""

    # 项目
    env: str = "development"
    log_level: str = "INFO"

    # 数据库
    sqlalchemy_database_uri: str = (
        "postgresql+asyncpg://springer:postgres@localhost:5432/manus"
    )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # 腾讯云 co

    # 使用pydantic v2的写法来完成环境变量信息的告知
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """获取当前MoocManus项目的配置信息 并对内容进行缓存 避免重复读取"""
    settings = Settings()
    return settings
