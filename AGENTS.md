# ADM — Shopee Growth Quest

Streamlit dashboard for a Shopee health/supplements store (Nutri Active, DailyLife). Monolithic app with module-per-tab architecture.

**Stack:** Python 3.11 + Streamlit + SQLModel + SQLite + Google Gemini / OpenRouter + Tavily + Firecrawl

## Directory Map

| Module | What matters |
|--------|-------------|
| `dashboard/app.py` | **Entry point.** Streamlit `st.set_page_config()` first, then imports agents |
| `dashboard/tabs/` | 7 tabs, each has `render(user, agents)` — registered in `__init__.py` → `TAB_RENDERERS` |
| `dashboard/components/` | 3 components: `metric_card` (custom `st.html()`, not `st.metric()`), `competitor_view`, `settings_view` |
| `dashboard/main.py` | **DEPRECATED** — redirects to `app.py`. Don't use. |
| `core/` | Config, LLMClient, CompetitorService, SalesService |
| `core/database/` | 8 SQLModel tables, engine (CWD-relative path), migrations |
| `core/gamification/` | `engine.py` — quadratic level formula: `floor(sqrt(xp/100)) + 1` |
| `agents/` | 4 agents (Product, Finance, Ads, Customer) + BaseAgent |
| `scrapers/` | Shopee, Amazon, Enjoei + generic WebScraper for MercadoLivre/Magalu/Shein. **Tavily + Firecrawl only — no Playwright** |
| `data/` | CSVs only. **DB is NOT here.** |
| `docs/` | Project plan, status, streamlit DOM notes |
| `static/` (inside `dashboard/`) | `cupertino.css` — Dashdark X design system (`--dx-*` CSS variables) |

Both `dashboard/tabs/` and `scrapers/` have `__init__.py`. **Every other package lacks one** — Streamlit's CWD-based path resolution makes it work, but it's fragile.

Each module folder has its own `AGENTS.md`. Read the relevant one before editing files there.

## Run / Build

```bash
# ALWAYS from project root — DB path is relative to CWD
streamlit run dashboard/app.py
# Or double-click run_app.bat (auto-installs deps)
```

No linter, formatter, pre-commit, or CI configured. Code review is manual.

## Critical Gotchas (agents miss these repeatedly)

| # | Rule |
|---|------|
| 1 | **DB location:** `database.db` lives at **project root** because `engine.py` uses `sqlite_file_name = "database.db"` (relative to CWD). Running from another dir creates a phantom empty DB. |
| 2 | **`select()` import:** Every file calling `session.exec(select(...))` needs `from sqlmodel import select` — this is the most common `NameError`. |
| 3 | **Component imports:** Should be **local** (inside `render()`) except `anuncios.py` which imports `metric_card` at module top (older pattern). |
| 4 | **Scraper prices can be zero** — always validate before arithmetic. |
| 5 | **`settings_view.py` bug:** Line 57 calls `llm_client.setup_provider()` but the method is `_setup_provider()` (private). This raises `AttributeError` at runtime when saving API keys. |
| 6 | **Duplicate `MARKETPLACE_LABELS`:** Defined in both `core/competitor_service.py` (with material-icons) and `scrapers/__init__.py` (without). Edits to one must be mirrored. |
| 7 | **Module-level side effects:** `core/config.py` reads `.env`, `core/database/engine.py` creates the SQLAlchemy engine, `core/llm_client.py` instantiates the LLM client — all at import time, **before** `st.set_page_config()`. |

## LLM / AI

- **Multi-provider:** Gemini (`google-genai`), OpenRouter, NVIDIA. Provider set in `.env` via `LLM_PROVIDER`.
- **Fallback:** If primary provider fails AND `GOOGLE_API_KEY` is set, falls back to Gemini automatically with a `[System – Gemini Fallback]` prefix.
- **`LLM_ENABLED`** gate in `.env` controls whether the dashboard shows AI features.
- `Config.set_api_key()`, `set_llm_settings()`, `set_llm_enabled()` mutate in-memory AND persist to `.env`.
- **LLMClient session pattern:** `llm_client = LLMClient(provider, model_name)` — instantiated once at `llm_client.py` import time. The singleton is imported via `from core.llm_client import llm_client`.

## DB Session Pattern

```python
from core.database.engine import get_session
from core.database.models import Product
from sqlmodel import select

session = next(get_session())
products = session.exec(select(Product)).all()
# Some callers don't close explicitly — GC handles it.
```

## Design System (Dashdark X)

- **CSS:** `dashboard/static/cupertino.css` — loaded via `st.markdown(f"<style>{...}</style>", unsafe_allow_html=True)` in `app.py`
- **Tokens:** `var(--dx-*)` in `:root`. Never hardcode hex values.
- **Icons:** Use Streamlit **native** Material Symbols: `st.button(label, icon=":material/home:")`, `st.markdown(":material/rocket:")` — no custom HTML needed for icon-only usage.
- **`metric_card` component** uses `st.html()` instead of `st.metric()` — bypasses Streamlit's Emotion CSS-in-JS. Inline styles only (no CSS classes).
- **Emotion override:** Streamlit's Emotion cache injects styles AFTER our `<style>`. To override header backgrounds, use `<script>` via `st.markdown()` (see `app.py` lines 43-49 for the pattern).
- **`data-testid` values** are `stColumn`, `stVerticalBlock`, `stHorizontalBlock` — NOT `column`.
- **CSS `:has()` pitfall:** `:has(.marker)` matches ALL ancestors. Use `:has(> .parent:has(.marker))` to scope.

## Testing

```bash
pytest tests/
```

Mock Tavily/Firecrawl in tests. No integration test infrastructure. Tests dir is mostly empty.
