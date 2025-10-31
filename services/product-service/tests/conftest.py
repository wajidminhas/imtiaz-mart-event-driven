import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_product_session
from app.models.product_model import Product


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
    app.dependency_overrides[get_product_session] = get_session_override
    
    # Create test client
    client = TestClient(app)
    yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """Sample product data for tests"""
    return {
        "name": "Test Laptop",
        "description": "High performance laptop",
        "price": 150000.0,
        "stock_quantity": 10,
        "is_active": True
    }


@pytest.fixture
def create_sample_product(session: Session):
    """Helper to create a product in database"""
    def _create_product(**kwargs):
        default_data = {
            "name": "Sample Product",
            "description": "Test description",
            "price": 1000.0,
            "stock_quantity": 5,
            "is_active": True
        }
        default_data.update(kwargs)
        
        product = Product(**default_data)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    
    return _create_product