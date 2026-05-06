"""LangGraph 对话状态定义"""

from typing import Annotated, TypedDict, Literal
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """对话状态

    Attributes:
        messages: 对话消息列表（LangGraph 自动管理）
        session_id: 会话 ID
        intent: 识别到的意图
        intent_confidence: 意图识别置信度
        entities: 提取的实体信息
        skill_result: Skill 执行结果
        faq_answer: FAQ 检索结果
        needs_clarification: 是否需要用户澄清
        clarification_question: 澄清问题
    """

    messages: Annotated[list, add_messages]
    session_id: str
    intent: str
    intent_confidence: float
    entities: dict
    skill_result: str
    faq_answer: str
    needs_clarification: bool
    clarification_question: str


# 意图类型定义
IntentType = Literal[
    "add_user",          # 添加用户
    "delete_user",       # 删除用户
    "add_resource",      # 添加资源
    "delete_resource",   # 删除资源
    "sso",               # 单点登录
    "faq",               # FAQ 问答
    "general_chat",      # 一般对话
    "clarification",     # 需要澄清
]

# 意图描述映射（用于 prompt）
INTENT_DESCRIPTIONS = {
    "add_user": "用户想要添加/创建新用户账号",
    "delete_user": "用户想要删除/移除用户账号",
    "add_resource": "用户想要添加/创建资源（如服务器、存储、权限等）",
    "delete_resource": "用户想要删除/释放资源",
    "sso": "用户想要配置/了解/使用单点登录（SSO）",
    "faq": "用户询问常见问题或一般性知识",
    "general_chat": "一般性闲聊或不明确的请求",
    "clarification": "需要用户提供更多信息才能判断意图",
}
