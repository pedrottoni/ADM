# 🚀 ADM — Shopee Growth Quest (Hermes Navigation Map)

## Visão Geral do Projeto
Dashboard Streamlit para gestão de loja Shopee (niche saúde/bem-estar/suplementos). Gerencia catálogo, precificação, concorrência, finanças e atendimento, com suporte de IA multi-provider.

**Stack:** Streamlit + SQLModel + SQLite + Google Gemini / OpenRouter + Tavily + Firecrawl

---

## 📂 Mapa de Módulos (AGENTS.md)

| Pasta | AGENTS.md | O que contém |
|-------|-----------|-------------|
| **[`agents/`](./agents/AGENTS.md)** | ✅ | 5 agentes IA: Product, Finance, Ads, Customer + Base |
| **[`core/`](./core/AGENTS.md)** | ✅ | Config, LLMClient, CompetitorService, SalesService |
| ↳ `core/database/` | ✅ | Models (9 tabelas), Engine, Migrations |
| ↳ `core/gamification/` | ✅ | Engine de XP, níveis, missões |
| **[`dashboard/`](./dashboard/AGENTS.md)** | ✅ | App Streamlit (entry point) |
| ↳ `dashboard/tabs/` | ✅ | 7 tabs (Resumo, Financeiro, Marketing, Atendimento, Anúncios, Concorrência, Config) |
| ↳ `dashboard/components/` | ✅ | Componentes reutilizáveis |
| **[`scrapers/`](./scrapers/AGENTS.md)** | ✅ | Shopee, Amazon, Enjoei scrapers (Tavily+Firecrawl) |
| **[`docs/`](./docs/AGENTS.md)** | ✅ | Plano mestre, status do projeto, design system |
| **[`DESIGN.md`](./DESIGN.md)** | ✅ | Design system Cupertino Dark — paleta, tokens, componentes, regras visuais |
| **[`scripts/`](./scripts/AGENTS.md)** | ✅ | Utilitários |
| **[`data/`](./data/AGENTS.md)** | ✅ | Banco SQLite + dados |
| **[`tests/`](./tests/AGENTS.md)** | ✅ | (vazio — preparado para testes) |

---

## 🧭 Navegação por Tarefa

| Se eu pedir... | Abra primeiro | Depois abra |
|---------------|---------------|-------------|
| "criar um anúncio" | `dashboard/tabs/anuncios.py` | `agents/product_agent.py` + `core/database/models.py` |
| "analisar finanças" | `dashboard/tabs/financeiro.py` | `agents/finance_agent.py` + `core/database/models.py` |
| "ver concorrência" | `dashboard/components/competitor_view.py` | `scrapers/shopee_scraper.py` + `core/competitor_service.py` |
| "responder cliente" | `dashboard/tabs/atendimento.py` | `agents/customer_agent.py` |
| "campanha marketing" | `dashboard/tabs/marketing.py` | `agents/ads_agent.py` |
| "configurar LLM" | `dashboard/components/settings_view.py` | `core/llm_client.py` + `.env` |
| "mexer no DB" | `core/database/models.py` | `core/database/engine.py` |
| "algo não funciona" | Leia o `AGENTS.md` das pastas envolvidas | Verifique `.env`, imports, e `core/config.py` |

---

## 📐 Arquitetura

```
Usuário → Dashboard (app.py) → Tabs (tabs/*.py) → Agents → LLMClient / Database / Scrapers
                                                              ↕
                                                          Tavily / Firecrawl (externo)
```

---

## ⚠️ Regras Importantes para o Hermes

1. **Sempre leia o AGENTS.md** da pasta antes de abrir vários arquivos — economiza contexto
2. **NUNCA commitar .env ou database.db** (estão no .gitignore)
3. **Imports de componentes** (`dashboard/components/`) devem ser **locais** (dentro da função), não no topo do módulo
4. **Preços podem vir zerados** dos scrapers — sempre valide antes de usar
5. **Se precisar de mais contexto**, leia os AGENTS.md relacionados antes de abrir arquivos
6. **`select()` do SQLModel** — toda vez que usar `session.exec(select(...))`, lembre de **importar `select`**: `from sqlmodel import select`. Sem isso dá `NameError`. (EXEMPLO em `core/database/AGENTS.md`)

---

> 📌 **Como este sistema funciona:**
> Cada pasta tem um `AGENTS.md` que descreve o que ela contém, quais arquivos abrir para cada tarefa, e as dependências. Quando você pedir uma tarefa, o Hermes deve ler o AGENTS.md relevante (não todos os arquivos da pasta) para entender o que fazer. Isso economiza contexto e acelera o desenvolvimento.
