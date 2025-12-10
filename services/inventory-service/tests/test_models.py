"""
Test Inventory Models
Tests for Inventory and StockMovement SQLModel models
"""
import pytest
from app.models.inventory_model import (
    Inventory, InventoryCreate, StockMovement, 
    StockMovementType, StockAdjustment
)


def test_inventory_model_creation():
    """Test creating an Inventory model"""
    inventory = Inventory(
        product_id=1,
        product_name="Test Product",
        quantity=100,
        reserved_quantity=10,
        low_stock_threshold=20
    )
    
    assert inventory.product_id == 1
    assert inventory.product_name == "Test Product"
    assert inventory.quantity == 100
    assert inventory.reserved_quantity == 10
    assert inventory.low_stock_threshold == 20


def test_stock_movement_model_creation():
    """Test creating a StockMovement model"""
    movement = StockMovement(
        product_id=1,
        product_name="Test Product",
        movement_type=StockMovementType.IN,
        quantity=50,
        order_id=None,
        notes="Restock"
    )
    
    assert movement.product_id == 1
    assert movement.product_name == "Test Product"
    assert movement.movement_type == StockMovementType.IN
    assert movement.quantity == 50
    assert movement.notes == "Restock"


def test_stock_movement_type_enum():
    """Test StockMovementType enum values"""
    assert StockMovementType.IN == "in"
    assert StockMovementType.OUT == "out"
    assert StockMovementType.RETURN == "return"
    assert StockMovementType.ADJUSTMENT == "adjustment"


def test_inventory_create_schema():
    """Test InventoryCreate schema validation"""
    inventory_data = InventoryCreate(
        product_id=1,
        product_name="Test Product",
        quantity=100,
        low_stock_threshold=15
    )
    
    assert inventory_data.product_id == 1
    assert inventory_data.product_name == "Test Product"
    assert inventory_data.quantity == 100
    assert inventory_data.low_stock_threshold == 15


def test_stock_adjustment_schema():
    """Test StockAdjustment schema"""
    adjustment = StockAdjustment(
        product_id=1,
        quantity_change=50,
        notes="Manual restock"
    )
    
    assert adjustment.product_id == 1
    assert adjustment.quantity_change == 50
    assert adjustment.notes == "Manual restock"


def test_inventory_default_values():
    """Test inventory default values"""
    inventory = Inventory(
        product_id=1,
        product_name="Test Product"
    )
    
    assert inventory.quantity == 0
    assert inventory.reserved_quantity == 0
    assert inventory.low_stock_threshold == 10
