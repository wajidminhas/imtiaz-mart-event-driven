from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# ============================================
# ENUMS
# ============================================

class StockMovementType(str, Enum):
    """Types of stock movements"""
    IN = "in"              # Stock added (restock)
    OUT = "out"            # Stock removed (order placed)
    RETURN = "return"      # Stock returned (order cancelled)
    ADJUSTMENT = "adjustment"  # Manual adjustment


# ============================================
# INVENTORY MODELS
# ============================================

class InventoryBase(SQLModel):
    """
    Base Inventory Schema
    Tracks stock levels for each product
    """
    product_id: int = Field(unique=True, index=True)
    product_name: str = Field(max_length=255)
    quantity: int = Field(default=0, ge=0)  # Available quantity
    reserved_quantity: int = Field(default=0, ge=0)  # Reserved for pending orders
    low_stock_threshold: int = Field(default=10)  # Alert when below this


class Inventory(InventoryBase, table=True):
    """
    Inventory Database Model
    Main table tracking product stock
    """
    __tablename__ = "inventory"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============================================
# STOCK MOVEMENT MODELS (Audit Trail)
# ============================================

class StockMovementBase(SQLModel):
    """
    Base Stock Movement Schema
    Records every stock change for audit
    """
    product_id: int = Field(index=True)
    product_name: str = Field(max_length=255)
    movement_type: StockMovementType
    quantity: int  # Can be positive or negative
    order_id: Optional[int] = None  # If related to an order
    notes: Optional[str] = Field(default=None, max_length=500)


class StockMovement(StockMovementBase, table=True):
    """
    Stock Movement Database Model
    Audit trail of all stock changes
    """
    __tablename__ = "stock_movements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)


# ============================================
# API SCHEMAS
# ============================================

class InventoryCreate(SQLModel):
    """Schema for creating inventory record"""
    product_id: int
    product_name: str
    quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10)


class InventoryUpdate(SQLModel):
    """Schema for updating inventory"""
    quantity: Optional[int] = Field(default=None, ge=0)
    reserved_quantity: Optional[int] = Field(default=None, ge=0)
    low_stock_threshold: Optional[int] = None


class InventoryRead(InventoryBase):
    """Schema for reading inventory (API response)"""
    id: int
    available_quantity: int  # Computed: quantity - reserved_quantity
    is_low_stock: bool  # Computed: quantity < low_stock_threshold
    is_out_of_stock: bool  # Computed: quantity == 0
    created_at: datetime
    updated_at: datetime


class StockMovementCreate(SQLModel):
    """Schema for creating stock movement"""
    product_id: int
    movement_type: StockMovementType
    quantity: int
    order_id: Optional[int] = None
    notes: Optional[str] = None


class StockMovementRead(StockMovementBase):
    """Schema for reading stock movement"""
    id: int
    created_at: datetime


class StockAdjustment(SQLModel):
    """Schema for manual stock adjustment"""
    product_id: int
    quantity_change: int  # Positive to add, negative to remove
    notes: Optional[str] = None