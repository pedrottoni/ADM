import json
from typing import List, Dict, Optional
from datetime import datetime
from sqlmodel import select, Session
from core.database.engine import get_session
from core.database.models import Product, CompetitorListing
from core.llm_client import llm_client
from scrapers import SCRAPER_MAP


MARKETPLACES = ["shopee", "mercadolivre", "amazon", "magalu", "shein", "enjoei"]

MARKETPLACE_LABELS = {
    "shopee": ":material/storefront: Shopee",
    "mercadolivre": ":material/shopping_cart: Mercado Livre",
    "amazon": ":material/package_2: Amazon",
    "magalu": ":material/local_offer: Magalu",
    "shein": ":material/checkroom: Shein",
    "enjoei": ":material/recycling: Enjoei",
}


class CompetitorService:

    def search_competitors(self, product_id: int, marketplaces: List[str] = None, keyword: str = None) -> List[Dict]:
        session = next(get_session())
        product = session.get(Product, product_id)
        if not product:
            return []

        if marketplaces is None:
            marketplaces = MARKETPLACES

        if keyword is None:
            keyword = self._build_search_keyword(product)
        our_price = product.price
        all_results = []

        for mp in marketplaces:
            scraper_cls = SCRAPER_MAP.get(mp)
            if not scraper_cls:
                continue
            try:
                scraper = scraper_cls()
                results = scraper.search(keyword, limit=20)
                for r in results:
                    r["our_price_at_time"] = our_price
                all_results.extend(results)
                print(f"✅ [{mp}] {len(results)} resultados para '{keyword}'")
            except Exception as e:
                print(f"❌ [{mp}] Erro na busca: {e}")

        if all_results and llm_client:
            all_results = self._match_with_ai(product, all_results)

        saved = self._save_results(product_id, all_results, session)
        session.close()
        return saved

    def _build_search_keyword(self, product: Product) -> str:
        parts = []
        if product.title:
            parts.append(product.title)
        if product.keywords:
            parts.append(product.keywords)
        combined = " ".join(parts)
        if len(combined) > 100:
            combined = combined[:100]
        return combined.strip()

    def _match_with_ai(self, product: Product, results: List[Dict]) -> List[Dict]:
        if not results:
            return results

        items_text = ""
        for i, r in enumerate(results[:15]):
            items_text += f"\n[{i+1}] Título: {r['competitor_title']} | Preço: R${r['competitor_price']:.2f} | Marketplace: {r['marketplace']}"

        prompt = f"""Você é um analista de mercado e-commerce. Analise se os resultados de busca são o MESMO PRODUTO ou um produto similar/diferente do produto de referência.

Produto de referência: "{product.title}"
Preço do nosso produto: R${product.price:.2f}

Resultados encontrados:{items_text}

Para cada resultado, responda em JSON válido (sem markdown, sem ```):
{{
  "matches": [
    {{"index": 1, "is_match": true/false, "confidence": "alto"/"médio"/"baixo", "reason": "breve explicação"}}
  ]
}}

Seja rigoroso: só marque como is_match=true se for claramente o mesmo produto ou versão muito similar (mesmo tipo, peso, sabor, marca). Kit com quantidade diferente pode ser match com confiança "médio"."""

        try:
            response = llm_client.generate_content(prompt)
            clean = response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            parsed = json.loads(clean)
            matches = {m["index"]: m for m in parsed.get("matches", [])}

            for i, r in enumerate(results[:15]):
                match_info = matches.get(i + 1)
                if match_info:
                    r["confidence_score"] = match_info.get("confidence", "baixo") if match_info.get("is_match") else "nao_match"
        except Exception as e:
            print(f"⚠️ Erro no matching IA: {e}")

        return results

    def _save_results(self, product_id: int, results: List[Dict], session: Session) -> List[Dict]:
        saved = []
        for r in results:
            if r.get("confidence_score") == "nao_match":
                continue
            listing = CompetitorListing(
                product_id=product_id,
                marketplace=r.get("marketplace", ""),
                competitor_title=r.get("competitor_title", ""),
                competitor_price=r.get("competitor_price", 0.0),
                competitor_seller=r.get("competitor_seller", ""),
                our_price_at_time=r.get("our_price_at_time", 0.0),
                price_before_discount=r.get("price_before_discount"),
                shipping_cost=r.get("shipping_cost"),
                product_url=r.get("product_url", ""),
                marketplace_id=r.get("marketplace_id"),
                rating=r.get("rating"),
                sold_count=r.get("sold_count"),
                seller_location=r.get("seller_location", ""),
                is_confirmed_match=False,
                confidence_score=r.get("confidence_score"),
                last_checked_at=datetime.utcnow(),
            )
            session.add(listing)
            saved.append(r)
        session.commit()

        for r in saved:
            if r.get("competitor_price", 0) > 0:
                r["price_diff"] = r["competitor_price"] - r["our_price_at_time"]
                r["price_diff_pct"] = ((r["competitor_price"] - r["our_price_at_time"]) / r["our_price_at_time"] * 100) if r["our_price_at_time"] > 0 else 0
            else:
                r["price_diff"] = 0
                r["price_diff_pct"] = 0

        return saved

    def get_comparison_data(self, product_id: int) -> List[Dict]:
        session = next(get_session())
        statement = (
            select(CompetitorListing)
            .where(CompetitorListing.product_id == product_id)
            .order_by(CompetitorListing.marketplace, CompetitorListing.competitor_price)
        )
        listings = session.exec(statement).all()
        results = []
        for l in listings:
            diff = l.competitor_price - l.our_price_at_time
            pct = (diff / l.our_price_at_time * 100) if l.our_price_at_time > 0 else 0
            results.append({
                "id": l.id,
                "marketplace": l.marketplace,
                "competitor_title": l.competitor_title,
                "competitor_price": l.competitor_price,
                "competitor_seller": l.competitor_seller,
                "our_price_at_time": l.our_price_at_time,
                "price_before_discount": l.price_before_discount,
                "shipping_cost": l.shipping_cost,
                "product_url": l.product_url,
                "rating": l.rating,
                "sold_count": l.sold_count,
                "seller_location": l.seller_location,
                "is_confirmed_match": l.is_confirmed_match,
                "confidence_score": l.confidence_score,
                "last_checked_at": l.last_checked_at,
                "price_diff": diff,
                "price_diff_pct": pct,
            })
        session.close()
        return results

    def confirm_match(self, listing_id: int, is_match: bool) -> bool:
        session = next(get_session())
        listing = session.get(CompetitorListing, listing_id)
        if not listing:
            session.close()
            return False
        if not is_match:
            session.delete(listing)
        else:
            listing.is_confirmed_match = True
            listing.confidence_score = "alto"
        session.commit()
        session.close()
        return True

    def get_competitiveness_badge(self, product_id: int) -> Dict:
        data = self.get_comparison_data(product_id)
        confirmed = [d for d in data if d["is_confirmed_match"]]
        if not confirmed:
            confirmed = data
        if not confirmed:
            return {"status": "sem_dados", "label": "Sem dados", "color": "gray"}

        our_price = confirmed[0]["our_price_at_time"] if confirmed else 0
        if our_price <= 0:
            return {"status": "sem_dados", "label": "Sem dados", "color": "gray"}

        competitor_prices = [d["competitor_price"] for d in confirmed if d["competitor_price"] > 0]
        if not competitor_prices:
            return {"status": "sem_dados", "label": "Sem dados", "color": "gray"}

        avg_price = sum(competitor_prices) / len(competitor_prices)
        min_price = min(competitor_prices)

        if our_price <= min_price:
            return {"status": "mais_barato", "label": ":material/emoji_events: Mais barato do mercado!", "color": "green"}
        elif our_price < avg_price:
            return {"status": "abaixo_media", "label": ":material/check_circle: Preço abaixo da média", "color": "green"}
        elif our_price <= avg_price * 1.1:
            return {"status": "na_media", "label": ":material/scale: Preço na média", "color": "orange"}
        else:
            return {"status": "acima_media", "label": ":material/warning_amber: Preço acima da média", "color": "red"}

    def clear_listings(self, product_id: int):
        session = next(get_session())
        statement = select(CompetitorListing).where(CompetitorListing.product_id == product_id)
        listings = session.exec(statement).all()
        for l in listings:
            session.delete(l)
        session.commit()
        session.close()


competitor_service = CompetitorService()
