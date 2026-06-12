from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    marketplace = "amazon"
    BASE_URL = "https://www.amazon.com.br"

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        search_url = f"{self.BASE_URL}/s?k={keyword.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
            "Referer": "https://www.amazon.com.br/",
        }

        resp = self._http_get(search_url, headers=headers)
        if not resp or resp.status_code != 200:
            print(f"⚠️ Amazon retornou status {resp.status_code if resp else 'None'}")
            return []

        return self._parse_search_results(resp.text, limit)

    def _parse_search_results(self, html: str, limit: int) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        items = soup.select("div[data-component-type='s-search-result']")
        if not items:
            items = soup.select(".s-result-item")

        for item in items[:limit]:
            try:
                result = self._parse_item(item)
                if result and result["competitor_price"] > 0:
                    results.append(result)
            except Exception as e:
                continue

        return results

    def _parse_item(self, item) -> Optional[Dict]:
        title_el = item.select_one("h2 a span, .a-text-normal")
        price_whole = item.select_one(".a-price .a-price-whole")
        price_fraction = item.select_one(".a-price .a-price-fraction")
        original_price_el = item.select_one(".a-text-price .a-offscreen")
        link_el = item.select_one("h2 a")
        rating_el = item.select_one(".a-icon-star-small .a-icon-alt")
        reviews_el = item.select_one(".a-size-small .a-link-normal .a-size-base")
        shipping_el = item.select_one(".a-color-base .a-spacing-top-mini")

        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            return None

        price = 0.0
        if price_whole:
            whole = price_whole.get_text(strip=True).replace(".", "").replace(",", "").replace("\xa0", "")
            frac = price_fraction.get_text(strip=True) if price_fraction else "0"
            try:
                price = float(f"{whole}.{frac}")
            except ValueError:
                price = 0.0

        original_price = None
        if original_price_el:
            original_price = self._parse_price(original_price_el.get_text(strip=True))

        href = link_el.get("href", "") if link_el else ""
        url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

        rating = None
        if rating_el:
            try:
                rating_text = rating_el.get_text(strip=True)
                import re
                match = re.search(r"(\d+[.,]\d+)", rating_text)
                if match:
                    rating = float(match.group(1).replace(",", "."))
            except Exception:
                pass

        asin = ""
        if item.get("data-asin"):
            asin = item["data-asin"]

        has_free_shipping = False
        if shipping_el:
            shipping_text = shipping_el.get_text(strip=True).lower()
            has_free_shipping = "frete grátis" in shipping_text or "free shipping" in shipping_text or "grátis" in shipping_text

        return {
            "marketplace": self.marketplace,
            "competitor_title": title,
            "competitor_price": price,
            "competitor_seller": "",
            "price_before_discount": original_price if original_price and original_price > price else None,
            "shipping_cost": 0.0 if has_free_shipping else None,
            "product_url": url,
            "marketplace_id": asin,
            "rating": rating,
            "sold_count": None,
            "seller_location": "",
            "confidence_score": None,
        }

    def get_product_details(self, url: str) -> Optional[Dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
        resp = self._http_get(url, headers=headers)
        if not resp or resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one("#productTitle")
        price_el = soup.select_one(".a-price .a-offscreen")

        return {
            "competitor_title": title.get_text(strip=True) if title else "",
            "competitor_price": self._parse_price(price_el.get_text(strip=True)) if price_el else 0.0,
            "competitor_seller": "",
            "product_url": url,
            "marketplace": self.marketplace,
        }
