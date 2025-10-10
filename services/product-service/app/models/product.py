"""
Product Model - Database representation
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
import uuid

if TYPE_CHECKING:
    from app.models.category import Category


class Product(SQLModel, table=True):
    """
    Product table for inventory management
    """
    __tablename__ = "products"
    
    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    # Basic Information
    name: str = Field(max_length=255, nullable=False, index=True)
    description: Optional[str] = Field( default=None, nullable=True)
    sku: str = Field(max_length=50, nullable=False, unique=True, index=True)
    # Pricing
    price: Decimal = Field(default=Decimal("0.00"),max_digits=10, decimal_places=2, nullable=False) # Non-negative price
    stock_quantity: int = Field(default=0, nullable=False, ge=0)  # Greater than or equal to 0
    # Category Relationship
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id", nullable=True)
    # Status
    is_active: bool = Field(default=True, nullable=False)
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    # Relationships
    category: Optional["Category"] = Relationship(back_populates="products")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15 Pro",
                "description": "Latest Apple smartphone with A17 Pro chip",
                "sku": "IPHONE-15-PRO-256GB",
                "price": 1199.99,
                "stock_quantity": 50,
                "is_active": True
            }
        }