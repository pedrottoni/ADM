# 🚀 ADM — Shopee Growth Quest

## Project Context
Dashboard Streamlit for managing a Shopee store (health/supplements niche — Nutri Active, DailyLife). Monolithic app refactored into module-per-tab architecture.

## Tech Stack
- **Python 3.11** + Streamlit + SQLModel + SQLite
- **LLM:** google.genai (Gemini) + OpenAI-compatible (OpenRouter, NVIDIA)
- **Scraping:** Tavily Search API + Firecrawl Crawl API (NO Playwright)
- **Host:** Windows (git-bash)

## Navigation (read AGENTS.md first, NOT the raw files)
```
Root AGENTS.md  →  maps all modules
agents/AGENTS.md        →  AI agents
core/AGENTS.md          →  core services
core/database/AGENTS.md →  DB models & engine
dashboard/AGENTS.md     →  Streamlit UI
dashboard/tabs/AGENTS.md →  per-tab modules
scrapers/AGENTS.md      →  price monitoring
docs/AGENTS.md          →  planning docs
```

## Key Files
- `dashboard/app.py` — Streamlit entry point
- `dashboard/tabs/anuncios.py` — Product management (the biggest module)
- `core/llm_client.py` — LLM multi-provider with fallback
- `scrapers/shopee_scraper.py` — Shopee price fetching (Tavily + Firecrawl)

## Critical Rules
1. **Read the AGENTS.md** of the relevant folder BEFORE opening source files
2. **NO Playwright/Chromium** — removed permanently
3. **NO committing** `.env` or `database.db`
4. **Component imports** (`dashboard/components/`) stay LOCAL inside functions
5. **Scraper prices can be zero** — validate before using
6. **DB is SQLite** at `data/database.db`

## Entry Point
```bash
streamlit run dashboard/app.py
```
