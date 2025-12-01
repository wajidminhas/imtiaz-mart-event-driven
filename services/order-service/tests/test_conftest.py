

import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_order_session
from app.models.order_model import Order, OrderItem, OrderStatus


# Create in-memory SQLite database for testing
@pytest.fixture(name="session", scope="function")
def session_fixture():
    """
    Create a fresh database for each test
    Uses SQLite in-memory for speed
    """
    # Create in-memory database engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    # Create session
    with Session(engine) as session:
        yield session
    
    # Cleanup after test
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    FastAPI TestClient with database session override
    """
    def get_session_override():
        return session
    
    # Override dependency
    app.dependency_overrides[get_order_session] = get_session_override
    
    # Create test client
    client = TestClient(app)
    yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_order_data():
    """Sample order data for tests"""
    return {
        "user_id": 1,
        "shipping_address": "123 Test Street, Mingora, KP",
        "notes": "Test order",
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            },
            {
                "product_id": 2,
                "quantity": 1
            }
        ]
    }


@pytest.fixture
def create_sample_order(session: Session):
    """Helper to create an order in database"""
    def _create_order(**kwargs):
        default_data = {
            "user_id": 1,
            "order_number": "ORD-TEST-001",
            "total_amount": 5000.0,
            "status": OrderStatus.PENDING,
            "shipping_address": "Test Address",
            "notes": "Test order"
        }
        default_data.update(kwargs)
        
        order = Order(**default_data)
        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    
    return _create_order


@pytest.fixture
def create_sample_order_item(session: Session):
    """Helper to create order items"""
    def _create_order_item(order_id: int, **kwargs):
        default_data = {
            "order_id": order_id,
            "product_id": 1,
            "product_name": "Test Product",
            "quantity": 2,
            "price_per_unit": 1000.0,
            "subtotal": 2000.0
        }
        default_data.update(kwargs)
        
        order_item = OrderItem(**default_data)
        session.add(order_item)
        session.commit()
        session.refresh(order_item)
        return order_item
    
    return _create_order_item