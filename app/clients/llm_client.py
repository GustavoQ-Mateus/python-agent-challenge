from openai import AsyncOpenAI
from app.core.config import Settings

class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    async def generate_answer(
        self,
        message: str,
        context: str,
        history: str | None = None,
    ) -> str:
        messages = [
            {
            "role": "system",
            "content": (
                "Voce gera respostas curtas em portugues com base apenas no "
                "contexto fornecido. Se o contexto nao sustentar a resposta, "
                "nao invente. Nao inclua fontes no texto da resposta."
                ),
            }
        ]
        if history:
            messages.append(
                {
                "role": "user",
                "content": f"Historico curto da sessao:\n{history}",
                }
            )

        messages.append(
            {
            "role": "user",
            "content": (
                f"Pergunta:\n{message}\n\n"
                f"Contexto da base de conhecimento:\n{context}\n\n"
                "Responda somente com o texto final para o campo answer."
                ),
            }
        )

        response = await self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=messages,
            temperature=0.2,
        )
        answer = response.choices[0].message.content or ""
        return answer.strip()