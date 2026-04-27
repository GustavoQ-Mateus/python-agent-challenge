# Python Agent Challenge

Backend em Python para responder perguntas usando uma base de conhecimento em Markdown, uma tool de contexto e um LLM no fluxo principal.

## Stack

- Python
- FastAPI
- Pydantic
- HTTPX
- OpenAI SDK compativel
- Docker Compose

## Configuracao

arquivo de env:

```bash
cp .env.example .env
```

Configuração das variaveis no `.env`:

```env
KB_URL=https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md
LLM_PROVIDER=openai
LLM_MODEL=
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
```

## Endpoint

```http
POST /messages
```
Entrada minima:
```json
{
  "message": "O que é composição?"
}
```
Entrada com sessao opcional:
```json
{
  "message": "Pode resumir o que falamos?",
  "session_id": "sessao-123"
}
```
Resposta de sucesso:

```json
{
  "answer": "Texto gerado pelo LLM com base no contexto recuperado.",
  "sources": [
    {
      "section": "Composição"
    }
  ]
}
```
Sem contexto suficiente:
```json
{
  "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
  "sources": []
}
```

## Ex
```bash
curl -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"O que é composição?"}'
```
```bash
curl -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"Pergunta fora do escopo da KB"}'
```

## Fluxo
1. A API recebe `message` e valida a entrada.
2. O orquestrador chama a tool de conhecimento.
3. A tool busca a KB em Markdown via HTTP usando `KB_URL`.
4. A tool retorna secoes relevantes para o orquestrador.
5. O orquestrador monta pergunta + contexto e chama o LLM.
6. A API retorna `answer` e `sources`.
## Regras de decisao
1. A tool e chamada para buscar contexto da KB antes da resposta final.
2. O LLM sintetiza a resposta, mas nao e a fonte primaria da verdade.
3. Se a tool nao encontrar contexto suficiente, o fluxo retorna o fallback padrao.
4. `sources` contem somente secoes realmente enviadas como contexto.
5. A tool nao responde diretamente ao usuario final.
## Memoria de sessao
`session_id` e opcional.
1. Sem `session_id`, cada chamada e independente.
2. Com `session_id`, a aplicacao mantem um historico curto em memoria.
3. Cada sessao e isolada das demais.
4. O historico tem limite de turnos e TTL.

