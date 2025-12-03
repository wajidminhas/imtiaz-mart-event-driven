

"""
Test Order Repository
Tests for OrderRepository database operations
"""
import pytest
from app.repositories.order_repository import OrderRepository
from app.models.order_model import Order, OrderStatus, OrderCreate, OrderItemCreate


def test_create_order(session):
    """Test creating an order"""
    repo = OrderRepository(session)
    
    order = repo.create(
        order_data=OrderCreate(
            user_id=1,
            shipping_address="Test Address",
            items=[]
        ),
        order_number="ORD-TEST-001",
        total_amount=5000.0
    )
    
    assert order.id is not None
    assert order.user_id == 1
    assert order.order_number == "ORD-TEST-001"
    assert order.total_amount == 5000.0
    assert order.status == OrderStatus.PENDING


def test_add_order_items(session, create_sample_order):
    """Test adding items to an order"""
    repo = OrderRepository(session)
    
    # Create order first
    order = create_sample_order()
    
    # Add items
    items_data = [
        {
            'product_id': 1,
            'product_name': 'Product 1',
            'quantity': 2,
            'price_per_unit': 1000.0,
            'subtotal': 2000.0
        },
        {
            'product_id': 2,
            'product_name': 'Product 2',
            'quantity': 1,
            'price_per_unit': 3000.0,
            'subtotal': 3000.0
        }
    ]
    
    order_items = repo.add_order_items(order.id, items_data)
    
    assert len(order_items) == 2
    assert order_items[0].product_id == 1
    assert order_items[1].product_id == 2


def test_get_order_by_id(session, create_sample_order):
    """Test getting order by ID"""
    repo = OrderRepository(session)
    
    # Create order
    created_order = create_sample_order(order_number="ORD-GET-001")
    
    # Get order
    order = repo.get_by_id(created_order.id)
    
    assert order is not None
    assert order.id == created_order.id
    assert order.order_number == "ORD-GET-001"


def test_get_order_by_number(session, create_sample_order):
    """Test getting order by order number"""
    repo = OrderRepository(session)
    
    # Create order
    created_order = create_sample_order(order_number="ORD-NUM-001")
    
    # Get by order number
    order = repo.get_by_order_number("ORD-NUM-001")
    
    assert order is not None
    assert order.order_number == "ORD-NUM-001"


def test_get_by_user_id(session, create_sample_order):
    """Test getting orders by user ID"""
    repo = OrderRepository(session)
    
    # Create multiple orders for user
    create_sample_order(user_id=1, order_number="ORD-U1-001")
    create_sample_order(user_id=1, order_number="ORD-U1-002")
    create_sample_order(user_id=2, order_number="ORD-U2-001")
    
    # Get user 1 orders
    user1_orders = repo.get_by_user_id(user_id=1)
    
    assert len(user1_orders) == 2
    assert all(o.user_id == 1 for o in user1_orders)


def test_get_by_status(session, create_sample_order):
    """Test getting orders by status"""
    repo = OrderRepository(session)
    
    # Create orders with different statuses
    create_sample_order(status=OrderStatus.PENDING, order_number="ORD-S1")
    create_sample_order(status=OrderStatus.CONFIRMED, order_number="ORD-S2")
    create_sample_order(status=OrderStatus.PENDING, order_number="ORD-S3")
    
    # Get pending orders
    pending_orders = repo.get_by_status(OrderStatus.PENDING)
    
    assert len(pending_orders) == 2
    assert all(o.status == OrderStatus.PENDING for o in pending_orders)


def test_update_order_status(session, create_sample_order):
    """Test updating order status"""
    repo = OrderRepository(session)
    
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING, order_number="ORD-UP-001")
    
    # Update status
    updated_order = repo.update_status(order.id, OrderStatus.CONFIRMED)
    
    assert updated_order is not None
    assert updated_order.status == OrderStatus.CONFIRMED


def test_cancel_order(session, create_sample_order):
    """Test cancelling an order"""
    repo = OrderRepository(session)
    
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING, order_number="ORD-CAN-001")
    
    # Cancel order
    success = repo.cancel_order(order.id)
    
    assert success is True
    
    # Verify status changed
    cancelled_order = repo.get_by_id(order.id)
    assert cancelled_order.status == OrderStatus.CANCELLED


def test_cannot_cancel_shipped_order(session, create_sample_order):
    """Test that shipped orders cannot be cancelled"""
    repo = OrderRepository(session)
    
    # Create shipped order
    order = create_sample_order(status=OrderStatus.SHIPPED, order_number="ORD-SHIP-001")
    
    # Try to cancel
    success = repo.cancel_order(order.id)
    
    assert success is False