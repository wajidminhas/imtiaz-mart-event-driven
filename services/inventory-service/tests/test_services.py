"""
Test Inventory Service
Tests for InventoryService business logic
"""
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.inventory_service import InventoryService
from app.repositories.inventory_repository import InventoryRepository
from app.models.inventory_model import InventoryCreate, StockAdjustment


@pytest.fixture
def inventory_service(session):
    """Create InventoryService instance"""
    repo = InventoryRepository(session)
    return InventoryService(repo)


@pytest.mark.asyncio
async def test_create_inventory(session, inventory_service):
    """Test creating inventory"""
    inventory_data = InventoryCreate(
        product_id=1,
        product_name="Test Product",
        quantity=100,
        low_stock_threshold=10
    )
    
    inventory = await inventory_service.create_inventory(inventory_data)
    
    assert inventory.product_id == 1
    assert inventory.quantity == 100


@pytest.mark.asyncio
async def test_cannot_create_duplicate(session, create_sample_inventory, inventory_service):
    """Test cannot create duplicate inventory"""
    create_sample_inventory(product_id=1)
    
    inventory_data = InventoryCreate(
        product_id=1,
        product_name="Duplicate",
        quantity=50
    )
    
    with pytest.raises(HTTPException) as exc:
        await inventory_service.create_inventory(inventory_data)
    
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_inventory_by_product(session, create_sample_inventory, inventory_service):
    """Test getting inventory by product"""
    create_sample_inventory(product_id=5, product_name="Product 5")
    
    inventory = await inventory_service.get_inventory_by_product(5)
    
    assert inventory.product_id == 5


@pytest.mark.asyncio
async def test_adjust_stock(session, create_sample_inventory, inventory_service):
    """Test adjusting stock"""
    create_sample_inventory(product_id=1, quantity=100)
    
    adjustment = StockAdjustment(
        product_id=1,
        quantity_change=50,
        notes="Restock"
    )
    
    with patch('app.services.inventory_service.publish_inventory_restocked'):
        inventory = await inventory_service.adjust_stock(adjustment)
    
    assert inventory.quantity == 150


@pytest.mark.asyncio
async def test_get_low_stock_items(session, create_sample_inventory, inventory_service):
    """Test getting low stock items"""
    create_sample_inventory(product_id=1, quantity=5, low_stock_threshold=10)
    create_sample_inventory(product_id=2, quantity=50, low_stock_threshold=10)
    
    low_stock = await inventory_service.get_low_stock_items()
    
    assert len(low_stock) == 1
    assert low_stock[0].product_id == 1
