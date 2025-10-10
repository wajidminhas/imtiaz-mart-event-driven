"""
Category Model - Database representation
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import uuid

if TYPE_CHECKING:
    from app.models.product import Product


class Category(SQLModel, table=True):
    """
    Category table for product organization
    """
    __tablename__ = "categories"
    
    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    
    # Basic Information
    name: str = Field(max_length=100, nullable=False, index=True)
    slug: str = Field(max_length=100, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None, nullable=True)
    # Status
    is_active: bool = Field(default=True, nullable=False)
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    # Relationships
    products: list["Product"] = Relationship(back_populates="category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Electronics",
                "slug": "electronics",
                "description": "Electronic devices and accessories",
                "is_active": True
            }
        }