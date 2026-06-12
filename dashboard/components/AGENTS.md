# 🔲 Dashboard Components — Componentes Reutilizáveis

## Visão Geral
Componentes de UI que podem ser usados por múltiplas tabs ou páginas.

## Arquivos

|| Arquivo | Propósito |
|---------|-----------|
| `competitor_view.py` | `render_competitor_page(user_id)` — monitor de preços concorrência com scrapers Shopee/Amazon/Enjoei |
| `settings_view.py` | `render_settings_page()` — configurações de LLM provider, API keys |
| `metric_card.py` | `metric_card(label, value, delta=None)` — card KPI custom via st.html() (bypassa CSS-in-JS interno do Streamlit) |

## Como Usar
```python
from dashboard.components.competitor_view import render_competitor_page
render_competitor_page(user.id)
```

## Dependências
- `core/competitor_service.py` — acesso aos scrapers
- `core/llm_client.py` — toggle e configuração
- `scrapers/` — coleta de dados de concorrência
