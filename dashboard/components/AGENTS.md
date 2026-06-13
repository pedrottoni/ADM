# 🔲 Dashboard Components — Componentes Reutilizáveis

## Visão Geral
Componentes de UI que podem ser usados por múltiplas tabs ou páginas.

## Arquivos

|| Arquivo | Propósito |
|---------|-----------|
| `competitor_view.py` | `render_competitor_page(user_id)` — monitor de preços concorrência com scrapers Shopee/Amazon/Enjoei/Mercado Livre/Magalu/Shein (6 marketplaces via `SCRAPER_MAP`) |
| `settings_view.py` | `render_settings_page()` — configurações de LLM provider, API keys, toggle IA |
| `metric_card.py` | `metric_card(label, value, delta=None)` — card KPI custom via `st.html()` (bypassa CSS-in-JS interno do Streamlit 1.56). **Comportamento delta:** aceita string com emoji 🟢/🟡/🔴 no prefixo — componente detecta automaticamente e renderiza seta ▲/▼ + cor verde/vermelha. **Regra do Pedro**: delta é puramente gráfico (só emoji + seta + número + %), zero texto. |

## Como Usar
```python
from dashboard.components.competitor_view import render_competitor_page
render_competitor_page(user.id)
```

## Dependências
- `core/competitor_service.py` — acesso aos scrapers
- `core/llm_client.py` — toggle e configuração
- `scrapers/` — coleta de dados de concorrência
