import logging

from fastapi import APIRouter

from app.interface.schema import Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/status", tags=["状态模块"])


@router.get(
    path="",
    response_model=Response,
    summary="系统健康检查",
    description="检查系统的postgres、redis、fastapi等组件的状态信息。",
)
async def get_status() -> Response:
    """系统健康检查: 检查postgres/redis/fastapi/cos等服务"""
    # TODO: 等待接入 postgres/redis/fastapi/cos
    return Response.success(msg="系统健康检查成功")
