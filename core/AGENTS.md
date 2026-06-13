# ⚙️ Core — Serviços Centrais

## Visão Geral
Camada de infraestrutura do projeto: configuração, LLM, serviços de negócio, banco de dados e gamificação.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `config.py` | Carrega `.env`, expõe Config.LLM_PROVIDER, SHOPEE_*, API keys. Classe `Config` é **mutável** e persiste mudanças em `.env` via `set_api_key()`, `set_llm_settings()`, `set_llm_enabled()` |
| `llm_client.py` | Cliente LLM multi-provider (Gemini via `google.genai`, OpenRouter + NVIDIA via OpenAI-compatible) com fallback automático para Gemini quando primary falha. Tem método `generate_content()` (texto) e `generate_with_image()` (Vision) |
| `competitor_service.py` | `CompetitorService` — orquestra scrapers + matching IA + persistência. Métodos principais: `search_competitors()`, `confirm_match()` (revisão manual), `get_competitiveness_badge()` ("mais barato"/"abaixo da média"/"na média"/"acima da média"/"sem dados") |
| `sales_service.py` | `SalesService` — processa vendas em lote. Faz fuzzy match do `product_name` com `Product.title` (threshold 55%), decrementa `Product.stock` + `InventoryItem.stock` (via multiplicador `ProductComponent.quantity`), checa duplicatas. **API**: `match_product()`, `process_sale()`, `check_duplicate()`, `process_income_batch()` |

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
1. Abrir `llm_client.py` — métodos `generate_content(prompt, use_search=False)` e `generate_with_image(prompt, image_bytes, mime_type)` (Vision)
2. Providers: gemini → `google.genai`, openrouter/nvidia → OpenAI-compatible
3. `use_search=True` (Gemini) aciona Google Search grounding nos resultados
4. Quando provider falha, faz fallback automático para Gemini (se `GOOGLE_API_KEY` existir) e prefixa a resposta com aviso ⊳ "Backup (Gemini)..."
5. `LLMClient.set_enabled(bool)` persiste em `.env` (toggle do sidebar é persistente, não só em memória)

### Para mudar provider/model em runtime:
- `Config.set_llm_settings(provider, model)` persiste em `.env`
- `Config.set_api_key(provider, new_key)` atualiza a key (gemini/openrouter/nvidia)

### Para monitoramento de concorrência:
1. Abrir `competitor_service.py` + `scrapers/AGENTS.md`

## Dependências
- `agents/` — usa agentes em alguns fluxos
- `scrapers/` — `competitor_service.py` consome scrapers
- `.env` — Config carrega da raiz
