# 🧠 Agents — Agentes de IA

## Visão Geral
Módulo de agentes especializados que usam o `LLMClient` (Gemini / OpenRouter) para tarefas de negócio. Cada agente encapsula um domínio.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `base_agent.py` | Classe base abstrata `BaseAgent`. Define interface `run(*args, **kwargs)` (NÃO `execute()` — esse nome era errado na doc antiga) |
| `product_agent.py` | Geração de título, descrição, keywords, SEO para Shopee |
| `finance_agent.py` | Análise financeira, KPIs, budgeting, relatórios |
| `ads_agent.py` | Geração de criativos e prompts de anúncio |
| `customer_agent.py` | Respostas para clientes (formal, casual, empático) |

## Como Usar

### Para tarefas de **criação de anúncio**:
1. Abrir `product_agent.py` + `core/llm_client.py` + `core/config.py`

### Para análise financeira:
1. Abrir `finance_agent.py` + `core/database/` (models + engine)

### Para respostas de atendimento:
1. Abrir `customer_agent.py`

## Métodos principais por agente

Cada agente concreto implementa `run(*args, **kwargs)` herdado de `BaseAgent` e expõe vários métodos. Os mais usados:

- **`ProductAgent`**: `generate_listing()`, `process_csv_import()`, `save_product()`, `get_low_stock_items()`, `generate_image_prompt()`, `generate_mass_upload_csv()`
- **`FinanceAgent`**: `process_upload()`, `confirm_upload()`, `get_financial_stats()`, `analyze_health()`, `calculate_order_profit()`, `get_top_products()`, `get_top_products_by_potes()`, `add_transaction()`, `generate_deep_analysis()`
- **`AdsAgent`**: `generate_keywords()`, `analyze_ad_performance()`
- **`CustomerAgent`**: `generate_response()` (3 tons: formal/casual/empático), `analyze_sentiment()`

Para a lista completa, abrir o `.py` correspondente.

## Dependências
- `core/llm_client.py` — todos os agentes usam o LLMClient
- `core/config.py` — Config.LLM_PROVIDER, API keys
- `core/database/` — agents acessam dados via SQLModel

## Tarefas Comuns
- "Criar um anúncio pra X" → `product_agent.py`, método `generate_listing()`
- "Analisar minhas finanças" → `finance_agent.py`, método `analyze_health()`
- "Responder cliente reclamando" → `customer_agent.py`
- "Gerar arte pra campanha" → `ads_agent.py`
