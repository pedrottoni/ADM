# Dashboard Components — Reusable UI

## Overview
UI components that can be used by multiple tabs or pages.

## Files

| File | Purpose |
|------|---------|
| `competitor_view.py` | `render_competitor_page(user_id)` — price monitor with scrapers for Shopee/Amazon/Enjoei/Mercado Livre/Magalu/Shein (6 marketplaces via `SCRAPER_MAP`) |
| `settings_view.py` | `render_settings_page()` — LLM provider config, API keys, AI toggle |
| `metric_card.py` | `metric_card(label, value, delta=None)` — custom KPI card via `st.html()` (bypasses Streamlit 1.56 CSS-in-JS). **Delta behavior:** accepts string with emoji prefix (🟢/🟡/🔴) — component auto-detects and renders arrow ▲/▼ + green/red color |

## How to Use
```python
from dashboard.components.competitor_view import render_competitor_page
render_competitor_page(user.id)
```

## Technical Quirks

- **`metric_card.py` delta convention ("Regra do Pedro")**: Delta should be purely graphical (emoji + arrow + number + %), zero text. This is a **caller convention**, not enforced by code — the component renders whatever string is passed.
- **`settings_view.py` bug**: Calls `llm_client.setup_provider()` but method is actually `_setup_provider()` (private). Will raise `AttributeError` at runtime.
- Uses `st.html()` to bypass Streamlit's internal CSS-in-JS (Emotion)

## Dependencies
- `core/competitor_service.py` — scraper access
- `core/llm_client.py` — toggle and configuration
- `scrapers/` — data collection
