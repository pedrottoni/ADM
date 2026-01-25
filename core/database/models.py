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
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str
    keywords: Optional[str] = None
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
