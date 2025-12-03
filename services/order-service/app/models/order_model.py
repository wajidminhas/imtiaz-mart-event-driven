from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============================================
# ENUMS
# ============================================

class OrderStatus(str, Enum):
    """Order status enum"""
    PENDING = "pending"           # Order created, awaiting payment
    CONFIRMED = "confirmed"       # Payment received
    PROCESSING = "processing"     # Being prepared
    SHIPPED = "shipped"           # On the way
    DELIVERED = "delivered"       # Completed
    CANCELLED = "cancelled"       # Cancelled by user/system


# ============================================
# ORDER MODELS
# ============================================

class OrderBase(SQLModel):
    """
    Base Order Schema - shared fields
    Used for inheritance by other schemas
    """
    user_id: int = Field(index=True)
    total_amount: float = Field(gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    shipping_address: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)


class Order(OrderBase, table=True):
    """
    Order Database Model - actual table in PostgreSQL
    Represents the main order
    """
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True)  # e.g., "ORD-2024-001"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship with order items
    items: List["OrderItem"] = Relationship(back_populates="order")


# ============================================
# ORDER ITEM MODELS (Products in the order)
# ============================================

class OrderItemBase(SQLModel):
    """Base Order Item Schema"""
    product_id: int = Field()  # Remove foreign_key for flexibility
    product_name: str = Field(max_length=255)  # Store name for history
    quantity: int = Field(gt=0)
    price_per_unit: float = Field(gt=0)  # Store price at time of order
    subtotal: float = Field(gt=0)  # quantity * price_per_unit


class OrderItem(OrderItemBase, table=True):
    """
    Order Item Database Model
    Each item represents a product in the order
    """
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship
    order: Optional[Order] = Relationship(back_populates="items")


# ============================================
# API SCHEMAS (Request/Response)
# ============================================

class OrderItemCreate(SQLModel):
    """Schema for creating order item in request"""
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemRead(OrderItemBase):
    """Schema for reading order item in response"""
    id: int
    order_id: int
    created_at: datetime


class OrderCreate(SQLModel):
    """
    Schema for creating a new order (API request body)
    Client sends user_id, shipping address, and list of items
    """
    user_id: int
    shipping_address: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    items: List[OrderItemCreate]  # List of products to order


class OrderUpdate(SQLModel):
    """
    Schema for updating order (API request body)
    Typically only status and notes are updated
    """
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)


class OrderRead(OrderBase):
    """Schema for reading order (API response)"""
    id: int
    order_number: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []  # Include items in response