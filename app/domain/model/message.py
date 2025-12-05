from pydantic import BaseModel, Field


class Message(BaseModel):
    """用户传递的消息"""

    message: str = ""  # 用户发送的消息
    # FIXME: naming may conflict with the field in File model
    attachments: list[str] = Field(default_factory=list)  # 用户发送的附件路径
