

"""
Test Order Models
Tests for Order and OrderItem SQLModel models
"""
import pytest
from app.models.order_model import Order, OrderItem, OrderStatus, OrderCreate, OrderItemCreate


def test_order_model_creation():
    """Test creating an Order model"""
    order = Order(
        user_id=1,
        order_number="ORD-2024-001",
        total_amount=5000.0,
        status=OrderStatus.PENDING,
        shipping_address="123 Test Street"
    )
    
    assert order.user_id == 1
    assert order.order_number == "ORD-2024-001"
    assert order.total_amount == 5000.0
    assert order.status == OrderStatus.PENDING
    assert order.shipping_address == "123 Test Street"


def test_order_item_model_creation():
    """Test creating an OrderItem model"""
    order_item = OrderItem(
        order_id=1,
        product_id=10,
        product_name="Test Product",
        quantity=2,
        price_per_unit=1000.0,
        subtotal=2000.0
    )
    
    assert order_item.order_id == 1
    assert order_item.product_id == 10
    assert order_item.product_name == "Test Product"
    assert order_item.quantity == 2
    assert order_item.price_per_unit == 1000.0
    assert order_item.subtotal == 2000.0


def test_order_status_enum():
    """Test OrderStatus enum values"""
    assert OrderStatus.PENDING == "pending"
    assert OrderStatus.CONFIRMED == "confirmed"
    assert OrderStatus.PROCESSING == "processing"
    assert OrderStatus.SHIPPED == "shipped"
    assert OrderStatus.DELIVERED == "delivered"
    assert OrderStatus.CANCELLED == "cancelled"


def test_order_create_schema():
    """Test OrderCreate schema validation"""
    order_data = OrderCreate(
        user_id=1,
        shipping_address="Test Address",
        items=[
            OrderItemCreate(product_id=1, quantity=2),
            OrderItemCreate(product_id=2, quantity=1)
        ]
    )
    
    assert order_data.user_id == 1
    assert order_data.shipping_address == "Test Address"
    assert len(order_data.items) == 2
    assert order_data.items[0].product_id == 1
    assert order_data.items[0].quantity == 2