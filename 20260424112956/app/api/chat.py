"""聊天 API 路由"""

import uuid
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, AIMessage

from app.api.schemas import ChatRequest, ChatResponse, HistoryResponse, SkillInfo
from app.graph.agent import get_compiled_graph
from app.graph.state import ConversationState
from app.memory.conversation_store import get_conversation_store
from app.skills.registry import get_registry

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理用户消息，返回助手回复"""
    # 保存用户消息
    store = get_conversation_store()
    store.save_message(request.session_id, "human", request.message)

    # 获取历史消息
    history = store.get_messages_for_langchain(request.session_id)

    # 构建初始状态
    initial_state: ConversationState = {
        "messages": history + [HumanMessage(content=request.message)],
        "session_id": request.session_id,
        "intent": "",
        "intent_confidence": 0.0,
        "entities": {},
        "skill_result": "",
        "faq_answer": "",
        "needs_clarification": False,
        "clarification_question": "",
    }

    # 执行 LangGraph
    graph = get_compiled_graph()
    result = await graph.ainvoke(initial_state)

    # 提取助手回复
    last_message = result["messages"][-1]
    reply = last_message.content if hasattr(last_message, "content") else str(last_message)

    # 保存助手回复
    intent = result.get("intent", "")
    store.save_message(request.session_id, "ai", reply, intent=intent)

    # 判断是否执行了 Skill
    skill_result = result.get("skill_result", "")
    skill_executed = bool(skill_result)

    return ChatResponse(
        reply=reply,
        session_id=request.session_id,
        intent=intent,
        entities=result.get("entities", {}),
        skill_executed=skill_executed,
    )


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """获取对话历史"""
    store = get_conversation_store()
    messages = store.get_history(session_id)
    return HistoryResponse(session_id=session_id, messages=messages)


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """清除对话历史"""
    store = get_conversation_store()
    store.clear_session(session_id)
    return {"status": "ok", "message": f"Session {session_id} cleared"}


@router.get("/sessions", response_model=list[str])
async def list_sessions():
    """列出所有会话"""
    store = get_conversation_store()
    return store.list_sessions()


@router.get("/skills", response_model=list[SkillInfo])
async def list_skills():
    """列出所有可用 Skills"""
    registry = get_registry()
    return registry.list_skills()


@router.post("/sessions/new")
async def create_session():
    """创建新会话"""
    session_id = str(uuid.uuid4())[:8]
    return {"session_id": session_id}
