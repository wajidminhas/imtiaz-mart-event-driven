

"""
Test Order Service
Tests for OrderService business logic
"""
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.models.order_model import OrderStatus


@pytest.fixture
def order_service(session):
    """Create OrderService instance with repository"""
    repo = OrderRepository(session)
    return OrderService(repo)


@pytest.mark.asyncio
async def test_generate_order_number(order_service):
    """Test order number generation"""
    order_number = order_service.generate_order_number()
    
    assert order_number.startswith("ORD-")
    assert len(order_number) > 10


@pytest.mark.asyncio
async def test_get_order(session, create_sample_order, order_service):
    """Test getting an order"""
    # Create order
    created_order = create_sample_order(order_number="ORD-GET-001")
    
    # Get order
    order = await order_service.get_order(created_order.id)
    
    assert order.id == created_order.id
    assert order.order_number == "ORD-GET-001"


@pytest.mark.asyncio
async def test_get_order_not_found(order_service):
    """Test getting non-existent order raises exception"""
    with pytest.raises(HTTPException) as exc_info:
        await order_service.get_order(999)
    
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_user_orders(session, create_sample_order, order_service):
    """Test getting orders for a user"""
    # Create orders
    create_sample_order(user_id=1, order_number="ORD-U1-001")
    create_sample_order(user_id=1, order_number="ORD-U1-002")
    create_sample_order(user_id=2, order_number="ORD-U2-001")
    
    # Get user 1 orders
    orders = await order_service.get_user_orders(user_id=1)
    
    assert len(orders) == 2
    assert all(o.user_id == 1 for o in orders)


@pytest.mark.asyncio
async def test_update_order_status(session, create_sample_order, order_service):
    """Test updating order status"""
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING, order_number="ORD-UP-001")
    
    # Mock event publisher
    with patch('app.services.order_service.publish_order_updated'):
        updated_order = await order_service.update_order_status(
            order.id, 
            OrderStatus.CONFIRMED
        )
    
    assert updated_order.status == OrderStatus.CONFIRMED


@pytest.mark.asyncio
async def test_cannot_update_cancelled_order(session, create_sample_order, order_service):
    """Test that cancelled orders cannot be updated"""
    # Create cancelled order
    order = create_sample_order(status=OrderStatus.CANCELLED, order_number="ORD-CAN-001")
    
    # Try to update
    with pytest.raises(HTTPException) as exc_info:
        await order_service.update_order_status(order.id, OrderStatus.CONFIRMED)
    
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_cancel_order(session, create_sample_order, order_service):
    """Test cancelling an order"""
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING, order_number="ORD-CAN-002")
    
    # Mock event publisher
    with patch('app.services.order_service.publish_order_cancelled'):
        result = await order_service.cancel_order(order.id)
    
    assert "cancelled successfully" in result["message"]
    assert result["order_id"] == order.id


@pytest.mark.asyncio
async def test_cannot_cancel_shipped_order(session, create_sample_order, order_service):
    """Test that shipped orders cannot be cancelled"""
    # Create shipped order
    order = create_sample_order(status=OrderStatus.SHIPPED, order_number="ORD-SHIP-001")
    
    # Try to cancel
    with pytest.raises(HTTPException) as exc_info:
        await order_service.cancel_order(order.id)
    
    assert exc_info.value.status_code == 400
    assert "Cannot cancel" in str(exc_info.value.detail)