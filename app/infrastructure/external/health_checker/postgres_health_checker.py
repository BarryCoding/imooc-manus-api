import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.external.health_checker import HealthChecker
from app.domain.model.health_status import HealthStatus

logger = logging.getLogger(__name__)


class PostgresHealthChecker(HealthChecker):
    """Postgres健康检查器: 用于检查Postgres数据库服务是否正常"""

    def __init__(self, db_session: AsyncSession) -> None:
        """构造函数: 传递数据库会话完成服务初始化"""
        self._db_session = db_session

    async def check(self) -> HealthStatus:
        """执行一段简单的sql: 用于判断数据库服务是否正常"""
        try:
            await self._db_session.execute(text("SELECT 1"))
            return HealthStatus(service="postgres", status="ok")
        except Exception as e:
            logger.error(f"Postgres健康检查失败: {str(e)}")
            return HealthStatus(
                service="postgres",
                status="error",
                details=str(e),
            )
