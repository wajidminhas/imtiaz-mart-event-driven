"""
Test Order API Endpoints
Integration tests for Order Service REST API
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.models.order_model import OrderStatus


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Order Service"
    assert data["status"] == "healthy"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Order Service"
    assert data["status"] == "healthy"


def test_get_order(client, create_sample_order, create_sample_order_item):
    """Test GET /orders/{id}"""
    # Create order with items
    order = create_sample_order(order_number="ORD-API-001")
    create_sample_order_item(order.id, product_id=1, quantity=2)
    
    # Get order
    response = client.get(f"/orders/{order.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == order.id
    assert data["order_number"] == "ORD-API-001"
    assert len(data["items"]) == 1


def test_get_order_not_found(client):
    """Test GET /orders/{id} with non-existent order"""
    response = client.get("/orders/999")
    assert response.status_code == 404


def test_get_all_orders(client, create_sample_order):
    """Test GET /orders/"""
    # Create multiple orders
    create_sample_order(order_number="ORD-1")
    create_sample_order(order_number="ORD-2")
    create_sample_order(order_number="ORD-3")
    
    # Get all orders
    response = client.get("/orders/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3


def test_get_orders_with_status_filter(client, create_sample_order):
    """Test GET /orders/ with status filter"""
    # Create orders with different statuses AND unique order numbers
    create_sample_order(status=OrderStatus.PENDING, order_number="ORD-F1")
    create_sample_order(status=OrderStatus.CONFIRMED, order_number="ORD-F2")
    create_sample_order(status=OrderStatus.PENDING, order_number="ORD-F3")
    
    # Get only pending orders
    response = client.get("/orders/?status=pending")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(order["status"] == "pending" for order in data)


def test_get_user_orders(client, create_sample_order):
    """Test GET /orders/user/{user_id}"""
    # Create orders for different users
    create_sample_order(user_id=1, order_number="ORD-U1-1")
    create_sample_order(user_id=1, order_number="ORD-U1-2")
    create_sample_order(user_id=2, order_number="ORD-U2-1")
    
    # Get user 1 orders
    response = client.get("/orders/user/1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(order["user_id"] == 1 for order in data)


def test_update_order_status(client, create_sample_order):
    """Test PATCH /orders/{id}/status"""
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING)
    
    # Mock event publisher
    with patch('app.services.order_service.publish_order_updated'):
        # Update status
        response = client.patch(
            f"/orders/{order.id}/status",
            params={"new_status": "confirmed"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"


def test_cancel_order(client, create_sample_order):
    """Test POST /orders/{id}/cancel"""
    # Create order
    order = create_sample_order(status=OrderStatus.PENDING)
    
    # Mock event publisher
    with patch('app.services.order_service.publish_order_cancelled'):
        # Cancel order
        response = client.post(f"/orders/{order.id}/cancel")
    
    assert response.status_code == 200
    data = response.json()
    assert "cancelled successfully" in data["message"]


def test_cannot_cancel_shipped_order(client, create_sample_order):
    """Test that shipped orders cannot be cancelled"""
    # Create shipped order
    order = create_sample_order(status=OrderStatus.SHIPPED)
    
    # Try to cancel
    response = client.post(f"/orders/{order.id}/cancel")
    assert response.status_code == 400