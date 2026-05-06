"""LangGraph 处理节点"""

from langchain_core.messages import AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic

from app.config import settings
from app.graph.state import ConversationState
from app.skills.registry import get_registry
from app.knowledge.faq_retriever import get_faq_retriever


# 系统 Prompt
SYSTEM_PROMPT = """你是一个智能运维助手，可以帮助用户管理系统中的用户和资源。

你的能力包括：
1. 添加/删除用户
2. 添加/删除资源
3. 单点登录（SSO）配置
4. 回答常见问题

当前对话上下文：
- 识别到的意图：{intent}
- 提取的实体：{entities}
- FAQ 检索结果：{faq_answer}
- Skill 执行结果：{skill_result}

请根据上下文信息自然地回复用户。如果 Skill 已执行成功，请用简洁的语言告知用户结果。
如果需要更多信息，请礼貌地询问。"""


async def general_handler_node(state: ConversationState) -> dict:
    """一般对话处理节点（占位）"""
    return {}


def get_chat_llm():
    """获取对话 LLM"""
    return ChatAnthropic(
        model=settings.ANTHROPIC_MODEL,
        api_key=settings.ANTHROPIC_API_KEY,
        base_url=settings.ANTHROPIC_BASE_URL,
        temperature=0.7,
        timeout=settings.API_TIMEOUT_MS,
    )


def faq_retrieval_node(state: ConversationState) -> dict:
    """FAQ 检索节点：根据用户消息检索知识库"""
    retriever = get_faq_retriever()

    # 获取最新用户消息
    last_user_msg = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, SystemMessage):
            continue
        if hasattr(msg, "type") and msg.type == "human":
            last_user_msg = msg.content
            break
        if msg.__class__.__name__ == "HumanMessage":
            last_user_msg = msg.content
            break

    if not last_user_msg:
        return {"faq_answer": ""}

    results = retriever.retrieve(last_user_msg, top_k=2)

    if results:
        best = results[0]
        faq_text = f"相关FAQ：Q: {best['question']} A: {best['answer']}"
        return {"faq_answer": faq_text}

    return {"faq_answer": ""}


async def skill_execution_node(state: ConversationState) -> dict:
    """Skill 执行节点：根据意图执行对应 Skill"""
    intent = state.get("intent", "")
    entities = state.get("entities", {})
    needs_clarification = state.get("needs_clarification", False)

    if needs_clarification:
        return {"skill_result": ""}

    registry = get_registry()
    skill = registry.get_by_intent(intent)

    if skill is None:
        return {"skill_result": ""}

    # 检查缺失参数
    missing = skill.get_missing_params(entities)
    if missing:
        clarification = skill.format_clarification(missing)
        return {
            "skill_result": "",
            "needs_clarification": True,
            "clarification_question": clarification,
        }

    # 异步执行 Skill
    result = await skill.execute(entities)

    if result.success:
        return {"skill_result": result.message}
    else:
        return {"skill_result": f"操作失败：{result.message}"}


def clarification_node(state: ConversationState) -> dict:
    """澄清节点：处理需要用户澄清的情况"""
    question = state.get("clarification_question", "")
    if question:
        return {
            "messages": [AIMessage(content=question)],
        }
    return {"messages": []}


def response_node(state: ConversationState) -> dict:
    """响应生成节点：生成最终回复"""
    llm = get_chat_llm()

    intent = state.get("intent", "general_chat")
    entities = state.get("entities", {})
    faq_answer = state.get("faq_answer", "")
    skill_result = state.get("skill_result", "")

    system_content = SYSTEM_PROMPT.format(
        intent=intent,
        entities=str(entities) if entities else "无",
        faq_answer=faq_answer if faq_answer else "无相关FAQ",
        skill_result=skill_result if skill_result else "无",
    )

    response = llm.invoke([
        SystemMessage(content=system_content),
        *state["messages"][-6:],
    ])

    return {"messages": [response]}
