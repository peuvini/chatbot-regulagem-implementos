from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.recommendations.schemas import RecommendationItem, RecommendationRequest


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    response_type: Literal["guidance", "clarification", "recommendation", "no_match"]
    parsed_payload: RecommendationRequest
    recommendations: list[RecommendationItem]


class ChatConversationRead(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    metadata_json: dict | None = None


class ChatConversationDetail(ChatConversationRead):
    messages: list[ChatMessageRead]
