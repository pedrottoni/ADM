# ADM — Shopee Growth Quest

Streamlit dashboard for managing a Shopee health/supplements store (Nutri Active, DailyLife). Monolithic app with module-per-tab architecture.

**Stack:** Python 3.11 + Streamlit + SQLModel + SQLite + Google Gemini / OpenRouter + Tavily + Firecrawl

## Navigation

Read the relevant `AGENTS.md` before opening source files. Each module has its own.

| Module | AGENTS.md |
|--------|-----------|
| Root | Navigation map, critical rules, quirks |
| `agents/` | AI agents (Product, Finance, Ads, Customer) |
| `core/` | Config, LLMClient, CompetitorService, SalesService |
| `core/database/` | 8 SQLModel tables, engine, migrations |
| `core/gamification/` | XP, levels, missions |
| `dashboard/` | Streamlit app entry point |
| `dashboard/tabs/` | 7 tab modules |
| `dashboard/components/` | Reusable UI components |
| `scrapers/` | Shopee, Amazon, Enjoei, MercadoLivre, Magalu, Shein |
| `docs/` | Project plan and status |

## Key Files

- `dashboard/app.py` — Streamlit entry point
- `dashboard/tabs/anuncios.py` — Product management (largest module)
- `core/llm_client.py` — LLM multi-provider with Gemini fallback
- `core/database/engine.py` — DB initialization (CWD-relative path!)
- `scrapers/shopee_scraper.py` — Shopee price fetching (Tavily + Firecrawl)

## Critical Rules

1. **DB location**: `database.db` lives at **project root**, NOT in `data/`. The `engine.py` uses a relative path, so **always run from project root**.
2. **Never commit** `.env` or `database.db` (gitignored).
3. **Component imports** must be **local** (inside the function), not at module top.
4. **Scraper prices can be zero** — always validate before using.
5. **`select()` import**: Every file using `session.exec(select(...))` must `from sqlmodel import select`.
6. **No Playwright** — removed permanently.

## Running

```bash
# From project root (required for DB path)
streamlit run dashboard/app.py
```

Or double-click `run_app.bat` (Windows).

## DB Location (common mistake)

The DB path is documented incorrectly in some places. Reality:

- **DB is at:** project root (`database.db`)
- **NOT at:** `data/database.db` (that folder is only for CSVs and AGENTS.md)
- `engine.py` creates DB with a **CWD-relative path** — launching from the wrong directory creates a phantom empty DB

## Import Pattern

```python
from core.database.engine import get_session
from core.database.models import Product
from sqlmodel import select

session = next(get_session())
products = session.exec(select(Product)).all()
```

## Technical Quirks

- **Module-level side effects**: Importing `core/config.py` reads `.env`, `engine.py` creates the SQLAlchemy engine, `llm_client.py` instantiates the LLM client — all before `st.set_page_config()`.
- **No `__init__.py`** in most packages — works due to Streamlit's CWD-based path resolution but fragile.
- **Session pattern**: `session = next(get_session())` — some callers don't close explicitly.
- **LLM fallback**: When primary provider fails and `GOOGLE_API_KEY` exists, automatically falls back to Gemini.
- **`settings_view.py` bug**: Calls `llm_client.setup_provider()` but method is actually `_setup_provider()` — will raise `AttributeError` at runtime.
- **Duplicate `MARKETPLACE_LABELS`**: Defined in both `core/competitor_service.py` (with emojis) and `scrapers/__init__.py` (without).
