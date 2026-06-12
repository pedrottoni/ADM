# 🗄️ Database — Models e Migrations

## Visão Geral
Camada de dados usando SQLModel + SQLAlchemy + SQLite.

## Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `models.py` | **9 tabelas**: User, Product, ProductVariation, ProductComponent, InventoryItem, Transaction, Mission, CompetitorListing, Category |
| `engine.py` | `create_db_and_tables()`, `get_session()`, `initialize_default_user()`, engine singleton |
| `migrations/` | Scripts de migração incremental (v0 → v1 → v2...) |

## Modelos Principais

| Modelo | Tabela | Uso |
|--------|--------|-----|
| `User` | Admin dono da loja. Tem XP, level, missions |
| `Product` | Anúncios Shopee. title, price, supplier_price, category_id |
| `ProductVariation` | Variações de produto (ex: 30d, 60d) |
| `ProductComponent` | Bridge Product → InventoryItem (kits) |
| `InventoryItem` | Estoque físico (potes/cápsulas), com min_stock |
| `Transaction` | Vendas (INCOME) e despesas (EXPENSE) |
| `CompetitorListing` | Preços coletados por scrapers |
| `Mission` | Missões de gamificação ligadas ao User |

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
