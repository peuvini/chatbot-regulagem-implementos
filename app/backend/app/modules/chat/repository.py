from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.chat.models import ChatConversation, ChatMessage


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: int, title: str) -> ChatConversation:
        conversation = ChatConversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.flush()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, user_id: int, conversation_id: int) -> ChatConversation | None:
        stmt = select(ChatConversation).where(ChatConversation.id == conversation_id, ChatConversation.user_id == user_id)
        return self.db.scalar(stmt)

    def list_conversations(self, user_id: int, limit: int = 30) -> list[ChatConversation]:
        stmt = (
            select(ChatConversation)
            .where(ChatConversation.user_id == user_id)
            .order_by(ChatConversation.updated_at.desc(), ChatConversation.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def add_message(self, conversation_id: int, role: str, content: str, metadata_json: dict | None = None) -> ChatMessage:
        message = ChatMessage(conversation_id=conversation_id, role=role, content=content, metadata_json=metadata_json)
        self.db.add(message)
        self.db.flush()
        return message

    def list_messages(self, conversation_id: int) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.id)
        return list(self.db.scalars(stmt).all())
