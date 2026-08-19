from types import SimpleNamespace

import pytest

from app.modules.chat.service import ChatService
from app.modules.implements.schemas import ImplementRead
from app.modules.recommendations.schemas import RecommendationItem, RecommendationRequest


def recommendation(group: str, minimum: float, maximum: float, model: str = "TESTE") -> RecommendationItem:
    return RecommendationItem(
        score=90,
        reasons=["potência compatível"],
        ml_predicted_power_hp=(minimum + maximum) / 2,
        technical_note="teste",
        implement=ImplementRead(
            id=1,
            grupo=group,
            familia="FAM",
            modelo=model,
            potencia_min_hp=minimum,
            potencia_max_hp=maximum,
            largura_mm=2000,
        ),
    )


@pytest.mark.unit
def test_parse_message_extracts_technical_parameters():
    service = ChatService.__new__(ChatService)

    payload = service.parse_message("Preciso de uma grade NVCR para trator de 120 hp em solo argiloso e seco")

    assert payload.implement_type == "GRADE"
    assert payload.family == "NVCR"
    assert payload.tractor_power_hp == 120
    assert payload.soil_texture == "argiloso"
    assert payload.moisture == "seco"


@pytest.mark.unit
def test_greeting_does_not_become_recommendation_intent():
    service = ChatService.__new__(ChatService)
    payload = RecommendationRequest()

    assert service._classify_intent("Bom dia", payload) == "greeting"
    assert service._classify_intent("Bom dia, tenho um trator de 90 hp", service.parse_message("trator de 90 hp")) == "recommendation"


@pytest.mark.unit
def test_compatibility_filter_respects_power_and_implement_group():
    payload = RecommendationRequest(implement_type="GRADE", tractor_power_hp=90)
    items = [
        recommendation("GRADE", 80, 100, "COMPATÍVEL"),
        recommendation("GRADE", 120, 150, "POTÊNCIA ERRADA"),
        recommendation("ARADO", 80, 100, "GRUPO ERRADO"),
    ]

    result = ChatService._compatible_recommendations(items, payload)

    assert [item.implement.modelo for item in result] == ["COMPATÍVEL"]


@pytest.mark.unit
def test_greeting_answer_does_not_call_recommendation_engine():
    class FakeRepository:
        def __init__(self):
            self.messages = []

        def create_conversation(self, user_id, title):
            return SimpleNamespace(id=1)

        def add_message(self, conversation_id, role, content, metadata_json=None):
            self.messages.append(SimpleNamespace(role=role, content=content, metadata_json=metadata_json))

        def list_messages(self, conversation_id):
            return self.messages

    class FailingRecommendationService:
        def recommend(self, payload):
            raise AssertionError("Saudações não devem consultar o motor de recomendação")

    service = ChatService.__new__(ChatService)
    service.repository = FakeRepository()
    service.recommendation_service = FailingRecommendationService()
    service.db = SimpleNamespace(commit=lambda: None)

    response = service.answer("Olá", SimpleNamespace(id=7))

    assert response.response_type == "guidance"
    assert "Informe a potência" in response.answer
    assert response.recommendations == []
