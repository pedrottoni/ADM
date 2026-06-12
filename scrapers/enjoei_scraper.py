import httpx
import json
from typing import List, Dict, Optional
from scrapers.base_scraper import BaseScraper


class EnjoeiScraper(BaseScraper):
    marketplace = "enjoei"
    BASE_URL = "https://www.enjoei.com.br"
    API_BASE = "https://www.enjoei.com.br/api/v2"

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        results = self._search_api(keyword, limit)
        if results:
            return results
        return self._search_html(keyword, limit)

    def _search_api(self, keyword: str, limit: int = 20) -> List[Dict]:
        url = f"{self.API_BASE}/products"
        params = {
            "q": keyword,
            "per_page": min(limit, 24),
            "page": 1,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Referer": f"{self.BASE_URL}/busca?q={keyword}",
        }

        resp = self._http_get(url, headers=headers)
        if not resp or resp.status_code != 200:
            return []

        try:
            data = resp.json()
            products = data.get("products", [])
            results = []
            for product in products[:limit]:
                result = self._parse_api_product(product)
                if result:
                    results.append(result)
            return results
        except Exception as e:
            print(f"⚠️ Erro ao parsear API Enjoei: {e}")
            return []

    def _search_html(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Fallback: usa Tavily para busca no Enjoei."""
        from scrapers.web_scraper import WebScraper
        ws = WebScraper("enjoei")
        return ws.search(keyword, limit)

    def _parse_api_product(self, product: Dict) -> Optional[Dict]:
        try:
            price = product.get("price", 0.0)
            if isinstance(price, str):
                price = self._parse_price(price)
            original_price = product.get("original_price", product.get("suggested_price", None))
            if original_price and isinstance(original_price, str):
                original_price = self._parse_price(original_price)

            return {
                "marketplace": self.marketplace,
                "competitor_title": product.get("title", product.get("name", "")),
                "competitor_price": float(price),
                "competitor_seller": product.get("seller_name", product.get("brand", "")),
                "price_before_discount": float(original_price) if original_price and original_price > price else None,
                "shipping_cost": None,
                "product_url": f"{self.BASE_URL}/p/{product.get('slug', product.get('id', ''))}",
                "marketplace_id": str(product.get("id", "")),
                "rating": product.get("rating", None),
                "sold_count": product.get("sold_count", product.get("sold_quantity", None)),
                "seller_location": "",
                "confidence_score": None,
            }
        except Exception as e:
            print(f"⚠️ Erro ao parsear produto API Enjoei: {e}")
            return None

    def _parse_html_item(self, item_el) -> Optional[Dict]:
        try:
            title_el = item_el.query_selector(".product-card__title, .title")
            price_el = item_el.query_selector(".product-card__price, .price")
            link_el = item_el.query_selector("a")

            title = title_el.inner_text() if title_el else ""
            price = self._parse_price(price_el.inner_text()) if price_el else 0.0
            href = link_el.get_attribute("href") if link_el else ""
            url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

            return {
                "marketplace": self.marketplace,
                "competitor_title": title.strip(),
                "competitor_price": price,
                "competitor_seller": "",
                "price_before_discount": None,
                "shipping_cost": None,
                "product_url": url,
                "marketplace_id": None,
                "rating": None,
                "sold_count": None,
                "seller_location": "",
                "confidence_score": None,
            }
        except Exception:
            return None

    def get_product_details(self, url: str) -> Optional[Dict]:
        resp = self._http_get(url)
        if not resp or resp.status_code != 200:
            return None

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one("h1")
        price_el = soup.select_one("[data-product-price], .price")

        return {
            "competitor_title": title.get_text(strip=True) if title else "",
            "competitor_price": self._parse_price(price_el.get_text(strip=True)) if price_el else 0.0,
            "competitor_seller": "",
            "product_url": url,
            "marketplace": self.marketplace,
        }
