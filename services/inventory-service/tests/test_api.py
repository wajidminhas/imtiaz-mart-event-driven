"""
Test Inventory API Endpoints
Integration tests for Inventory Service REST API
"""
import pytest
from app.models.inventory_model import StockMovementType


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Inventory Service Test"


def test_health_check(client):
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_inventory(client):
    """Test POST /inventory/"""
    inventory_data = {
        "product_id": 1,
        "product_name": "Test Product",
        "quantity": 100,
        "low_stock_threshold": 10
    }
    
    response = client.post("/inventory/", json=inventory_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["product_id"] == 1
    assert data["quantity"] == 100


def test_get_inventory_by_product(client, create_sample_inventory):
    """Test GET /inventory/product/{product_id}"""
    create_sample_inventory(product_id=5, product_name="Product 5")
    
    response = client.get("/inventory/product/5")
    assert response.status_code == 200
    
    data = response.json()
    assert data["product_id"] == 5


def test_get_all_inventory(client, create_sample_inventory):
    """Test GET /inventory/"""
    create_sample_inventory(product_id=1)
    create_sample_inventory(product_id=2)
    create_sample_inventory(product_id=3)
    
    response = client.get("/inventory/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3


def test_get_low_stock_items(client, create_sample_inventory):
    """Test GET /inventory/alerts/low-stock"""
    create_sample_inventory(product_id=1, quantity=5, low_stock_threshold=10)
    create_sample_inventory(product_id=2, quantity=50, low_stock_threshold=10)
    
    response = client.get("/inventory/alerts/low-stock")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == 1


def test_adjust_stock(client, create_sample_inventory):
    """Test POST /inventory/adjust"""
    create_sample_inventory(product_id=1, quantity=100)
    
    adjustment = {
        "product_id": 1,
        "quantity_change": 50,
        "notes": "Restock"
    }
    
    response = client.post("/inventory/adjust", json=adjustment)
    assert response.status_code == 200
    
    data = response.json()
    assert data["quantity"] == 150


def test_get_product_movements(client, create_sample_inventory, create_sample_movement):
    """Test GET /inventory/movements/product/{product_id}"""
    create_sample_inventory(product_id=1)
    create_sample_movement(product_id=1, quantity=10)
    create_sample_movement(product_id=1, quantity=-5)
    
    response = client.get("/inventory/movements/product/1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
