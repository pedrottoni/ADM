# Dashboard — Streamlit UI

## Overview
Frontend Streamlit app. Entry point in `app.py`, each tab is a separate module in `tabs/`.

## Files

| File | Purpose |
|------|---------|
| `app.py` | **Entry point**. Initializes DB, agents, sidebar. Creates 7 tabs and delegates rendering |
| `main.py` | **Deprecated**. Redirects to `app.py` |

## Sub-modules

### `tabs/` → [AGENTS.md](./tabs/AGENTS.md)
One `render(user, agents)` function per tab.

### `static/` (no own AGENTS.md)
- `static/cupertino.css` — **~720 lines CSS**, source of truth for Dashdark X design system (`--dx-*` palette, all component variants). Loaded by `app.py` at boot. **See [DESIGN.md](../../DESIGN.md) before modifying.**

### `components/` → [AGENTS.md](./components/AGENTS.md)
Reusable UI components (competitor view, settings, metric cards).

## How to Use

### Run the dashboard:
```bash
streamlit run dashboard/app.py
```

### Add a new tab:
1. Create `dashboard/tabs/new_tab.py` with `render(user, agents)`
2. Add to `TAB_RENDERERS` in `__init__.py`
3. Add label + key in `dashboard/app.py`

## Technical Quirks

- **CSS debug marker**: `app.py` injects a `<meta name="css-loaded">` tag with diagnostic data — dev-time aid left in production code
- **Module-level side effects**: Importing `app.py` triggers Config, engine, and LLM client initialization before `st.set_page_config()`
- **`st.set_page_config()`** must be the first Streamlit command — order matters

## Dependencies
- `agents/` — all tabs use agents
- `core/` — config, llm_client
- `core/database/` — models + engine
