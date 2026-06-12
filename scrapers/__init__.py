from scrapers.shopee_scraper import ShopeeScraper
from scrapers.amazon_scraper import AmazonScraper
from scrapers.enjoei_scraper import EnjoeiScraper
from scrapers.web_scraper import WebScraper


# Subclasses de WebScraper com marketplace fixo
class MercadoLivreScraper(WebScraper):
    def __init__(self):
        super().__init__("mercadolivre")


class MagaluScraper(WebScraper):
    def __init__(self):
        super().__init__("magalu")


class SheinScraper(WebScraper):
    def __init__(self):
        super().__init__("shein")


# Marketplace que usam scrapers dedicados (HTTP/Tavily)
SCRAPER_MAP = {
    "shopee": ShopeeScraper,
    "amazon": AmazonScraper,
    "enjoei": EnjoeiScraper,
    "mercadolivre": MercadoLivreScraper,
    "magalu": MagaluScraper,
    "shein": SheinScraper,
}

# Marketplaces disponíveis para busca
MARKETPLACES = sorted(SCRAPER_MAP.keys())

# Labels amigáveis
MARKETPLACE_LABELS = {
    "shopee": "Shopee",
    "mercadolivre": "Mercado Livre",
    "amazon": "Amazon",
    "magalu": "Magazine Luiza",
    "shein": "Shein",
    "enjoei": "Enjoei",
}
