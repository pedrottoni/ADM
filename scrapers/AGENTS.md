# 🕷️ Scrapers — Coleta de Dados de Mercado

## Visão Geral
Módulo de scraping para monitoramento de preços e concorrência. Usa **Tavily Search API** + **Firecrawl Crawl API** exclusivamente (Playwright/Chromium foram removidos).

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `base_scraper.py` | Classe abstrata `BaseScraper` (herdada por todos) |
| `shopee_scraper.py` | `ShopeeScraper`: busca Shopee via Tavily + Firecrawl |
| `amazon_scraper.py` | `AmazonScraper`: scraper Amazon Brasil (HTTP + BeautifulSoup) |
| `enjoei_scraper.py` | `EnjoeiScraper`: API HTTP + Tavily fallback |
| `web_scraper.py` | `WebScraper` genérico: Tavily Search genérico p/ qualquer marketplace. Exporta factory `create_web_scraper(marketplace)` para criar scraper de marketplace custom |
| `__init__.py` | Exporta `SCRAPER_MAP` (dict marketplace→classe), `MARKETPLACES` (lista ordenada das keys), `MARKETPLACE_LABELS`. Define 3 subclasses de `WebScraper` (`MercadoLivreScraper`, `MagaluScraper`, `SheinScraper`) — total **6 marketplaces disponíveis** |

## Pipeline
```
Dashboard/Agent → competitor_service.py → Scraper.search() → Tavily API / Firecrawl → Lista de preços
                                                                       ↓
                                                          _match_with_ai()  ← Gemini/OpenRouter matching
                                                                       ↓
                                                       _save_results() → CompetitorListing
```

## ⚠️ Workflow de Concorrência (detalhado)

`CompetitorService` (em `core/competitor_service.py`) tem **mais comportamento do que o scrape básico**:

1. **`search_competitors(product_id, marketplaces, keyword)`** — busca concorrentes em N marketplaces
2. **`_build_search_keyword(product)`** — concatena `title + keywords`, máximo 100 chars
3. **`_match_with_ai(product, results)`** — usa LLM pra classificar cada resultado como match (`is_match=true/false`) e dar `confidence_score` ("alto"/"médio"/"baixo"/"nao_match"). **Usa Gemini/OpenRouter** — sem ele, todos os resultados ficam sem `confidence_score` (não são filtrados depois).
4. **`_save_results(product_id, results, session)`** — persiste em `CompetitorListing`; pula automaticamente items com `confidence_score == "nao_match"`
5. **`get_comparison_data(product_id)`** — retorna lista com `price_diff` e `price_diff_pct` calculados
6. **`confirm_match(listing_id, is_match)`** — workflow de revisão manual: `is_match=False` deleta a listing; `is_match=True` força `confidence_score="alto"`
7. **`get_competitiveness_badge(product_id)`** — retorna `dict` com `status` ∈ {"mais_barato", "abaixo_media", "na_media", "acima_media", "sem_dados"} + `label` + `color` ("green"/"orange"/"red"/"gray")
8. **`clear_listings(product_id)`** — deleta TODAS as listings de um produto

## Como Usar
```python
from scrapers.shopee_scraper import ShopeeScraper
scraper = ShopeeScraper()
results = scraper.search("polivitaminico AZ+")
for r in results:
    print(r.title, r.price, r.seller)
```

## ⚠️ Limitações Conhecidas
- **Preços podem vir zerados** quando Tavily não retorna preço na listagem
- **Filtro `site:shopee.com.br`** ajuda mas não garante 100%
- Shopee tem anti-bot agressivo — Firecrawl é fallback quando Tavily falha
- Tavily tem rate limits (depende do plano)
- **Sem LLM configurado** → matching IA fica desabilitado, e todos os resultados viram listings com `confidence_score=NULL`. Pode poluir o DB com lixo. Pré-valide com `CoreConfig.LLM_ENABLED`.

## Dependências
- `.env` — TAVILY_API_KEY, FIRECRAWL_API_KEY
- `core/competitor_service.py` — orquestra scrapers
- `core/database/models.py` — CompetitorListing (persiste resultados)
