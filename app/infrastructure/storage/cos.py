import logging
from functools import lru_cache
from typing import Optional

from qcloud_cos import CosConfig, CosS3Client

from core.config import get_settings

logger = logging.getLogger(__name__)


class Cos:
    """腾讯云Cos对象存储"""

    def __init__(self):
        """构造函数: 完成配置获取 + 腾讯云Cos客户端初始化赋值"""
        self._settings = get_settings()
        self._client: Optional[CosS3Client] = None

    async def init(self) -> None:
        """手动调用: 完成腾讯云Cos客户端的创建"""
        # 1.判断客户端是否存在
        if self._client is not None:
            logger.warning("腾讯云Cos已初始化 无需重复操作")
            return

        try:
            # 2.创建cos配置
            config = CosConfig(
                Region=self._settings.cos_region,
                SecretId=self._settings.cos_secret_id,
                SecretKey=self._settings.cos_secret_key,
                Scheme=self._settings.cos_scheme,
                Token=None,
            )
            self._client = CosS3Client(config)
            logger.info("腾讯云Cos 初始化成功")
        except Exception as e:
            logger.error(f"腾讯云Cos 初始化失败: {str(e)}")
            raise

    async def shutdown(self) -> None:
        """关闭腾讯云Cos"""
        if self._client is not None:
            self._client = None
            logger.info("成功关闭: 腾讯云Cos")

        # 清除缓存
        get_cos.cache_clear()

    @property
    def client(self) -> CosS3Client:
        """只读属性:返回腾讯云Cos客户端"""
        if self._client is None:
            raise RuntimeError("腾讯云Cos未初始化 请调用init()完成初始化")
        return self._client


@lru_cache()
def get_cos() -> Cos:
    """使用lru_cache实现单例模式 获取腾讯云Cos"""
    return Cos()
