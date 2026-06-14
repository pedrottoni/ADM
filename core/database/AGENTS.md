# Database — Models & Migrations

## Overview
Data layer using SQLModel + SQLAlchemy + SQLite.

## Files

| File | Purpose |
|------|---------|
| `models.py` | **8 tables**: User, Mission, Transaction, Product, ProductVariation, ProductComponent, InventoryItem, CompetitorListing |
| `engine.py` | `create_db_and_tables()`, `get_session()`, `initialize_default_user()`, engine singleton |
| `migrations/` | Incremental migration scripts (v0 → v1 → v2...) |

## Models

| Model | Table | Usage |
|-------|-------|-------|
| `User` | Store admin. Has XP, level, missions |
| `Product` | Shopee listings. title, price, supplier_price, sku, shopee_id, category (free string) |
| `ProductVariation` | Product variations (e.g. 30d, 60d) — name, price, supplier_price, stock, sku, shopee_id |
| `ProductComponent` | Bridge Product → InventoryItem (kits) — quantity (multiplier) |
| `InventoryItem` | Physical stock (pots/capsules), with min_stock, initial_stock |
| `Transaction` | Sales (INCOME) and expenses (EXPENSE). Has optional `product_id` FK and `quantity` |
| `Mission` | Gamification missions — title, description, xp_reward, is_completed, user_id |
| `CompetitorListing` | Scraped competitor prices. Fields: marketplace, competitor_title/price/seller, our_price_at_time, confidence_score ("alto"/"médio"/"baixo"/"nao_match"), is_confirmed_match, last_checked_at |

## Query Pattern

```python
from core.database.engine import get_session
from core.database.models import Product
from sqlmodel import select

session = next(get_session())
products = session.exec(select(Product)).all()
```

## Migrations

One-shot scripts — no migration framework:
1. Create script in `migrations/<name>.py`
2. Run manually once
3. Document in `docs/`

## Rules
- **NEVER** commit `database.db` (gitignored)
- **ALWAYS** use `get_session()` pattern
- DB path is **CWD-relative** — always run from project root
- No `__init__.py` in this package — works but fragile
