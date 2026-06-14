# Dashboard Tabs — Per-Tab Rendering

## Overview
Each file exports a `render(user, agents)` function that draws one dashboard tab. Loaded by `app.py` via `TAB_RENDERERS`.

## Tabs

| File / Key | Label | What it does |
|------------|-------|--------------|
| `resumo.py` | Resumo | KPIs, top sales, XP progress, active missions, stock alerts |
| `financeiro.py` | Financeiro | Treasury: financial summary, record sales, expenses, upload data |
| `marketing.py` | Central de Marketing | Campaign analysis, Midjourney prompt generator |
| `atendimento.py` | Atendimento | Response generator (formal/casual/empathetic), sentiment analysis |
| `anuncios.py` | Meus Anuncios | **Largest tab**. Product CRUD, bulk upload, kits, stock, CSV import |
| `concorrencia.py` | Concorrencia | Price monitor (delegates to `competitor_view.py`) |
| `configuracoes.py` | Configuracoes | LLM provider, API keys (delegates to `settings_view.py`) |

> **Note**: Real label is "Central de Marketing" not just "Marketing", per `app.py` TAB_LABELS.

## How to Use

### "Meus Anuncios" (product management):
1. **Main file:** `dashboard/tabs/anuncios.py`
2. **Data models:** `core/database/models.py` (Product, ProductVariation, InventoryItem, ProductComponent)
3. **Services:** `core/sales_service.py`, `agents/product_agent.py`

### "Financeiro":
1. Open `dashboard/tabs/financeiro.py`
2. Open `core/database/models.py` (Transaction)
3. Open `agents/finance_agent.py`

### Add new tab:
1. Create file with `def render(user, agents):`
2. Add to `TAB_RENDERERS` in `__init__.py`
3. Add to `dashboard/app.py` (tab_labels + tab_keys)

## Rules
- **NEVER** import `dashboard/components/` at module level (only inside render function)
- Access agents via `agents["finance_agent"]` etc.
- Keep imports local inside the function for rare imports
