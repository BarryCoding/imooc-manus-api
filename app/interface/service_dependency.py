import logging
from functools import lru_cache

from app.domain.service.app_config_service import AppConfigService
from app.infrastructure.repository.file_app_config_repository import (
    FileAppConfigRepository,
)
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_app_config_service() -> AppConfigService:
    """获取应用配置服务"""
    # 1.获取数据仓库并打印日志
    logger.info("加载获取AppConfigService")
    file_app_config_repository = FileAppConfigRepository(settings.app_config_filepath)

    # 2.实例化AppConfigService
    return AppConfigService(app_config_repository=file_app_config_repository)
