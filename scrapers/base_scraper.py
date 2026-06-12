from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
import random
import time


class BaseScraper(ABC):
    marketplace: str = "base"

    def __init__(self):
        self._request_count = 0
        self._max_requests = 50

    @abstractmethod
    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        pass

    @abstractmethod
    def get_product_details(self, url: str) -> Optional[Dict]:
        pass

    def _http_get(self, url: str, headers: Optional[Dict] = None, cookies: Optional[Dict] = None, timeout: int = 30) -> Optional[httpx.Response]:
        self._rate_limit()
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if headers:
            default_headers.update(headers)
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                resp = client.get(url, headers=default_headers, cookies=cookies)
                self._request_count += 1
                return resp
        except Exception as e:
            print(f"❌ Erro HTTP GET {url}: {e}")
            return None

    def _rate_limit(self):
        delay = random.uniform(2.0, 5.0)
        time.sleep(delay)
        if self._request_count >= self._max_requests:
            print(f"⚠️ [{self.marketplace}] Limite de requests atingido. Cooldown...")
            time.sleep(random.uniform(30, 60))
            self._request_count = 0

    def _parse_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0
        cleaned = price_str.replace("R$", "").replace("$", "").strip()
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _parse_price_cents(self, price_cents: int) -> float:
        return price_cents / 100.0 if price_cents else 0.0
