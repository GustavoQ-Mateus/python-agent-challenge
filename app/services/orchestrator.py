from app.clients.llm_client import LLMClient
from app.schemas.message import MessageRequest, MessageResponse, Source
from app.services.session_memory import SessionMemory
from app.tools.knowledge_tool import KnowledgeResult, KnowledgeTool
FALLBACK_ANSWER = "Não encontrei informação suficiente na base para responder essa pergunta."

class MessageOrchestrator:
    def __init__(
        self,
        knowledge_tool: KnowledgeTool,
        llm_client: LLMClient,
        session_memory: SessionMemory,
    ) -> None:
        self.knowledge_tool = knowledge_tool
        self.llm_client = llm_client
        self.session_memory = session_memory

    async def handle(self, request: MessageRequest) -> MessageResponse:
        context_items = await self.knowledge_tool.search(request.message)
        if not context_items:
            return MessageResponse(answer=FALLBACK_ANSWER, sources=[])
        context = self._build_context(context_items)
        history = self.session_memory.get_history(request.session_id)
        answer = await self.llm_client.generate_answer(
            message=request.message,
            context=context,
            history=history,
        )

        if not answer:
            return MessageResponse(answer=FALLBACK_ANSWER, sources=[])
        self.session_memory.append(
            session_id=request.session_id,
            message=request.message,
            answer=answer,
        )

        return MessageResponse(
            answer=answer,
            sources=[Source(section=item.section) for item in context_items],
        )

    def _build_context(self, items: list[KnowledgeResult]) -> str:
        chunks = []
        for item in items:
            chunks.append(f"## {item.section}\n{item.content}")
        return "\n\n".join(chunks)