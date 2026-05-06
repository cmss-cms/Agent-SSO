"""LangGraph 对话 Agent - 核心图定义"""

from langgraph.graph import StateGraph, END

from app.graph.state import ConversationState
from app.graph.intent_classifier import classify_intent
from app.graph.nodes import (
    faq_retrieval_node,
    skill_execution_node,
    general_handler_node,
    clarification_node,
    response_node,
)


def should_clarify(state: ConversationState) -> str:
    """条件边：判断是否需要澄清"""
    if state.get("needs_clarification", False):
        return "clarify"
    return "respond"


def route_by_intent(state: ConversationState) -> str:
    """条件边：根据意图路由到不同处理"""
    intent = state.get("intent", "general_chat")
    confidence = state.get("intent_confidence", 0.0)

    if confidence < 0.5:
        return "faq"  # 置信度低，走 FAQ 检索

    # 有明确意图
    if intent in ("add_user", "delete_user", "add_resource", "delete_resource", "sso"):
        return "skill"

    if intent == "faq":
        return "faq"

    return "general"


def build_graph() -> StateGraph:
    """构建对话图

    图结构：
    ┌──────────────────┐
    │  intent_classifier │ ← 识别意图
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  route_by_intent  │ ← 意图路由
    └───┬────┬────┬────┘
        │    │    │
   ┌────▼┐ ┌─▼──┐ ┌▼──────┐
   │skill│ │ faq│ │general│
   └──┬──┘ └──┬─┘ └──┬────┘
      │       │      │
      └───┬───┘──────┘
     ┌────▼─────┐
     │ clarify? │ ← 判断是否需要澄清
     └─┬─────┬──┘
       │     │
  ┌────▼──┐ ┌▼────────┐
  │clarify│ │response │
  └───────┘ └─────────┘
    """
    graph = StateGraph(ConversationState)

    # 添加节点
    graph.add_node("intent_classifier", classify_intent)
    graph.add_node("faq_retrieval", faq_retrieval_node)
    graph.add_node("skill_execution", skill_execution_node)
    graph.add_node("general_handler", general_handler_node)
    graph.add_node("clarification", clarification_node)
    graph.add_node("response", response_node)

    # 设置入口
    graph.set_entry_point("intent_classifier")

    # 意图路由：分类后根据意图走不同分支
    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "skill": "skill_execution",
            "faq": "faq_retrieval",
            "general": "general_handler",
        },
    )

    # 各分支汇入澄清判断
    graph.add_edge("skill_execution", "response")
    graph.add_edge("faq_retrieval", "response")
    graph.add_edge("general_handler", "response")

    # 澄清判断（预留，skill_execution 内部已处理）
    # graph.add_conditional_edges(
    #     "skill_execution",
    #     should_clarify,
    #     {"clarify": "clarification", "respond": "response"},
    # )

    # 响应后结束
    graph.add_edge("clarification", END)
    graph.add_edge("response", END)

    return graph


# 编译图
def get_compiled_graph():
    """获取编译后的图"""
    graph = build_graph()
    return graph.compile()
