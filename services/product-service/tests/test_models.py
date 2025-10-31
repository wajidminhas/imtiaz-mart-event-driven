

import pytest
from pydantic import ValidationError
from app.models.product_model import Product, ProductCreate, ProductUpdate


def test_product_create_valid():
    """Test valid product creation"""
    product_data = {
        "name": "Laptop",
        "description": "Gaming laptop",
        "price": 150000.0,
        "stock_quantity": 5,
        "is_active": True
    }
    product = ProductCreate(**product_data)
    
    assert product.name == "Laptop"
    assert product.price == 150000.0
    assert product.stock_quantity == 5


def test_product_price_must_be_positive():
    """Test that price must be greater than 0"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name="Laptop",
            price=-100.0,  # Invalid: negative price
            stock_quantity=5
        )
    
    assert "greater than 0" in str(exc_info.value)


def test_product_stock_cannot_be_negative():
    """Test that stock_quantity cannot be negative"""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name="Laptop",
            price=1000.0,
            stock_quantity=-5  # Invalid: negative stock
        )
    
    assert "greater than or equal to 0" in str(exc_info.value)


def test_product_update_partial():
    """Test partial update with ProductUpdate"""
    update_data = ProductUpdate(price=200000.0)
    
    assert update_data.price == 200000.0
    assert update_data.name is None  # Other fields not provided
    assert update_data.stock_quantity is None


def test_product_default_values():
    """Test default values for optional fields"""
    product = ProductCreate(
        name="Minimal Product",
        price=1000.0
    )
    
    assert product.stock_quantity == 0  # Default
    assert product.is_active is True  # Default
    assert product.description is None  # Optional