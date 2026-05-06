"""对话历史持久化存储"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, ColumnElement
from sqlalchemy.orm import declarative_base, sessionmaker
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import settings

Base = declarative_base()


class ConversationModel(Base):
    """对话记录表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # human / ai / system
    content = Column(Text, nullable=False)
    intent = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationStore:
    """对话历史存储

    支持 SQLite 持久化，可轻松切换到 PostgreSQL 等
    """

    def __init__(self, db_url: str | None = None):
        db_url = db_url or settings.DATABASE_URL.replace("+aiosqlite", "")
        # 确保数据目录存在
        db_path = db_url.split("///")[-1] if "///" in db_url else ""
        if db_path:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_message(
        self, session_id: str, role: str, content: str, intent: str | None = None
    ):
        """保存一条消息"""
        session = self.Session()
        try:
            record = ConversationModel(
                session_id=session_id,
                role=role,
                content=content,
                intent=intent,
            )
            session.add(record)
            session.commit()
        finally:
            session.close()

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        """获取对话历史"""
        session = self.Session()
        try:
            records = (
                session.query(ConversationModel)
                .filter_by(session_id=session_id)
                .order_by(ConversationModel.id.asc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "role": r.role,
                    "content": r.content,
                    "intent": r.intent,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]
        finally:
            session.close()

    def get_messages_for_langchain(self, session_id: str, limit: int = 50) -> list:
        """获取 LangChain 格式的消息列表"""
        history = self.get_history(session_id, limit)
        messages = []
        for msg in history:
            if msg["role"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "ai":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
        return messages

    def clear_session(self, session_id: str):
        """清除指定会话的历史"""
        session = self.Session()
        try:
            session.query(ConversationModel).filter_by(
                session_id=session_id
            ).delete()
            session.commit()
        finally:
            session.close()

    def list_sessions(self) -> list[ColumnElement[Any]]:
        """列出所有会话 ID"""
        session = self.Session()
        try:
            results = (
                session.query(ConversationModel.session_id)
                .distinct()
                .all()
            )
            return [r[0] for r in results]
        finally:
            session.close()


# 全局存储实例
_store: ConversationStore | None = None


def get_conversation_store() -> ConversationStore:
    """获取对话存储单例"""
    global _store
    if _store is None:
        _store = ConversationStore()
    return _store
