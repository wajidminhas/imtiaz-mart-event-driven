

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class ProductBase(SQLModel):
    """
    Base Product Schema - shared fields
    Used for inheritance by other schemas
    """
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: float = Field(gt=0)  # Greater than 0
    stock_quantity: int = Field(default=0, ge=0)  # Greater or equal to 0
    is_active: bool = Field(default=True)


class Product(ProductBase, table=True):
    """
    Product Database Model - actual table in PostgreSQL
    Inherits from ProductBase and adds database-specific fields
    """
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductCreate(ProductBase):
    """Schema for creating a new product (API request body)"""
    pass


class ProductUpdate(SQLModel):
    """
    Schema for updating product (API request body)
    All fields optional - only update what's provided
    """
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[float] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductRead(ProductBase):
    """Schema for reading product (API response)"""
    id: int
    created_at: datetime
    updated_at: datetime