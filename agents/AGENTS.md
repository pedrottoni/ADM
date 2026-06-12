# 🧠 Agents — Agentes de IA

## Visão Geral
Módulo de agentes especializados que usam o `LLMClient` (Gemini / OpenRouter) para tarefas de negócio. Cada agente encapsula um domínio.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `base_agent.py` | Classe base abstrata. Define interface `execute(prompt)` |
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

## Dependências
- `core/llm_client.py` — todos os agentes usam o LLMClient
- `core/config.py` — Config.LLM_PROVIDER, API keys
- `core/database/` — agents acessam dados via SQLModel

## Tarefas Comuns
- "Criar um anúncio pra X" → `product_agent.py`, método `generate_listing()`
- "Analisar minhas finanças" → `finance_agent.py`, método `analyze_health()`
- "Responder cliente reclamando" → `customer_agent.py`
- "Gerar arte pra campanha" → `ads_agent.py`
