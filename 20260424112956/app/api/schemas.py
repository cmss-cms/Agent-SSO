"""API 数据模型"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str
    session_id: str
    intent: str = ""
    entities: dict = {}
    skill_executed: bool = False


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    message_count: int = 0


class SkillInfo(BaseModel):
    """Skill 信息"""
    name: str
    description: str
    intent: str
    parameters: list[dict]


class HistoryResponse(BaseModel):
    """历史记录响应"""
    session_id: str
    messages: list[dict]
