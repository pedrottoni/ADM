from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    level: int = Field(default=1)
    xp: int = Field(default=0)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    missions: List["Mission"] = Relationship(back_populates="user")

class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    xp_reward: int
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="missions")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    type: str  # "INCOME" or "EXPENSE"
    category: str # "Sale", "Ads", "COGS", "Subscription", "Other"
    description: str
    amount: float
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = Field(default=1)  # Quantidade de unidades vendidas nesta transação
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class ProductVariation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # e.g. "Sabor Morango", "Kit 3 - 200g"
    price: float = Field(default=0.0)
    supplier_price: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None
    shopee_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    product_id: int = Field(foreign_key="product.id")
    product: Optional["Product"] = Relationship(back_populates="variations")

class InventoryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # Ex: "Pote Melatonina 60 caps"
    supplier_price: float = Field(default=0.0)
    stock: int = Field(default=0)
    initial_stock: int = Field(default=100)
    min_stock: int = Field(default=10) # Limite para alerta de reposição
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class ProductComponent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1) # Ex: 1x, 2x, 3x neste anúncio
    
    product_id: int = Field(foreign_key="product.id")
    inventory_item_id: int = Field(foreign_key="inventoryitem.id")
    
    product: Optional["Product"] = Relationship(back_populates="components")
    inventory_item: Optional[InventoryItem] = Relationship()

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    keywords: Optional[str] = None
    price: float = Field(default=0.0)
    supplier_price: float = Field(default=0.0)
    stock: int = Field(default=0)
    initial_stock: int = Field(default=100)
    sku: Optional[str] = None
    shopee_id: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    variations: List[ProductVariation] = Relationship(back_populates="product", cascade_delete=True)
    components: List[ProductComponent] = Relationship(back_populates="product", cascade_delete=True)
    competitor_listings: List["CompetitorListing"] = Relationship(back_populates="product", cascade_delete=True)


class CompetitorListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    marketplace: str = Field(index=True)
    competitor_title: str
    competitor_price: float
    competitor_seller: Optional[str] = None
    our_price_at_time: float = Field(default=0.0)
    price_before_discount: Optional[float] = None
    shipping_cost: Optional[float] = None
    product_url: str
    marketplace_id: Optional[str] = None
    rating: Optional[float] = None
    sold_count: Optional[int] = None
    seller_location: Optional[str] = None
    is_confirmed_match: bool = Field(default=False)
    confidence_score: Optional[str] = None
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    product: Optional[Product] = Relationship(back_populates="competitor_listings")


class Task(SQLModel, table=True):
    """Practical operations task — replaces the old gamification mission system."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    category: str  # "vendas", "estoque", "concorrencia", "marketing", "anuncio", "relatorio"
    priority: int = Field(default=3)  # 1=urgente .. 5=baixa
    is_completed: bool = Field(default=False)
    auto_generated: bool = Field(default=True)
    target_tab: Optional[str] = None  # ex: "financeiro", "concorrencia" — atalho na UI
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
