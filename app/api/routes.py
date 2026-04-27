from functools import lru_cache
from typing import Annotated
from fastapi import APIRouter, Depends
from app.clients.llm_client import LLMClient
from app.core.config import get_settings
from app.schemas.message import MessageRequest, MessageResponse
from app.services.orchestrator import MessageOrchestrator
from app.services.session_memory import SessionMemory
from app.tools.knowledge_tool import KnowledgeTool
router = APIRouter()

@lru_cache
def get_orchestrator() -> MessageOrchestrator:
    settings = get_settings()
    return MessageOrchestrator(
        knowledge_tool=KnowledgeTool(kb_url=settings.kb_url),
        llm_client=LLMClient(settings=settings),
        session_memory=SessionMemory(
            max_turns=settings.memory_max_turns,
            ttl_seconds=settings.memory_ttl_seconds,
        ),
    )
@router.post("/messages", response_model=MessageResponse)
async def create_message(
    payload: MessageRequest,
    orchestrator: Annotated[MessageOrchestrator, Depends(get_orchestrator)],
) -> MessageResponse:
    return await orchestrator.handle(payload)