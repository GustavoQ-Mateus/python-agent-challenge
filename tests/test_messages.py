from fastapi.testclient import TestClient

from app.api.routes import get_orchestrator
from app.main import app
from app.schemas.message import MessageRequest, MessageResponse, Source
from app.services.orchestrator import FALLBACK_ANSWER


class FakeOrchestrator:
    async def handle(self, request: MessageRequest) -> MessageResponse:
        if "fora do escopo" in request.message.casefold():
            return MessageResponse(answer=FALLBACK_ANSWER, sources=[])

        return MessageResponse(
            answer="Composição usa outra instância para executar parte do trabalho.",
            sources=[Source(section="Composição")],
        )


def create_client() -> TestClient:
    app.dependency_overrides[get_orchestrator] = lambda: FakeOrchestrator()
    return TestClient(app)


def test_messages_returns_contract() -> None:
    client = create_client()

    response = client.post("/messages", json={"message": "O que é composição?"})

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"answer", "sources"}
    assert data["answer"]
    assert data["sources"] == [{"section": "Composição"}]


def test_sources_only_include_section() -> None:
    client = create_client()

    response = client.post("/messages", json={"message": "O que é composição?"})

    assert response.status_code == 200
    source = response.json()["sources"][0]
    assert set(source.keys()) == {"section"}


def test_fallback_without_context() -> None:
    client = create_client()

    response = client.post(
        "/messages",
        json={"message": "Pergunta fora do escopo da KB"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": FALLBACK_ANSWER,
        "sources": [],
    }


def test_empty_message_is_invalid() -> None:
    client = create_client()

    response = client.post("/messages", json={"message": "   "})

    assert response.status_code == 422