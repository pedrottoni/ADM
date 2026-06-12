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
| `web_scraper.py` | `WebScraper` genérico: Tavily Search genérico p/ qualquer marketplace |
| `__init__.py` | Exporta `ShopeeScraper`, `AmazonScraper`, `EnjoeiScraper`, `WebScraper` |

## Pipeline
```
Dashboard/Agent → competitor_service.py → Scraper.search() → Tavily API / Firecrawl → Lista de preços
```

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

## Dependências
- `.env` — TAVILY_API_KEY, FIRECRAWL_API_KEY
- `core/competitor_service.py` — orquestra scrapers
- `core/database/models.py` — CompetitorListing (persiste resultados)
