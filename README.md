# Python Agent Challenge

Backend em Python para responder perguntas usando uma base de conhecimento em Markdown, uma tool de contexto e um LLM no fluxo principal.

## Stack

- Python
- FastAPI
- Pydantic
- HTTPX
- OpenAI SDK compatível
- Docker Compose

## Configuração

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Variáveis principais:

```env
KB_URL=https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
```

`KB_URL` deve apontar para a base oficial do desafio. A chave do LLM deve ficar apenas no `.env` local.

## Execução

```bash
docker compose up -d --build
```

A API fica disponível em:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Para encerrar:

```bash
docker compose down
```

## Endpoint

```http
POST /messages
```

Entrada mínima:

```json
{
  "message": "O que é composição?"
}
```

Entrada com sessão opcional:

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

## Validação teste via DOCKER

Os comandos abaixo foram executados com a API rodando via Docker. Eles não acionam o LLM, porque usam perguntas sem contexto suficiente ou entrada inválida.

### teste fora do escopo

Comando:

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"Qual a capital da Franca?"}'
```

Resposta retornada:

```json
{"answer":"Não encontrei informação suficiente na base para responder essa pergunta.","sources":[]}
HTTP_STATUS:200
```

### teste fora do conhecimento

Comando:

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"Pergunta fora do escopo da KB"}'
```

Resposta retornada:

```json
{"answer":"Não encontrei informação suficiente na base para responder essa pergunta.","sources":[]}
HTTP_STATUS:200
```

### teste vazio

Comando:

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"   "}'
```

Resposta retornada:

```json
{"detail":[{"type":"value_error","loc":["body","message"],"msg":"Value error, message must not be empty","input":"   ","ctx":{"error":{}}}]}
HTTP_STATUS:422
```

## Fluxo

1. A API recebe `message` e valida a entrada.
2. O orquestrador chama a tool de conhecimento.
3. A tool busca a KB em Markdown via HTTP usando `KB_URL`.
4. A tool retorna seções relevantes para o orquestrador.
5. O orquestrador monta pergunta + contexto e chama o LLM.
6. A API retorna `answer` e `sources`.

## Regras de Decisão

1. A tool é chamada para buscar contexto da KB antes da resposta final.
2. O LLM sintetiza a resposta, mas não é a fonte primária da verdade.
3. Se a tool não encontrar contexto suficiente, o fluxo retorna o fallback padrão.
4. `sources` contém somente seções realmente enviadas como contexto.
5. A tool não responde diretamente ao usuário final.

## Memória De Sessão

`session_id` é opcional.

1. Sem `session_id`, cada chamada é independente.
2. Com `session_id`, a aplicação mantém um histórico curto em memória.
3. Cada sessão é isolada das demais.
4. O histórico tem limite de turnos e TTL.

## Testes

```bash
python -m pytest -q
```