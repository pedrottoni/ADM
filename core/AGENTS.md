# Core — Central Services

## Overview
Infrastructure layer: configuration, LLM, business services, database, and gamification.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Loads `.env`, exposes Config.LLM_PROVIDER, SHOPEE_*, API keys. `Config` is **mutable** — persists changes to `.env` via `set_api_key()`, `set_llm_settings()`, `set_llm_enabled()` |
| `llm_client.py` | Multi-provider LLM client (Gemini via `google.genai`, OpenRouter + NVIDIA via OpenAI-compatible) with automatic Gemini fallback. Methods: `generate_content()` (text) and `generate_with_image()` (Vision) |
| `competitor_service.py` | `CompetitorService` — orchestrates scrapers + AI matching + persistence. Key methods: `search_competitors()`, `confirm_match()` (manual review), `get_competitiveness_badge()` |
| `sales_service.py` | `SalesService` — batch sale processing. Fuzzy matches `product_name` to `Product.title` (55% threshold), decrements stock, checks duplicates. API: `match_product()`, `process_sale()`, `check_duplicate()`, `process_income_batch()` |

## Sub-modules

### `database/` → [AGENTS.md](./database/AGENTS.md)
SQLModel tables + engine + migrations.

### `gamification/` → [AGENTS.md](./gamification/AGENTS.md)
XP, levels, and missions engine.

## How to Use

### Configure API keys / provider:
1. Edit `config.py` + `.env` (root)
2. `Config.LLM_PROVIDER` controls which LLM is active

### Debug LLM:
1. Open `llm_client.py` — methods `generate_content(prompt, use_search=False)` and `generate_with_image(prompt, image_bytes, mime_type)` (Vision)
2. Providers: gemini → `google.genai`, openrouter/nvidia → OpenAI-compatible
3. `use_search=True` (Gemini only) enables Google Search grounding
4. When primary provider fails, auto-falls back to Gemini (if `GOOGLE_API_KEY` exists) with warning prefix
5. `LLMClient.set_enabled(bool)` persists to `.env` (sidebar toggle is persistent)

### Change provider/model at runtime:
- `Config.set_llm_settings(provider, model)` persists to `.env`
- `Config.set_api_key(provider, new_key)` updates the key (gemini/openrouter/nvidia)

### Competitor monitoring:
1. Open `competitor_service.py` + `scrapers/AGENTS.md`

## Technical Quirks

- **`settings_view.py` bug**: Calls `llm_client.setup_provider()` but method is actually `_setup_provider()` (private). Will raise `AttributeError` at runtime.
- **Duplicate `MARKETPLACE_LABELS`**: Defined in both `core/competitor_service.py` (with emojis) and `scrapers/__init__.py` (without). Maintenance hazard.
- `Config` class methods mutate in-memory AND persist to `.env` simultaneously

## Dependencies
- `agents/` — used in some flows
- `scrapers/` — `competitor_service.py` consumes scrapers
- `.env` — Config loads from root
