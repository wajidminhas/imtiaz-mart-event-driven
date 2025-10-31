

import pytest
from sqlmodel import Session
from fastapi import HTTPException

from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.models.product_model import ProductCreate, ProductUpdate


@pytest.fixture
def product_service(session: Session):
    """Create ProductService with repository"""
    repository = ProductRepository(session)
    return ProductService(repository)


@pytest.mark.asyncio
async def test_create_product_success(product_service, sample_product_data):
    """Test successful product creation through service"""
    product = await product_service.create_product(
        ProductCreate(**sample_product_data)
    )
    
    assert product.id is not None
    assert product.name == sample_product_data["name"]
    assert product.price == sample_product_data["price"]


@pytest.mark.asyncio
async def test_get_product_success(product_service, create_sample_product):
    """Test getting existing product"""
    # Create a product
    created = create_sample_product(name="Find Me")
    
    # Get it through service
    product = await product_service.get_product(created.id)
    
    assert product.id == created.id
    assert product.name == "Find Me"


@pytest.mark.asyncio
async def test_get_product_not_found(product_service):
    """Test getting non-existent product raises 404"""
    with pytest.raises(HTTPException) as exc_info:
        await product_service.get_product(999)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_all_products(product_service, create_sample_product):
    """Test getting all products"""
    # Create multiple products
    create_sample_product(name="Product 1", is_active=True)
    create_sample_product(name="Product 2", is_active=True)
    create_sample_product(name="Product 3", is_active=False)
    
    # Get all active products
    products = await product_service.get_all_products(active_only=True)
    
    assert len(products) == 2
    assert all(p.is_active for p in products)


@pytest.mark.asyncio
async def test_get_all_products_including_inactive(product_service, create_sample_product):
    """Test getting all products including inactive"""
    # Create products
    create_sample_product(name="Active", is_active=True)
    create_sample_product(name="Inactive", is_active=False)
    
    # Get all (including inactive)
    products = await product_service.get_all_products(active_only=False)
    
    assert len(products) == 2


@pytest.mark.asyncio
async def test_update_product_success(product_service, create_sample_product):
    """Test updating product through service"""
    # Create product
    product = create_sample_product(name="Old Name", price=1000.0)
    
    # Update
    update_data = ProductUpdate(name="New Name", price=2000.0)
    updated = await product_service.update_product(product.id, update_data)
    
    assert updated.name == "New Name"
    assert updated.price == 2000.0


@pytest.mark.asyncio
async def test_update_nonexistent_product(product_service):
    """Test updating non-existent product raises 404"""
    update_data = ProductUpdate(name="New Name")
    
    with pytest.raises(HTTPException) as exc_info:
        await product_service.update_product(999, update_data)
    
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_success(product_service, create_sample_product):
    """Test deleting product (soft delete)"""
    # Create product
    product = create_sample_product(name="To Delete")
    
    # Delete
    result = await product_service.delete_product(product.id)
    
    assert result["product_id"] == product.id
    assert "deleted successfully" in result["message"]


@pytest.mark.asyncio
async def test_delete_nonexistent_product(product_service):
    """Test deleting non-existent product raises 404"""
    with pytest.raises(HTTPException) as exc_info:
        await product_service.delete_product(999)
    
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_check_stock_in_stock(product_service, create_sample_product):
    """Test checking stock for product with stock"""
    product = create_sample_product(
        name="In Stock Product",
        stock_quantity=10
    )
    
    stock_info = await product_service.check_stock(product.id)
    
    assert stock_info["product_id"] == product.id
    assert stock_info["stock_quantity"] == 10
    assert stock_info["in_stock"] is True


@pytest.mark.asyncio
async def test_check_stock_out_of_stock(product_service, create_sample_product):
    """Test checking stock for product without stock"""
    product = create_sample_product(
        name="Out of Stock",
        stock_quantity=0
    )
    
    stock_info = await product_service.check_stock(product.id)
    
    assert stock_info["stock_quantity"] == 0
    assert stock_info["in_stock"] is False


@pytest.mark.asyncio
async def test_check_stock_nonexistent_product(product_service):
    """Test checking stock for non-existent product"""
    with pytest.raises(HTTPException) as exc_info:
        await product_service.check_stock(999)
    
    assert exc_info.value.status_code == 404