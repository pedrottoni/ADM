# 🗄️ Database — Models e Migrations

## Visão Geral
Camada de dados usando SQLModel + SQLAlchemy + SQLite.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `models.py` | **8 tabelas**: User, Mission, Transaction, Product, ProductVariation, ProductComponent, InventoryItem, CompetitorListing |
| `engine.py` | `create_db_and_tables()`, `get_session()`, `initialize_default_user()`, engine singleton |
| `migrations/` | Scripts de migração incremental (v0 → v1 → v2...) |

## Modelos Principais

| Modelo | Tabela | Uso |
|--------|--------|-----|
| `User` | Admin dono da loja. Tem XP, level, missions |
| `Product` | Anúncios Shopee. title, price, supplier_price, sku, shopee_id, category (str livre) |
| `ProductVariation` | Variações de produto (ex: 30d, 60d) — name, price, supplier_price, stock, sku, shopee_id |
| `ProductComponent` | Bridge Product → InventoryItem (kits) — quantity (multiplicador) |
| `InventoryItem` | Estoque físico (potes/cápsulas), com min_stock, initial_stock |
| `Transaction` | Vendas (INCOME) e despesas (EXPENSE). Tem `product_id` (FK opcional, populado por `SalesService.process_income_batch`) e `quantity` |
| `Mission` | Missões de gamificação — title, description, xp_reward, is_completed, user_id |
| `CompetitorListing` | Preços coletados por scrapers. Campos: marketplace, competitor_title/price/seller, our_price_at_time, price_before_discount, shipping_cost, product_url, marketplace_id, rating, sold_count, seller_location, **is_confirmed_match** (bool), **confidence_score** ("alto"/"médio"/"baixo"/"nao_match"), last_checked_at |

## Como Usar

### Para consultar dados:
```python
from core.database.engine import get_session
from core.database.models import Product
from sqlmodel import select

session = next(get_session())
products = session.exec(select(Product)).all()
```

### Para adicionar migration:
1. Criar script em `migrations/<nome>.py`
2. Rodar uma vez manualmente
3. Documentar em `docs/`

## ⚠️ Regras
- **NUNCA** commitar `database.db` (está no `.gitignore`)
- **SEMPRE** usar `get_session()` como context manager
- Migrations são **one-shot** — não tem framework de migração automática
