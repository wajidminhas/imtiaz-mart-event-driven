import pytest
import os

# Set test environment variables BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['APP_NAME'] = 'Inventory Service Test'
os.environ['DEBUG'] = 'true'

from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_inventory_session
from app.models.inventory_model import Inventory, StockMovement, StockMovementType


@pytest.fixture(name="session", scope="function")
def session_fixture():
    """
    Create a fresh database for each test
    Uses SQLite in-memory for speed
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """FastAPI TestClient with database session override"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_inventory_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def create_sample_inventory(session: Session):
    """Helper to create inventory in database"""
    def _create_inventory(**kwargs):
        default_data = {
            "product_id": 1,
            "product_name": "Test Product",
            "quantity": 100,
            "reserved_quantity": 0,
            "low_stock_threshold": 10
        }
        default_data.update(kwargs)
        
        inventory = Inventory(**default_data)
        session.add(inventory)
        session.commit()
        session.refresh(inventory)
        return inventory
    
    return _create_inventory


@pytest.fixture
def create_sample_movement(session: Session):
    """Helper to create stock movement"""
    def _create_movement(**kwargs):
        default_data = {
            "product_id": 1,
            "product_name": "Test Product",
            "movement_type": StockMovementType.IN,
            "quantity": 10,
            "notes": "Test movement"
        }
        default_data.update(kwargs)
        
        movement = StockMovement(**default_data)
        session.add(movement)
        session.commit()
        session.refresh(movement)
        return movement
    
    return _create_movement
