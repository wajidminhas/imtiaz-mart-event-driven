"""
Test Inventory Repository
Tests for InventoryRepository database operations
"""
import pytest
from app.repositories.inventory_repository import InventoryRepository
from app.models.inventory_model import (
    InventoryCreate, StockMovementCreate, StockMovementType
)


def test_create_inventory(session):
    """Test creating inventory"""
    repo = InventoryRepository(session)
    
    inventory_data = InventoryCreate(
        product_id=1,
        product_name="Test Product",
        quantity=100,
        low_stock_threshold=10
    )
    
    inventory = repo.create(inventory_data)
    
    assert inventory.id is not None
    assert inventory.product_id == 1
    assert inventory.quantity == 100


def test_get_by_product_id(session, create_sample_inventory):
    """Test getting inventory by product ID"""
    repo = InventoryRepository(session)
    
    created = create_sample_inventory(product_id=5)
    
    inventory = repo.get_by_product_id(5)
    
    assert inventory is not None
    assert inventory.product_id == 5


def test_update_quantity(session, create_sample_inventory):
    """Test updating quantity"""
    repo = InventoryRepository(session)
    
    create_sample_inventory(product_id=1, quantity=100)
    
    # Add 50
    updated = repo.update_quantity(1, 50)
    assert updated.quantity == 150
    
    # Remove 30
    updated = repo.update_quantity(1, -30)
    assert updated.quantity == 120


def test_cannot_go_negative(session, create_sample_inventory):
    """Test that quantity cannot go below zero"""
    repo = InventoryRepository(session)
    
    create_sample_inventory(product_id=1, quantity=10)
    
    # Try to remove more than available
    result = repo.update_quantity(1, -20)
    
    assert result is None


def test_get_low_stock_items(session, create_sample_inventory):
    """Test getting low stock items"""
    repo = InventoryRepository(session)
    
    create_sample_inventory(product_id=1, quantity=5, low_stock_threshold=10)
    create_sample_inventory(product_id=2, quantity=50, low_stock_threshold=10)
    create_sample_inventory(product_id=3, quantity=8, low_stock_threshold=10)
    
    low_stock = repo.get_low_stock_items()
    
    assert len(low_stock) == 2
    assert all(inv.quantity < inv.low_stock_threshold for inv in low_stock)


def test_create_stock_movement(session):
    """Test creating stock movement"""
    repo = InventoryRepository(session)
    
    movement_data = StockMovementCreate(
        product_id=1,
        product_name="Test Product",  # Added this
        movement_type=StockMovementType.IN,
        quantity=50,
        notes="Restock"
    )
    
    movement = repo.create_stock_movement(movement_data)
    
    assert movement.id is not None
    assert movement.product_id == 1
    assert movement.quantity == 50


def test_get_movements_by_product(session, create_sample_movement):
    """Test getting movements by product"""
    repo = InventoryRepository(session)
    
    create_sample_movement(product_id=1, quantity=10)
    create_sample_movement(product_id=1, quantity=-5)
    create_sample_movement(product_id=2, quantity=20)
    
    movements = repo.get_movements_by_product(1)
    
    assert len(movements) == 2
    assert all(m.product_id == 1 for m in movements)