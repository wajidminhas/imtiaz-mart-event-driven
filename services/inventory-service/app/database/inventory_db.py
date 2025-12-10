from sqlmodel import create_engine, Session, SQLModel
from app.config import settings


class InventoryDatabase:
    """
    Inventory Service Database Manager
    Encapsulates all database operations for Inventory Service
    True microservice isolation - no shared DB code
    """
    
    def __init__(self):
        """Initialize inventory database engine"""
        # Check if using SQLite (for tests)
        if settings.database_url.startswith("sqlite"):
            self.engine = create_engine(
                settings.database_url,
                echo=settings.debug,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                settings.database_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
    
    def create_tables(self):
        """Create all inventory-related tables (inventory + stock_movements)"""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)


# Singleton instance for Inventory Service
inventory_db = InventoryDatabase()


# Dependency Injection helper
def get_inventory_session():
    """
    FastAPI Dependency: Provides DB session to routes
    Automatically closes after request
    """
    with inventory_db.get_session() as session:
        yield session
