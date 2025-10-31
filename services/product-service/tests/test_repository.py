import pytest
from sqlmodel import Session
from app.repositories.product_repository import ProductRepository
from app.models.product_model import ProductCreate, ProductUpdate


def test_create_product(session: Session):
    """Test creating a product"""
    repo = ProductRepository(session)
    
    product_data = ProductCreate(
        name="Test Laptop",
        price=150000.0,
        stock_quantity=10
    )
    
    product = repo.create(product_data)
    
    assert product.id is not None
    assert product.name == "Test Laptop"
    assert product.price == 150000.0
    assert product.created_at is not None


def test_get_product_by_id(session: Session, create_sample_product):
    """Test retrieving product by ID"""
    repo = ProductRepository(session)
    
    # Create a product
    created_product = create_sample_product(name="Find Me")
    
    # Retrieve it
    found_product = repo.get_by_id(created_product.id)
    
    assert found_product is not None
    assert found_product.id == created_product.id
    assert found_product.name == "Find Me"


def test_get_product_by_id_not_found(session: Session):
    """Test retrieving non-existent product"""
    repo = ProductRepository(session)
    
    product = repo.get_by_id(999)
    
    assert product is None


def test_get_all_products(session: Session, create_sample_product):
    """Test getting all products with pagination"""
    repo = ProductRepository(session)
    
    # Create multiple products
    create_sample_product(name="Product 1")
    create_sample_product(name="Product 2")
    create_sample_product(name="Product 3")
    
    # Get all
    products = repo.get_all(skip=0, limit=10)
    
    assert len(products) == 3


def test_get_all_products_pagination(session: Session, create_sample_product):
    """Test pagination"""
    repo = ProductRepository(session)
    
    # Create 5 products
    for i in range(5):
        create_sample_product(name=f"Product {i}")
    
    # Get first 2
    page1 = repo.get_all(skip=0, limit=2)
    assert len(page1) == 2
    
    # Get next 2
    page2 = repo.get_all(skip=2, limit=2)
    assert len(page2) == 2
    
    # Ensure different products
    assert page1[0].id != page2[0].id


def test_get_active_products_only(session: Session, create_sample_product):
    """Test getting only active products"""
    repo = ProductRepository(session)
    
    # Create active and inactive products
    create_sample_product(name="Active 1", is_active=True)
    create_sample_product(name="Active 2", is_active=True)
    create_sample_product(name="Inactive", is_active=False)
    
    # Get only active
    active_products = repo.get_active_products()
    
    assert len(active_products) == 2
    assert all(p.is_active for p in active_products)


def test_update_product(session: Session, create_sample_product):
    """Test updating a product"""
    repo = ProductRepository(session)
    
    # Create product
    product = create_sample_product(name="Old Name", price=1000.0)
    
    # Update it
    update_data = ProductUpdate(name="New Name", price=2000.0)
    updated_product = repo.update(product.id, update_data)
    
    assert updated_product is not None
    assert updated_product.name == "New Name"
    assert updated_product.price == 2000.0
    assert updated_product.stock_quantity == product.stock_quantity  # Unchanged


def test_update_product_partial(session: Session, create_sample_product):
    """Test partial update (only some fields)"""
    repo = ProductRepository(session)
    
    # Create product
    product = create_sample_product(name="Original", price=1000.0)
    
    # Update only price
    update_data = ProductUpdate(price=1500.0)
    updated_product = repo.update(product.id, update_data)
    
    assert updated_product.price == 1500.0
    assert updated_product.name == "Original"  # Unchanged


def test_soft_delete_product(session: Session, create_sample_product):
    """Test soft delete (mark as inactive)"""
    repo = ProductRepository(session)
    
    # Create product
    product = create_sample_product(name="To Delete")
    
    # Soft delete
    success = repo.soft_delete(product.id)
    
    assert success is True
    
    # Verify it's marked inactive
    deleted_product = repo.get_by_id(product.id)
    assert deleted_product is not None  # Still exists
    assert deleted_product.is_active is False  # But inactive


def test_soft_delete_nonexistent_product(session: Session):
    """Test soft deleting non-existent product"""
    repo = ProductRepository(session)
    
    success = repo.soft_delete(999)
    
    assert success is False