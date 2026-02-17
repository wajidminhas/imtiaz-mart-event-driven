import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from unittest.mock import patch


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine with proper SQLite configuration"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},  # Allow multi-threading for tests
        echo=False
    )
    # Create all tables
    SQLModel.metadata.create_all(engine)
    yield engine
    # Clean up
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(test_session):
    """Create test client with mocked dependencies"""
    # Mock event publishers
    with patch('app.services.payment_service.publish_payment_initiated', return_value=True), \
         patch('app.services.payment_service.publish_payment_completed', return_value=True), \
         patch('app.services.payment_service.publish_payment_failed', return_value=True), \
         patch('app.services.payment_service.publish_payment_refunded', return_value=True):
        
        # Import app after mocking
        from app.main import app
        from app.database import get_payment_session
        
        # Override dependency
        def get_test_session():
            try:
                yield test_session
            finally:
                pass  # Don't close - managed by fixture
        
        app.dependency_overrides[get_payment_session] = get_test_session
        
        # Create test client
        client = TestClient(app, raise_server_exceptions=False)
        
        yield client
        
        # Clean up
        app.dependency_overrides.clear()


class TestPaymentAPI:
    """Integration tests for Payment API"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_payment(self, client):
        """Test creating a payment via API"""
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 100.50,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        response = client.post("/payments/", json=payment_data)
        
        assert response.status_code == 201, f"Error: {response.json()}"
        data = response.json()
        assert data["order_id"] == 1
        assert data["amount"] == 100.50
        assert data["status"] == "pending"
        assert "id" in data
    
    def test_get_payment_by_id(self, client):
        """Test getting payment by ID"""
        # Create payment first
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 200.00,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        payment_id = create_response.json()["id"]
        
        # Get payment
        response = client.get(f"/payments/{payment_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id
        assert data["amount"] == 200.00
    
    def test_get_payment_not_found(self, client):
        """Test getting non-existent payment returns 404"""
        response = client.get("/payments/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_user_payments(self, client):
        """Test getting all payments for a user"""
        # Create multiple payments
        for i in range(3):
            payment_data = {
                "order_id": i + 1,
                "user_id": 1,
                "amount": 100.00 * (i + 1),
                "currency": "PKR",
                "payment_method": "payfast",
                "payment_provider": "payfast"
            }
            response = client.post("/payments/", json=payment_data)
            assert response.status_code == 201
        
        # Get user payments
        response = client.get("/payments/user/1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(p["user_id"] == 1 for p in data)
    
    def test_get_payment_by_order(self, client):
        """Test getting payment by order ID"""
        payment_data = {
            "order_id": 123,
            "user_id": 1,
            "amount": 500.00,
            "currency": "PKR",
            "payment_method": "stripe",
            "payment_provider": "stripe"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        
        # Get by order ID
        response = client.get("/payments/order/123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == 123
    
    def test_complete_payment(self, client):
        """Test completing a payment"""
        # Create payment
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 300.00,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        payment_id = create_response.json()["id"]
        
        # Complete payment
        response = client.post(
            f"/payments/{payment_id}/complete",
            params={"provider_transaction_id": "txn_123456"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["provider_transaction_id"] == "txn_123456"
        assert data["completed_at"] is not None
    
    def test_fail_payment(self, client):
        """Test marking payment as failed"""
        # Create payment
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 150.00,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        payment_id = create_response.json()["id"]
        
        # Fail payment
        response = client.post(
            f"/payments/{payment_id}/fail",
            params={
                "failure_reason": "Insufficient funds",
                "failure_code": "INSUFFICIENT_FUNDS"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["failure_reason"] == "Insufficient funds"
        assert data["failure_code"] == "INSUFFICIENT_FUNDS"
    
    def test_refund_payment(self, client):
        """Test refunding a completed payment"""
        # Create and complete payment
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 500.00,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        payment_id = create_response.json()["id"]
        
        # Complete it first
        complete_response = client.post(
            f"/payments/{payment_id}/complete",
            params={"provider_transaction_id": "txn_123"}
        )
        assert complete_response.status_code == 200
        
        # Now refund
        response = client.post(
            f"/payments/{payment_id}/refund",
            params={"refund_amount": 200.00, "refund_reason": "Customer request"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "partially_refunded"
        assert data["refunded_amount"] == 200.00
    
    def test_cannot_complete_already_completed_payment(self, client):
        """Test that completing an already completed payment fails"""
        # Create and complete payment
        payment_data = {
            "order_id": 1,
            "user_id": 1,
            "amount": 100.00,
            "currency": "PKR",
            "payment_method": "payfast",
            "payment_provider": "payfast"
        }
        
        create_response = client.post("/payments/", json=payment_data)
        assert create_response.status_code == 201
        payment_id = create_response.json()["id"]
        
        # Complete once
        first_complete = client.post(
            f"/payments/{payment_id}/complete",
            params={"provider_transaction_id": "txn_123"}
        )
        assert first_complete.status_code == 200
        
        # Try to complete again
        response = client.post(
            f"/payments/{payment_id}/complete",
            params={"provider_transaction_id": "txn_456"}
        )
        
        assert response.status_code == 400
        assert "Cannot complete payment" in response.json()["detail"]
