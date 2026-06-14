# ADM — Shopee Growth Quest

Streamlit dashboard for managing a Shopee health/supplements store. Monolithic app with module-per-tab architecture.

**Stack:** Python 3.11 + Streamlit + SQLModel + SQLite + Google Gemini / OpenRouter + Tavily + Firecrawl

## Navigation

Each module has its own `AGENTS.md` — read it before opening source files.

| Module | What it contains |
|--------|------------------|
| `agents/` | 5 AI agents (Product, Finance, Ads, Customer + Base) |
| `core/` | Config, LLMClient, CompetitorService, SalesService |
| `core/database/` | 8 SQLModel tables, engine, migrations |
| `core/gamification/` | XP, levels, missions (quadratic formula) |
| `dashboard/` | Streamlit app entry point (`app.py`) |
| `dashboard/tabs/` | 7 tab modules (one `render(user, agents)` function each) |
| `dashboard/components/` | Reusable UI components |
| `scrapers/` | Shopee, Amazon, Enjoei, MercadoLivre, Magalu, Shein (Tavily+Firecrawl) |
| `docs/` | Project plan and status |
| `scripts/` | Utility scripts (empty) |
| `data/` | CSVs only — DB is NOT here |
| `tests/` | Empty, prepared for pytest |

## Critical Rules

1. **DB location**: `database.db` lives at **project root**, NOT in `data/`. The `engine.py` uses a relative path (`sqlite_file_name = "database.db"`), so CWD matters — always run from project root.
2. **Never commit** `.env` or `database.db` (gitignored).
3. **Component imports** (`dashboard/components/`) must be **local** (inside the function), not at module top.
4. **Scraper prices can be zero** — always validate before using.
5. **`select()` import**: Every file using `session.exec(select(...))` must `from sqlmodel import select` — otherwise `NameError`.
6. **No Playwright** — removed permanently. Scrapers use Tavily + Firecrawl only.

## Running

```bash
# From project root (required for DB path)
streamlit run dashboard/app.py

# Or double-click run_app.bat (Windows)
```

No linter, formatter, or pre-commit hooks configured. Code review is manual.

## Technical Quirks

- **Module-level side effects**: Importing `core/config.py` reads `.env`, `core/database/engine.py` creates the SQLAlchemy engine, `core/llm_client.py` instantiates the LLM client — all at import time before `st.set_page_config()`.
- **No `__init__.py`** in most packages — works due to Streamlit's CWD-based path resolution but fragile.
- **Session pattern**: Use `session = next(get_session())` to get a SQLModel session. Some callers don't close explicitly (relying on GC).
- **LLM fallback**: When primary provider fails and `GOOGLE_API_KEY` exists, automatically falls back to Gemini with a system warning prefix.
- **Mutable Config**: `Config.set_api_key()`, `Config.set_llm_settings()`, `Config.set_llm_enabled()` mutate in-memory AND persist to `.env`.
- **`settings_view.py` bug**: Calls `llm_client.setup_provider()` but the method is actually `_setup_provider()` (private). Will raise `AttributeError` at runtime.
- **Duplicate `MARKETPLACE_LABELS`**: Defined in both `core/competitor_service.py` (with emojis) and `scrapers/__init__.py` (without). Maintenance hazard.

## Architecture

```
User → Dashboard (app.py) → Tabs (tabs/*.py) → Agents → LLMClient / Database / Scrapers
                                                           ↕
                                                       Tavily / Firecrawl (external)
```

## Adding a New Tab

1. Create `dashboard/tabs/new_tab.py` with `render(user, agents)`
2. Register in `dashboard/tabs/__init__.py` → `TAB_RENDERERS`
3. Add label + key in `dashboard/app.py`

## Testing

```bash
pytest tests/
```

Mock Tavily/Firecrawl in tests. No integration test infrastructure yet.
