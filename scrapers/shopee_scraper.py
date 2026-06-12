"""
Shopee Scraper — via Tavily + Firecrawl Search.

Como funciona:
  1. Tavily busca produtos Shopee por keyword (inclui preços de páginas de listagem)
  2. Firecrawl Search como fallback/ampliação
  3. Firecrawl Scrape para detalhes individuais de produto
  4. Preço extraído do conteúdo textual (R$ XX,XX)

Por que Tavily/Firecrawl e não scraping direto?
  - Shopee bloqueia Playwright, HTTP direto com cookies, e até Firecrawl scrape
  - Tavily e Firecrawl Search acessam o índice já crawleado da Shopee SEM bloqueio
  - Páginas de listagem (shopee.com.br/list/...) retornam preços completos

Limitação conhecida:
  - Produtos individuais (product/...) podem não ter preço no índice (meta description)
  - Nesse caso, o preço fica como 0.0 — ainda útil para título, URL e seller
"""

import os
import re
from typing import List, Dict, Optional
from scrapers.base_scraper import BaseScraper
from dotenv import load_dotenv

load_dotenv()


def _get_tavily():
    from tavily import TavilyClient
    k = os.getenv("TAVILY_API_KEY") or os.environ.get("TAVILY_API_KEY")
    return TavilyClient(api_key=k) if k else None


def _get_firecrawl():
    from firecrawl import FirecrawlApp
    k = os.getenv("FIRECRAWL_API_KEY") or os.environ.get("FIRECRAWL_API_KEY")
    return FirecrawlApp(api_key=k) if k else None


def _extract_price(text: str) -> Optional[float]:
    """Extrai o primeiro preço em reais de um texto."""
    if not text:
        return None
    # R$ XX,XX  (vírgula decimal)
    m = re.search(r'R\$\s*([0-9]{1,3}(?:[.][0-9]{3})*[,][0-9]{2})', text)
    if m:
        return float(m.group(1).replace('.', '').replace(',', '.'))
    # R$ XX.XX  (ponto decimal, US-style)
    m = re.search(r'R\$\s*([0-9]+[.][0-9]{2}(?![0-9]))', text)
    if m:
        return float(m.group(1))
    # Número solto no formato brasileiro (ex: "26,90" em "R$26,90.")
    m = re.search(r'R\$\s*([0-9]+[,][0-9]{2})', text)
    if m:
        return float(m.group(1).replace(',', '.'))
    # Último recurso: número solto com vírgula decimal entre 1 e 9999
    m = re.search(r'(?<!\d)([1-9][0-9]{0,2}(?:[.][0-9]{3})*[,][0-9]{2})(?!\d)', text)
    if m:
        val = m.group(1).replace('.', '').replace(',', '.')
        if 1 <= float(val) <= 99999:
            return float(val)
    return None


def _extract_rating(text: str) -> Optional[float]:
    """Extrai rating estrela de texto."""
    m = re.search(r'(\d[.,]\d)\s*estrela', text.lower())
    if m:
        try:
            return float(m.group(1).replace(',', '.'))
        except ValueError:
            pass
    return None


def _extract_seller(text: str) -> str:
    """Extrai nome do vendedor."""
    for pat in [
        r'Vendido por\s*([^\n,.]+)',
        r'by\s*([^\n,.]+)',
        r'Seller[:\s]+([^\n,.&]+)',
        r'Loja[:\s]+([^\n,.&]+)',
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def _extract_ids(url: str) -> tuple:
    """Extrai (shop_id, item_id) de URL Shopee."""
    m = re.search(r'/product/(\d+)/(\d+)', url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r'i\.(\d+)\.(\d+)', url)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def _parse_to_schema(title: str, url: str, content: str, marketplace: str = "shopee") -> Optional[Dict]:
    """Converte (title, url, content) em schema ADM."""
    if not title or not url:
        return None

    full_text = f"{title} {content}"
    price = _extract_price(full_text)
    seller = _extract_seller(full_text)
    rating = _extract_rating(full_text)
    shop_id, item_id = _extract_ids(url)

    return {
        "marketplace": marketplace,
        "competitor_title": title.strip(),
        "competitor_price": price or 0.0,
        "competitor_seller": seller,
        "price_before_discount": None,
        "shipping_cost": None,
        "product_url": url,
        "marketplace_id": f"{shop_id}.{item_id}" if shop_id and item_id else None,
        "rating": rating,
        "sold_count": None,
        "seller_location": "",
        "confidence_score": None,
    }


# ═══════════════════════════════════════════════════════════════════════
class ShopeeScraper(BaseScraper):
    marketplace = "shopee"
    BASE_URL = "https://shopee.com.br"

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Busca produtos Shopee via Tavily + Firecrawl Search."""
        results = []
        seen_urls = set()

        # ── 1. Tavily ──────────────────────────────────────────────
        client = _get_tavily()
        if client:
            try:
                resp = client.search(
                    query=f'site:shopee.com.br "{keyword}"',
                    search_depth="advanced",
                    max_results=min(limit + 5, 15),
                    include_raw_content=True,
                )
                for item in resp.get("results") or []:
                    url = item.get("url", "")
                    if url in seen_urls or "shopee.com.br" not in url:
                        continue
                    seen_urls.add(url)
                    parsed = _parse_to_schema(
                        title=item.get("title", ""),
                        url=url,
                        content=(item.get("content") or "") + " " + (item.get("raw_content") or ""),
                    )
                    if parsed:
                        results.append(parsed)
            except Exception as e:
                print(f"⚠️ Tavily error: {e}")

        # ── 2. Firecrawl Search (amplia resultados) ────────────────
        if len(results) < limit:
            app = _get_firecrawl()
            if app:
                try:
                    fc_result = app.search(
                        query=f"vitamina {keyword} shopee",
                        include_domains=["shopee.com.br"],
                        limit=min(limit, 5),
                    )
                    web_items = getattr(fc_result, 'web', [])
                    for item in web_items:
                        url = getattr(item, 'url', getattr(item, 'url', ''))
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        title = getattr(item, 'title', '')
                        desc = getattr(item, 'description', '') or ''
                        parsed = _parse_to_schema(title=title, url=url, content=desc)
                        if parsed and parsed["competitor_price"] > 0:
                            results.append(parsed)
                except Exception as e:
                    print(f"⚠️ Firecrawl search error: {e}")

        print(f"✅ Shopee: {len(results)} resultados para '{keyword}'")
        return results[:limit]

    def get_product_details(self, url: str) -> Optional[Dict]:
        """Tenta Firecrawl scrape. Shopee pode bloquear (página indisponível)."""
        app = _get_firecrawl()
        if app:
            try:
                result = app.scrape_url(url, formats=["markdown"])
                content = ""
                if hasattr(result, 'markdown') and result.markdown:
                    content = result.markdown
                elif hasattr(result, 'content') and result.content:
                    content = result.content

                if content and "Página indisponível" in content:
                    print("⚠️ Shopee bloqueou Firecrawl scrape (login necessário)")
                    return None

                title = ""
                m = re.search(r'^#\s*(.+)$', content, re.MULTILINE) if content else None
                if m:
                    title = m.group(1).strip()
                price = _extract_price(content)
                shop_id, item_id = _extract_ids(url)
                return {
                    "marketplace": self.marketplace,
                    "competitor_title": title or "",
                    "competitor_price": price or 0.0,
                    "competitor_seller": "",
                    "product_url": url,
                    "marketplace_id": f"{shop_id}.{item_id}" if shop_id and item_id else None,
                }
            except Exception as e:
                print(f"⚠️ Firecrawl detail: {e}")

        return None
