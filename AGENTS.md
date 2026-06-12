# ADM - Shopee Growth Quest

Projeto Streamlit para gestão de loja virtual Shopee (BR). Controla anúncios, estoque físico, finanças, concorrência e atendimento.

---

## Stack

| Camada    | Tecnologia                                     |
|-----------|------------------------------------------------|
| Frontend  | Streamlit (`dashboard/main.py`)                |
| ORM/DB    | SQLModel + SQLite (`database.db` na raiz)      |
| LLM       | google-generativeai / openai (openrouter/nvidia) |
| Scraping  | httpx + Playwright + BeautifulSoup             |
| Gráficos  | Plotly                                         |
| Tabelas   | pandas + Streamlit data_editor                 |

**Dependências:** `pip install -r requirements.txt` + `playwright install`

---

## Como Rodar

```bash
streamlit run dashboard/main.py --server.headless true
# ou: run_app.bat (roda pip install + streamlit)
```

DB e usuário Admin são criados automaticamente no primeiro acesso.

---

## Arquitetura

### Dashboard (`dashboard/main.py`)

7 tabs inline (sem `dashboard/pages/`), tudo no mesmo arquivo ~1293 linhas:

| Tab | Nome | Conteúdo |
|-----|------|----------|
| 1 | 🏠 **Resumo** | KPIs (receita, lucro, margens), top produtos, low-stock alerts, missões/XP |
| 2 | 💰 **Financeiro** | Subtabs: Visão Geral, Registrar Venda, Despesas. COGS, gráficos, data_editor de transações, zona de perigo (reset) |
| 3 | 📢 **Central de Marketing** | Análise de campanha (ROAS/CTR), gerador de prompts de imagem (Midjourney) |
| 4 | 🤝 **Customer Hero** | Gerador de respostas (3 tons), análise de sentimento de reviews |
| 5 | 📦 **Gestão de Anúncios** | CRUD de produtos, upload em massa, componentes de kit, estoque, export CSV |
| 6 | 🔍 **Concorrência** | Monitor de preços (Shopee, ML, Amazon, etc.), login em marketplace |
| 7 | ⚙️ **Configurações** | Provedor/modelo LLM, API keys, sistema |

**LLM toggle** no topo da página — `st.toggle` persiste em `.env` via `Config.set_llm_enabled()`.

### Componentes (`dashboard/components/`)
- `competitor_view.py` — `CompetitorView`: gerenciamento de sessões marketplace + comparação de preços
- `settings_view.py` — `SettingsView`: seletor de provider LLM, inputs de API key

### Agentes (`agents/`)

ABC → `BaseAgent` (agent_name + log), 4 implementações:

| Arquivo | Classe | Métodos principais |
|---------|--------|-------------------|
| `finance_agent.py` | `FinanceAgent` | manage_transaction, add/delete/update_transaction, clear_all, reset_inventory, generate_deep_analysis, get_all_products, get_low_stock_items, **process_upload** (CSV/XLSX → LLM → preview) |
| `product_agent.py` | `ProductAgent` | get_all_products/inventory_items/get_product_components, add_inventory_item, add/remove_component, generate_listing (LLM), generate_image_prompt (LLM), generate_mass_upload_csv |
| `ads_agent.py` | `AdsAgent` | generate_keywords (LLM), analyze_ad_performance (ROAS/CTR + LLM advice) |
| `customer_agent.py` | `CustomerAgent` | generate_response (3 tones), analyze_sentiment |

Subdiretórios `agents/finance_agent/`, `agents/ads_agent/`, `agents/customer_agent/` estão **vazios** — só os `.py` na raiz de `agents/` são o código real.

### LLM (`core/llm_client.py`)

- Singleton `LLMClient(provider, model_name)` — instância global `llm_client`
- Lê API keys de `.env`: `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`
- Fallback automático: se provider primário falhar E chave Gemini existir, tenta Gemini
- `LLM_ENABLED` deve ser a string `"true"` no `.env`
- Método principal: `generate_content(prompt, use_search=False)` → `str`

Provider | Client | Modelo padrão | Base URL
---------|--------|---------------|---------
gemini | `google.generativeai` | `gemini-2.5-flash` | n/a (SDK nativo)
openrouter | `openai.OpenAI` | `google/gemini-2.5-flash` | `https://openrouter.ai/api/v1`
nvidia | `openai.OpenAI` | `z-ai/glm4.7` | `https://integrate.api.nvidia.com/v1`

Config salva em `.env` via `Config.set_llm_settings()` — persiste entre restart.

### Scraping (`scrapers/`)

Duas camadas de scraping:

**1. `BaseScraper`** (ABC, `scrapers/base_scraper.py`):
- httpx-based, sem browser
- Rate-limit: 2-5s aleatório entre requests, 50 req/session → cooldown 30-60s
- 6 scrapers via `SCRAPER_MAP` (`scrapers/__init__.py`):

| Chave | Classe | Marketplace |
|-------|--------|-------------|
| shopee | ShopeeScraper | Shopee |
| mercadolivre | MercadoLivreScraper | Mercado Livre |
| amazon | AmazonScraper | Amazon |
| magalu | MagaluScraper | Magazine Luiza |
| shein | SheinScraper | Shein |
| enjoei | EnjoeiScraper | Enjoei |

**2. `BrowserEngine`** (singleton, `core/browser_engine.py`):
- Playwright Chromium (headless ou não)
- Login manual com save de cookies em `browser_session/<marketplace>.json`
- Rate-limit: ~3s entre requests (min 2.5-5s), 50 req/session, 30-60s cooldown
- Stealth JS injection para evitar detecção

### Core
- `core/config.py` — lê `.env`, `Config.set_key()`, `Config.set_llm_settings()`
- `core/database/models.py` — todos os modelos SQLModel
- `core/database/migrations/` — 4 scripts manuais (executar explicitamente)
- `core/sales_service.py` — `SalesService`: registra venda, abate estoque, fuzzy match (threshold 0.55)
- `core/competitor_service.py` — `CompetitorService` (singleton): busca preços em 6 marketplaces, matching por LLM
- `core/gamification/engine.py` — `GamificationEngine`: cálculo de level (`floor(sqrt(xp/100)) + 1`), `add_xp()`
- `core/browser_engine.py` — singleton do Playwright

---

## Database (SQLModel, SQLite)

### Modelos (`core/database/models.py`)

**`User`** — `id`, `username`, `level`(1), `xp`(0), `joined_at`(utcnow), missions[]
- **Não tem** campo `email` — o identificador é `username`

**`Mission`** — `id`, `title`, `description`, `xp_reward`, `is_completed`, `completed_at`, `created_at`, `user_id`(FK)

**`Transaction`** — `id`, `date`(datetime), `type`(INCOME/EXPENSE), `category`, `description`, `amount`(float), `product_id`(FK nullable), `quantity`(int), `user_id`(FK)
- Formato DD/MM/YYYY é esperado em CSV/exibição; o model armazena `datetime`

**`Product`** — Anúncio Shopee virtual. `id`, `title`(!= name), `description`, `price`, `supplier_price`, `stock`(int), `initial_stock`(100), `category`, `keywords`(comma-separated string, nullable), `sku`, `shopee_id`, `user_id`, `variations`[], `components`[], `competitor_listings`[]
- **Não tem** campos `cost`, `url`, ou `status` — diferente de versões anteriores
- Quantidade de kit codificada via `ProductComponent`, não no title

**`ProductVariation`** — `id`, `name`, `price`, `supplier_price`, `stock`, `sku`, `shopee_id`, `product_id`(FK)

**`InventoryItem`** — Item físico na prateleira. `id`, `name`, `supplier_price`, `stock`(int), `initial_stock`(100), `min_stock`(10), `user_id`
- **Não tem** campos `unit_name` ou `cost`

**`ProductComponent`** — Link Product → InventoryItem com quantidade. `id`, `product_id`(FK), `inventory_item_id`(FK), `quantity`(int, default=1)

**`CompetitorListing`** — `id`, `product_id`(FK), `marketplace`, `competitor_title`, `competitor_price`, `competitor_seller`, `our_price_at_time`, `price_before_discount`, `shipping_cost`, `product_url`, `marketplace_id`, `rating`, `sold_count`, `seller_location`, `is_confirmed_match`, `confidence_score`, `last_checked_at`

---

## Fluxos Críticos

### Venda → Abate de Estoque
1. `SalesService.process_income_batch()` recebe lista de vendas
2. `check_duplicate()`: mesma `date+description+amount+type=INCOME` já existe? Skip
3. `match_product()`: fuzzy match (`SequenceMatcher`, threshold 0.55) entre `description` e `Product.title`
4. `process_sale()`: decrementa `Product.stock`
5. Para cada `ProductComponent`: decrementa `InventoryItem.stock` por `component.quantity * sale_quantity`

### Upload CSV Financeiro
1. `FinanceAgent.process_upload()` lê CSV/XLSX
2. Envia dados para LLM via `llm_client.generate_content()` → JSON array de vendas → preview table
3. Usuário confirma → `SalesService.process_income_batch()` faz batch insert + abate estoque

### Geração de Listing
1. `ProductAgent.generate_listing(product_name, key_benefits, ingredients)` envia para LLM
2. LLM retorna formato: `TÍTULO: ... / DESCRIÇÃO: ... / KEYWORDS: ...`
3. `_parse_llm_response()` extrai os campos do texto bruto
4. Se `kit_details` presente em geração futura → cria InventoryItem + ProductComponent

---

## Gotchas

| # | Problema | Detalhe |
|---|----------|---------|
| 1 | `LLM_ENABLED` é string | Comparar com `"true"`, não `True`. Default no `.env` é `"false"` |
| 2 | Sem testes | Zero test infrastructure. `*.csv` e `*.xlsx` no gitignore — usar `.xls` ou `.tsv` pra trackear |
| 3 | Migrations manuais | `core/database/migrations/` deve ser executado explicitamente via `python .../migrate_*.py` |
| 4 | `browser_session/` gitignored | Cookies de login não persistem entre clones |
| 5 | Product usa `title` | O campo principal do Product é `title` (não `name`) |
| 6 | Kit qty via ProductComponent | Quantidade de kit é `ProductComponent.quantity`, **não** sufixo no title (sufixo ` - Nx` é só p/ display) |
| 7 | Subdirs agents vazios | `agents/finance_agent/`, `agents/ads_agent/`, `agents/customer_agent/` são pastas placeholder |
| 8 | `CompetitorListing` tabela | Nome real da tabela SQL é `competitorlisting` (lowercase, sem separador) |
| 9 | Streamlit rerun | Todo o script é re-executado a cada interação — só `session_state` persiste |
| 10 | `.env` tem chaves reais | Gitignored — `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `NVIDIA_API_KEY` |
| 11 | `.env` key naming | A env var usada é `GOOGLE_API_KEY` (não `GEMINI_API_KEY`) — `google.generativeai` lê `GOOGLE_API_KEY` por padrão |
