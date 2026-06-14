from types import SimpleNamespace

from app.core.auth import Principal
from app.core.config import Settings
from app.schemas.chat import ChatRequest
from app.services.rag import RagChatService
from app.tools.internal_api import InternalApiClient
from app.tools.registry import ToolRegistry


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text="Employees may review the internal FAQ.",
            output=[
                SimpleNamespace(
                    type="file_search_call",
                    results=[
                        SimpleNamespace(
                            file_id="file_123",
                            filename="internal-faq.pdf",
                            text="Employees may review the internal FAQ.",
                        )
                    ],
                )
            ],
        )


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_rag_service_includes_file_search_and_sources() -> None:
    client = FakeClient()
    settings = Settings(openai_vector_store_id="vs_123", openai_api_key="test")
    service = RagChatService(client, settings, ToolRegistry(InternalApiClient()))

    response = service.answer(
        ChatRequest(question="Where is the FAQ?", conversation_id="c1"),
        Principal(user_id="u1", roles={"employee"}),
    )

    tools = client.responses.calls[0]["tools"]
    assert {"type": "file_search", "vector_store_ids": ["vs_123"], "max_num_results": 5} in tools
    assert client.responses.calls[0]["include"] == ["file_search_call.results"]
    assert response.sources[0].title == "internal-faq.pdf"

