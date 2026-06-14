# Scrapers — Market Data Collection

## Overview
Scraping module for price monitoring and competitor analysis. Uses **Tavily Search API** + **Firecrawl Crawl API** exclusively (Playwright/Chromium permanently removed).

## Files

| File | Purpose |
|------|---------|
| `base_scraper.py` | Abstract `BaseScraper` class (inherited by all) |
| `shopee_scraper.py` | `ShopeeScraper`: Shopee search via Tavily + Firecrawl |
| `amazon_scraper.py` | `AmazonScraper`: Amazon Brazil scraper (HTTP + BeautifulSoup) |
| `enjoei_scraper.py` | `EnjoeiScraper`: HTTP API + Tavily fallback |
| `web_scraper.py` | Generic `WebScraper`: Tavily search for any marketplace. Exports factory `create_web_scraper(marketplace)` for custom marketplace scrapers |
| `__init__.py` | Exports `SCRAPER_MAP` (dict marketplace→class), `MARKETPLACES` (sorted keys), `MARKETPLACE_LABELS`. Defines 3 `WebScraper` subclasses (`MercadoLivreScraper`, `MagaluScraper`, `SheinScraper`) — total **6 marketplaces** |

## Pipeline
```
Dashboard/Agent → competitor_service.py → Scraper.search() → Tavily API / Firecrawl → Price list
                                                                        ↓
                                                           _match_with_ai()  ← Gemini/OpenRouter matching
                                                                        ↓
                                                        _save_results() → CompetitorListing
```

## CompetitorService Workflow (8 steps)

`CompetitorService` (in `core/competitor_service.py`) has **more behavior than basic scraping**:

1. **`search_competitors(product_id, marketplaces, keyword)`** — search competitors across N marketplaces
2. **`_build_search_keyword(product)`** — concatenates `title + keywords`, max 100 chars
3. **`_match_with_ai(product, results)`** — LLM classifies each result as match (`is_match=true/false`) with `confidence_score` ("alto"/"médio"/"baixo"/"nao_match"). **Requires Gemini/OpenRouter** — without it, all results have `confidence_score=NULL` (not filtered)
4. **`_save_results(product_id, results, session)`** — persists to `CompetitorListing`; auto-skips items with `confidence_score == "nao_match"`
5. **`get_comparison_data(product_id)`** — returns list with `price_diff` and `price_diff_pct` calculated
6. **`confirm_match(listing_id, is_match)`** — manual review workflow: `is_match=False` deletes listing; `is_match=True` forces `confidence_score="alto"`
7. **`get_competitiveness_badge(product_id)`** — returns `dict` with `status` ∈ {"mais_barato", "abaixo_media", "na_media", "acima_media", "sem_dados"} + `label` + `color`
8. **`clear_listings(product_id)`** — deletes ALL listings for a product

## How to Use
```python
from scrapers.shopee_scraper import ShopeeScraper
scraper = ShopeeScraper()
results = scraper.search("polivitaminico AZ+")
for r in results:
    print(r.title, r.price, r.seller)
```

## Known Limitations
- **Prices can be zero** when Tavily doesn't return price in listing
- **`site:shopee.com.br` filter** helps but doesn't guarantee 100%
- Shopee has aggressive anti-bot — Firecrawl is fallback when Tavily fails
- Tavily has rate limits (depends on plan)
- **No LLM configured** → AI matching disabled, all results become listings with `confidence_score=NULL`. Can pollute DB with junk. Pre-validate with `Config.LLM_ENABLED`.

## Technical Quirks

- **Duplicate `MARKETPLACE_LABELS`**: Defined in both `core/competitor_service.py` (with emojis) and `scrapers/__init__.py` (without). Maintenance hazard.
- Three marketplaces (MercadoLivre, Magalu, Shein) are thin `WebScraper` subclasses with only a marketplace name override

## Dependencies
- `.env` — TAVILY_API_KEY, FIRECRAWL_API_KEY
- `core/competitor_service.py` — orchestrates scrapers
- `core/database/models.py` — CompetitorListing (persists results)
