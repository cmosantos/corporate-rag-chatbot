from fastapi import APIRouter, Depends, Request

from app.core.audit import AuditLogger, get_audit_logger
from app.core.auth import Principal, get_principal
from app.core.config import Settings, get_settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import RagChatService, get_rag_service

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
def readyz(settings: Settings = Depends(get_settings)) -> dict[str, str | bool]:
    return {
        "status": "ready" if settings.openai_vector_store_id else "degraded",
        "vector_store_configured": bool(settings.openai_vector_store_id),
    }


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    principal: Principal = Depends(get_principal),
    service: RagChatService = Depends(get_rag_service),
    audit: AuditLogger = Depends(get_audit_logger),
) -> ChatResponse:
    audit.write(
        "chat.request",
        user_id=principal.user_id,
        conversation_id=payload.conversation_id,
        route=str(request.url.path),
        metadata={"department": principal.department},
    )
    response = service.answer(payload, principal)
    audit.write(
        "chat.response",
        user_id=principal.user_id,
        conversation_id=payload.conversation_id,
        metadata={
            "source_count": len(response.sources),
            "tool_call_count": len(response.tool_calls),
        },
    )
    return response

