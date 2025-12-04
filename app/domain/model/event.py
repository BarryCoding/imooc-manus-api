import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field

from app.domain.model.file import File
from app.domain.model.plan import Plan, Step
from app.domain.model.tool_result import ToolResult


class BaseEvent(BaseModel):
    """基础事件类: 定义事件的通用属性"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 事件id
    type: Literal[""] = ""  # 事件的类型
    created_at: datetime = Field(default_factory=datetime.now)  # 事件创建时间


class PlanEventStatus(str, Enum):
    """规划事件状态: 已创建/已更新/已完成"""

    CREATED = "created"  # 已创建
    UPDATED = "updated"  # 已更新
    COMPLETED = "completed"  # 已完成


class PlanEvent(BaseEvent):
    """规划事件类"""

    type: Literal["plan"] = "plan"
    plan: Plan  # 规划
    status: PlanEventStatus = PlanEventStatus.CREATED  # 规划事件状态


class TitleEvent(BaseEvent):
    """标题事件类"""

    type: Literal["title"] = "title"
    title: str = ""  # 标题


class StepEventStatus(str, Enum):
    """步骤事件状态: 已开始/已完成/失败"""

    STARTED = "started"  # 已开始
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class StepEvent(BaseEvent):
    """步骤事件类"""

    type: Literal["step"] = "step"
    step: Step  # 步骤信息
    status: StepEventStatus = StepEventStatus.STARTED


class MessageEvent(BaseEvent):
    """消息事件类: 人类消息/AI消息"""

    type: Literal["message"] = "message"
    role: Literal["user", "assistant"] = "assistant"  # 消息角色
    message: str = ""  # 消息本身
    attachments: list[File] = Field(default_factory=list)  # 附件列表信息


class BrowserToolContent(BaseModel):
    """浏览器工具扩展内容"""

    screenshot: str  # 浏览器快照截图


class MCPToolContent(BaseModel):
    """MCP工具内容"""

    result: Any


# TODO:工具扩展内容待完善
ToolContent = Union[BrowserToolContent, MCPToolContent]


class ToolEventStatus(str, Enum):
    """工具事件状态类型枚举"""

    CALLING = "calling"  # 调用中
    CALLED = "called"  # 调用完毕


class ToolEvent(BaseEvent):
    """工具事件类"""

    type: Literal["tool"] = "tool"
    status: ToolEventStatus = ToolEventStatus.CALLING  # 工具事件状态
    tool_call_id: str  # 工具调用id
    tool_name: str  # 工具集的名字
    tool_content: ToolContent | None = None  # 工具扩展内容
    tool_result: ToolResult | None = None  # 工具调用结果

    # FIXME: distinguish function_name and tool_name
    function_name: str  # LLM调用函数/工具名字
    function_args: dict[str, Any]  # LLM生成的工具调用参数


class WaitEvent(BaseEvent):
    """等待事件类: 等待用户输入确认"""

    type: Literal["wait"] = "wait"


class ErrorEvent(BaseEvent):
    """错误事件类"""

    type: Literal["error"] = "error"
    error: str = ""  # 错误信息


class DoneEvent(BaseEvent):
    """结束事件类"""

    type: Literal["done"] = "done"


# 定义应用事件类型声明
Event = Union[
    PlanEvent,
    TitleEvent,
    StepEvent,
    MessageEvent,
    ToolEvent,
    WaitEvent,
    ErrorEvent,
    DoneEvent,
]
