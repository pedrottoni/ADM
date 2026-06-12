# ⚙️ Core — Serviços Centrais

## Visão Geral
Camada de infraestrutura do projeto: configuração, LLM, serviços de negócio, banco de dados e gamificação.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `config.py` | Carrega `.env`, expõe Config.LLM_PROVIDER, SHOPEE_*, API keys |
| `llm_client.py` | Cliente LLM multi-provider (Gemini, OpenRouter, NVIDIA) com fallback |
| `competitor_service.py` | Serviço de monitoramento de concorrência (usa scrapers) |
| `sales_service.py` | CRUD de vendas e transações |

## Submódulos

### `database/` → [AGENTS.md](./database/AGENTS.md)
Models SQLModel + engine + migrations.

### `gamification/` → [AGENTS.md](./gamification/AGENTS.md)
Engine de XP, níveis e missões.

## Como Usar

### Para configurar API keys / provider:
1. Abrir `config.py` + `.env` (raiz)
2. `Config.LLM_PROVIDER` controla qual LLM está ativo

### Para debug de LLM:
1. Abrir `llm_client.py` — método `generate_content()`
2. Providers: gemini → google.genai, openrouter/nvidia → OpenAI-compatible

### Para monitoramento de concorrência:
1. Abrir `competitor_service.py` + `scrapers/AGENTS.md`

## Dependências
- `agents/` — usa agentes em alguns fluxos
- `scrapers/` — `competitor_service.py` consome scrapers
- `.env` — Config carrega da raiz
