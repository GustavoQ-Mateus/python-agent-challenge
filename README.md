# Python Agent Challenge

API em Python feita para o desafio técnico TCE-CE

## Stack

- Python
- FastAPI
- Pydantic
- HTTPX
- OpenAI SDK compatível
- Docker Compose

## Configuração

Crie o `.env` a partir do arquivo de exemplo:

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

O `KB_URL` aponta para a base oficial do desafio. A chave do provedor de LLM fica somente no `.env` local.

## Rodando o projeto

```bash
docker compose up -d --build
```

A API sobe em:

```text
http://localhost:8000
```

A documentação automática do FastAPI fica em:

```text
http://localhost:8000/docs
```

Para parar:

```bash
docker compose down
```

## Endpoint

```http
POST /messages
```

Exemplo de entrada:

```json
{
  "message": "O que é composição?"
}
```

Também é possível enviar `session_id`:

```json
{
  "message": "Pode resumir o que falamos?",
  "session_id": "sessao-123"
}
```

Resposta esperada quando existe contexto:

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

Resposta quando a KB não tem contexto suficiente:

```json
{
  "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
  "sources": []
}
```

## Como o fluxo foi organizado

O endpoint só recebe e valida a entrada. Depois disso, o fluxo fica no orquestrador:

1. recebe a mensagem;
2. chama a tool de conhecimento;
3. a tool busca a KB por HTTP usando `KB_URL`;
4. o orquestrador monta pergunta + contexto;
5. o cliente de LLM gera a resposta;
6. a API retorna `answer` e `sources`.

Algumas regras que guiam o fluxo:

- a tool não responde diretamente ao usuário;
- o LLM sintetiza a resposta, mas não é usado como fonte primária;
- se a busca não encontra contexto suficiente, o fallback é retornado sem chamar o LLM;
- `sources` mostra apenas as seções realmente usadas como contexto;
- cada item de `sources` contém somente `section`.

## Memória de sessão

`session_id` é opcional.

Sem `session_id`, cada chamada é independente. Com `session_id`, a aplicação mantém um histórico curto em memória, com limite de turnos e TTL. As sessões ficam isoladas entre si.

## Testes

```bash
python -m pytest -q
```

## Teste - Validação via Docker

Os comandos abaixo foram executados com a API rodando no Docker. Eles foram escolhidos para validar contrato e fallback sem acionar o LLM.

### Teste - Pergunta fora do escopo

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"Qual a capital da Franca?"}'
```

Retorno:

```json
{"answer":"Não encontrei informação suficiente na base para responder essa pergunta.","sources":[]}
HTTP_STATUS:200
```

### Teste - Pergunta fora da KB

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"Pergunta fora do escopo da KB"}'
```

Retorno:

```json
{"answer":"Não encontrei informação suficiente na base para responder essa pergunta.","sources":[]}
HTTP_STATUS:200
```

### Teste - Entrada inválida

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST "http://localhost:8000/messages" \
  -H "Content-Type: application/json" \
  -d '{"message":"   "}'
```

Retorno:

```json
{"detail":[{"type":"value_error","loc":["body","message"],"msg":"Value error, message must not be empty","input":"   ","ctx":{"error":{}}}]}
HTTP_STATUS:422
```
