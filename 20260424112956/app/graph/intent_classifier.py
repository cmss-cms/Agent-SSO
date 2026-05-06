"""意图识别节点"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from app.config import settings
from app.graph.state import ConversationState, INTENT_DESCRIPTIONS


INTENT_CLASSIFICATION_PROMPT = """你是一个意图识别专家。根据用户的对话历史和当前消息，识别用户的意图。

可选意图类型：
{intent_descriptions}

请分析用户消息并返回 JSON 格式结果：
{{
    "intent": "意图类型",
    "confidence": 0.0-1.0的置信度,
    "entities": {{
        "用户名": "提取的用户名（如有）",
        "资源名": "提取的资源名（如有）",
        "资源类型": "提取的资源类型（如有）",
        "其他": "其他关键实体"
    }},
    "needs_clarification": false,
    "clarification_question": ""
}}

规则：
1. 如果用户意图明确，confidence 应 >= 0.8
2. 如果意图不太明确但可推测，confidence 在 0.5-0.8
3. 如果意图完全不明确，设为 "general_chat"，confidence < 0.5
4. 如果缺少关键信息（如添加用户但没说用户名），设置 needs_clarification 为 true
5. 只返回 JSON，不要其他文字"""


def get_intent_classifier():
    """获取意图分类器 LLM"""
    return ChatAnthropic(
        model=settings.ANTHROPIC_MODEL,
        api_key=settings.ANTHROPIC_API_KEY,
        base_url=settings.ANTHROPIC_BASE_URL,
        temperature=0,
        timeout=settings.API_TIMEOUT_MS,
    )


def classify_intent(state: ConversationState) -> dict:
    """意图识别节点：分析用户消息识别意图

    Args:
        state: 当前对话状态

    Returns:
        状态更新字典
    """
    llm = get_intent_classifier()

    # 构建意图描述
    intent_desc = "\n".join(
        f"- {k}: {v}" for k, v in INTENT_DESCRIPTIONS.items()
    )

    # 获取最近的消息
    recent_messages = state["messages"][-6:]  # 最近3轮对话
    messages_text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in recent_messages
    )

    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        intent_descriptions=intent_desc
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"对话历史：\n{messages_text}\n\n请识别意图："),
    ])

    try:
        # 清理可能的 markdown 代码块标记
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        content = content.strip()

        result = json.loads(content)
        intent = result.get("intent", "general_chat")
        confidence = result.get("confidence", 0.0)
        entities = result.get("entities", {})
        needs_clarification = result.get("needs_clarification", False)
        clarification_question = result.get("clarification_question", "")
    except (json.JSONDecodeError, KeyError):
        intent = "general_chat"
        confidence = 0.0
        entities = {}
        needs_clarification = False
        clarification_question = ""

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "entities": entities,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question,
    }
