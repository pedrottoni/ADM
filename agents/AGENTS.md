# Agents — AI Agents

## Overview
Specialized AI agents that use `LLMClient` (Gemini / OpenRouter) for business tasks. Each agent encapsulates a domain.

## Files

| File | Purpose |
|------|---------|
| `base_agent.py` | Abstract base class `BaseAgent`. Defines interface `run(*args, **kwargs)` (NOT `execute()` — that name was wrong in old docs) |
| `product_agent.py` | Title, description, keywords, SEO generation for Shopee listings |
| `finance_agent.py` | Financial analysis, KPIs, budgeting, reports |
| `ads_agent.py` | Ad creative and prompt generation |
| `customer_agent.py` | Customer responses (formal, casual, empathetic) |

## Key Methods

- **`ProductAgent`**: `generate_listing()`, `process_csv_import()`, `save_product()`, `get_low_stock_items()`, `generate_image_prompt()`, `generate_mass_upload_csv()`
- **`FinanceAgent`**: `process_upload()`, `confirm_upload()`, `get_financial_stats()`, `analyze_health()`, `calculate_order_profit()`, `get_top_products()`, `get_top_products_by_potes()`, `add_transaction()`, `generate_deep_analysis()`
- **`AdsAgent`**: `generate_keywords()`, `analyze_ad_performance()`
- **`CustomerAgent`**: `generate_response()` (3 tones: formal/casual/empathetic), `analyze_sentiment()`

## How to Use

| Task | Open first |
|------|-----------|
| "Create an ad for X" | `product_agent.py` → `generate_listing()` |
| "Analyze my finances" | `finance_agent.py` → `analyze_health()` |
| "Respond to customer" | `customer_agent.py` |
| "Generate campaign art" | `ads_agent.py` |

## Technical Quirks

- Agents are lazily instantiated into `st.session_state` on first browser session, not at import time
- All agents import `llm_client` singleton at module scope
- Sessions via `next(get_session())` — some callers don't close explicitly

## Dependencies
- `core/llm_client.py` — all agents use LLMClient
- `core/config.py` — Config.LLM_PROVIDER, API keys
- `core/database/` — agents access data via SQLModel
