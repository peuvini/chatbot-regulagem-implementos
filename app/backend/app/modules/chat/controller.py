from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.chat.schemas import ChatConversationDetail, ChatConversationRead, ChatRequest, ChatResponse
from app.modules.chat.service import ChatService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChatService(db).answer(payload.message, current_user, payload.conversation_id)


@router.get("/conversations", response_model=list[ChatConversationRead])
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChatService(db).list_conversations(current_user)


@router.get("/conversations/{conversation_id}", response_model=ChatConversationDetail)
def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ChatService(db).get_conversation(current_user, conversation_id)
