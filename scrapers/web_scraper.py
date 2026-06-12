"""
Web Scraper — unificado via Tavily + Firecrawl para qualquer marketplace.

Usa Tavily para busca e Firecrawl para detalhes de produto.
Substitui os scrapers individuais de Mercado Livre, Magalu, Shein etc.
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
    if not text:
        return None
    m = re.search(r'R\$\s*([0-9]+[.,][0-9]{1,2})', text)
    if m:
        return float(m.group(1).replace('.', '').replace(',', '.'))
    m = re.search(r'([0-9]{1,3}(?:[.][0-9]{3})*[,][0-9]{2})', text)
    if m:
        val = m.group(1).replace('.', '').replace(',', '.')
        if 1 <= float(val) <= 99999:
            return float(val)
    return None


# Mapeamento: marketplace -> domínio para busca Tavily
MARKETPLACE_DOMAINS = {
    "mercadolivre": "mercadolivre.com.br",
    "magalu": "magazineluiza.com.br",
    "shein": "br.shein.com",
    "amazon": "amazon.com.br",
    "shopee": "shopee.com.br",
}

MARKETPLACE_LABELS = {
    "mercadolivre": "Mercado Livre",
    "magalu": "Magazine Luiza",
    "shein": "Shein",
    "amazon": "Amazon",
    "shopee": "Shopee",
}


class WebScraper(BaseScraper):
    """
    Scraper genérico que busca em qualquer marketplace via Tavily.
    marketplace deve ser uma das chaves de MARKETPLACE_DOMAINS.
    """

    def __init__(self, marketplace: str):
        self.marketplace = marketplace
        self.domain = MARKETPLACE_DOMAINS.get(marketplace, marketplace)
        self.label = MARKETPLACE_LABELS.get(marketplace, marketplace)
        super().__init__()

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        client = _get_tavily()
        if not client:
            print(f"⚠️ Tavily não configurado para {self.label}")
            return []

        search_query = f"site:{self.domain} \"{keyword}\""
        try:
            resp = client.search(
                query=search_query,
                search_depth="advanced",
                max_results=min(limit, 10),
                include_raw_content=True,
            )
        except Exception as e:
            print(f"❌ Tavily/{self.label} error: {e}")
            return []

        results = []
        for item in resp.get("results", []):
            parsed = self._parse_result(item)
            if parsed and parsed["competitor_price"] > 0:
                results.append(parsed)

        # Fallback: busca sem site:
        if len(results) < 3:
            try:
                resp2 = client.search(
                    query=f"\"{keyword}\" {self.label}",
                    search_depth="basic",
                    max_results=min(limit, 5),
                )
                for item in resp2.get("results", []):
                    parsed = self._parse_result(item)
                    if parsed and parsed["competitor_price"] > 0 and self.domain in parsed["product_url"]:
                        results.append(parsed)
            except Exception:
                pass

        print(f"✅ {self.label} (Tavily): {len(results)} resultados para '{keyword}'")
        return results[:limit]

    def _parse_result(self, item: Dict) -> Optional[Dict]:
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "") or ""
        raw = item.get("raw_content", "") or ""

        full_text = f"{title} {content} {raw}"
        price = _extract_price(full_text) or _extract_price(title)

        seller = ""
        for pat in [r'Vendido por\s*([^\n.]+)', r'by\s*([^\n,.]+)', r'Seller[:\s]+([^\n,.]+)']:
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                seller = m.group(1).strip()
                break

        rating = None
        m = re.search(r'(\d[.,]\d)\s*estrela', full_text.lower())
        if m:
            try:
                rating = float(m.group(1).replace(',', '.'))
            except ValueError:
                pass

        if not title or not url:
            return None

        return {
            "marketplace": self.marketplace,
            "competitor_title": title.strip(),
            "competitor_price": price or 0.0,
            "competitor_seller": seller,
            "price_before_discount": None,
            "shipping_cost": None,
            "product_url": url,
            "marketplace_id": None,
            "rating": rating,
            "sold_count": None,
            "seller_location": "",
            "confidence_score": None,
        }

    def get_product_details(self, url: str) -> Optional[Dict]:
        """Tenta Firecrawl para detalhes."""
        app = _get_firecrawl()
        if not app:
            return None
        try:
            result = app.scrape_url(url, formats=["markdown"])
            content = result.markdown if hasattr(result, 'markdown') and result.markdown else ""
            title = ""
            m = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
            if m:
                title = m.group(1).strip()
            price = _extract_price(content)
            return {
                "marketplace": self.marketplace,
                "competitor_title": title or "",
                "competitor_price": price or 0.0,
                "competitor_seller": "",
                "product_url": url,
            }
        except Exception as e:
            print(f"⚠️ Firecrawl/{self.label} error: {e}")
            return None


# Factory function
def create_web_scraper(marketplace: str) -> WebScraper:
    """Cria WebScraper configurado para o marketplace."""
    return WebScraper(marketplace)
