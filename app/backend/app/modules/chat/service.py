from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.utils import normalize_text
from app.modules.auth.models import User
from app.modules.chat.repository import ChatRepository
from app.modules.chat.schemas import ChatConversationDetail, ChatConversationRead, ChatMessageRead, ChatResponse
from app.modules.recommendations.schemas import RecommendationRequest
from app.modules.recommendations.service import RecommendationService


class ChatService:
    GREETINGS = ("oi", "ola", "bom dia", "boa tarde", "boa noite")
    TECHNICAL_TERMS = (
        "arado", "grade", "subsolador", "escarificador", "trator", "hp", "cv",
        "solo", "argil", "aren", "umid", "seco", "profund", "regul", "implemento",
    )

    def __init__(self, db: Session):
        self.db = db
        self.repository = ChatRepository(db)
        self.recommendation_service = RecommendationService(db)

    def parse_message(self, message: str) -> RecommendationRequest:
        text = normalize_text(message)
        payload = {"limit": 5}
        if any(term in text for term in ["arado", "subsolador", "escarificador"]):
            payload["implement_type"] = "ARADO"
        elif any(term in text for term in ["grade", "niveladora", "aradora"]):
            payload["implement_type"] = "GRADE"

        families = ["AETCR", "ASTH", "AETH", "ASDA", "ARH", "AF", "CRSG", "GSPCR", "GTCR", "GRP", "CRI", "SNVA", "NVCR", "NVP", "NVA", "GR", "NV"]
        for family in families:
            family_norm = normalize_text(family)
            if re.search(rf"(?<![a-z0-9]){re.escape(family_norm)}(?![a-z0-9])", text):
                payload["family"] = family
                break

        hp_match = re.search(r"(\d{2,3}(?:[.,]\d+)?)\s*(?:hp|cv)", text)
        if hp_match:
            payload["tractor_power_hp"] = float(hp_match.group(1).replace(",", "."))

        if "argil" in text:
            payload["soil_texture"] = "argiloso"
        elif "aren" in text:
            payload["soil_texture"] = "arenoso"
        elif "medio" in text or "media" in text:
            payload["soil_texture"] = "textura media"

        if "umid" in text or "molh" in text:
            payload["moisture"] = "umido"
        elif "seco" in text:
            payload["moisture"] = "seco"
        elif "adequad" in text:
            payload["moisture"] = "adequado"

        return RecommendationRequest(**payload)

    def answer(self, message: str, user: User, conversation_id: int | None = None) -> ChatResponse:
        conversation = self._get_or_create_conversation(user.id, message, conversation_id)
        self.repository.add_message(conversation.id, "user", message)
        current_payload = self.parse_message(message)
        payload = self._merge_conversation_context(conversation.id, current_payload)
        intent = self._classify_intent(message, current_payload)

        recommendations = []
        response_type = "clarification"
        if intent == "greeting":
            response_type = "guidance"
            answer = (
                "Olá! Posso comparar arados e grades com o seu trator. "
                "Informe a potência em hp ou cv, o tipo de solo e a operação desejada."
            )
        elif intent == "depth_guidance":
            response_type = "guidance"
            answer = self._depth_guidance(payload)
        elif not self._has_recommendation_basis(payload):
            answer = self._clarification_message(payload)
        else:
            query_payload = payload.model_copy(update={"limit": 12})
            result = self.recommendation_service.recommend(query_payload)
            recommendations = self._compatible_recommendations(result.recommendations, payload)
            if recommendations:
                response_type = "recommendation"
                answer = self._recommendation_answer(recommendations, payload)
            else:
                response_type = "no_match"
                answer = self._no_match_answer(payload)

        self.repository.add_message(
            conversation.id,
            "assistant",
            answer,
            metadata_json={
                "parsed_payload": payload.model_dump(),
                "response_type": response_type,
                "recommendations": [item.model_dump() for item in recommendations],
            },
        )
        self.db.commit()
        return ChatResponse(
            conversation_id=conversation.id,
            answer=answer,
            response_type=response_type,
            parsed_payload=payload,
            recommendations=recommendations,
        )

    def _classify_intent(self, message: str, payload: RecommendationRequest) -> str:
        text = normalize_text(message).strip()
        has_technical_term = any(term in text for term in self.TECHNICAL_TERMS)
        if any(term in text for term in ("profundidade", "regular", "regulagem")):
            return "depth_guidance"
        if not has_technical_term and any(text == greeting or text.startswith(f"{greeting} ") for greeting in self.GREETINGS):
            return "greeting"
        if has_technical_term or self._has_recommendation_basis(payload):
            return "recommendation"
        return "clarification"

    def _merge_conversation_context(self, conversation_id: int, current: RecommendationRequest) -> RecommendationRequest:
        merged = current.model_dump()
        for message in reversed(self.repository.list_messages(conversation_id)):
            if message.role != "assistant" or not message.metadata_json:
                continue
            previous = message.metadata_json.get("parsed_payload") or {}
            for field in ("implement_type", "family", "tractor_power_hp", "soil_texture", "moisture", "crop", "slope"):
                if merged.get(field) in (None, "") and previous.get(field) not in (None, ""):
                    merged[field] = previous[field]
            break
        return RecommendationRequest(**merged)

    @staticmethod
    def _has_recommendation_basis(payload: RecommendationRequest) -> bool:
        return bool(payload.implement_type or payload.family or payload.tractor_power_hp)

    @staticmethod
    def _compatible_recommendations(recommendations, payload: RecommendationRequest):
        compatible = []
        for recommendation in recommendations:
            item = recommendation.implement
            if payload.tractor_power_hp and item.potencia_min_hp is not None and item.potencia_max_hp is not None:
                if not item.potencia_min_hp <= payload.tractor_power_hp <= item.potencia_max_hp:
                    continue
            if payload.implement_type and normalize_text(item.grupo) != normalize_text(payload.implement_type):
                continue
            compatible.append(recommendation)
        return compatible[:3]

    @staticmethod
    def _depth_guidance(payload: RecommendationRequest) -> str:
        soil = normalize_text(payload.soil_texture)
        if "aren" in soil:
            detail = "Em solo arenoso, comece com menor profundidade e evite mobilização excessiva."
        elif "argil" in soil:
            detail = "Em solo argiloso, regule com o solo friável e evite trabalhar quando estiver muito úmido."
        else:
            detail = "A profundidade deve ser definida pelo diagnóstico de compactação e pela operação desejada."
        return (
            f"{detail} Faça uma passada curta, confira se o implemento está nivelado e ajuste gradualmente. "
            "Informe o implemento, a textura do solo e a profundidade desejada para uma orientação mais específica."
        )

    @staticmethod
    def _clarification_message(payload: RecommendationRequest) -> str:
        known = []
        if payload.soil_texture:
            known.append(f"solo {payload.soil_texture}")
        if payload.moisture:
            known.append(f"condição {payload.moisture}")
        prefix = f"Entendi: {', '.join(known)}. " if known else ""
        return prefix + "Para consultar a base, informe a potência do trator e se procura arado ou grade."

    @staticmethod
    def _recommendation_answer(recommendations, payload: RecommendationRequest) -> str:
        context = []
        if payload.tractor_power_hp:
            context.append(f"trator de {payload.tractor_power_hp:g} hp")
        if payload.soil_texture:
            context.append(f"solo {payload.soil_texture}")
        count = len(recommendations)
        heading = "Encontrei 1 opção compatível" if count == 1 else f"Encontrei {count} opções compatíveis"
        if context:
            heading += f" para {', '.join(context)}"
        lines = [f"{heading}:"]
        for recommendation in recommendations:
            item = recommendation.implement
            power = (
                f"{item.potencia_min_hp:g}–{item.potencia_max_hp:g} hp"
                if item.potencia_min_hp is not None and item.potencia_max_hp is not None
                else "potência não informada"
            )
            width = f", largura {item.largura_mm / 1000:.2f} m" if item.largura_mm else ""
            configuration = f" ({item.n_discos:g} discos)" if item.n_discos else ""
            lines.append(f"• {item.modelo or item.familia or item.grupo}{configuration}: {power}{width}.")
        if not payload.tractor_power_hp:
            lines.append("Informe a potência do trator para confirmar a compatibilidade antes da operação.")
        lines.append("Confirme a regulagem no manual do fabricante e faça uma passagem de teste no campo.")
        return "\n".join(lines)

    @staticmethod
    def _no_match_answer(payload: RecommendationRequest) -> str:
        if payload.tractor_power_hp:
            return (
                f"Não encontrei na base um conjunto com faixa declarada compatível com {payload.tractor_power_hp:g} hp. "
                "Tente informar outro tipo de implemento ou consulte o manual do trator antes de operar."
            )
        return "Não encontrei implementos compatíveis com os critérios informados. Revise o tipo ou a família do implemento."

    def list_conversations(self, user: User) -> list[ChatConversationRead]:
        return [ChatConversationRead.model_validate(item, from_attributes=True) for item in self.repository.list_conversations(user.id)]

    def get_conversation(self, user: User, conversation_id: int) -> ChatConversationDetail:
        conversation = self.repository.get_conversation(user.id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
        messages = [
            ChatMessageRead.model_validate(message, from_attributes=True)
            for message in self.repository.list_messages(conversation.id)
        ]
        return ChatConversationDetail(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=messages,
        )

    def _get_or_create_conversation(self, user_id: int, message: str, conversation_id: int | None):
        if conversation_id:
            conversation = self.repository.get_conversation(user_id, conversation_id)
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
            return conversation
        title = " ".join(message.strip().split())[:80] or "Nova conversa"
        return self.repository.create_conversation(user_id, title)
