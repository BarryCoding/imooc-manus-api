from pydantic import BaseModel


class ToolResult[T](BaseModel):
    """工具结果Domain模型"""

    success: bool = True  # 是否成功调用
    message: str | None = None  # 额外的信息提示
    data: T | None = None  # 工具的执行结果/数据
