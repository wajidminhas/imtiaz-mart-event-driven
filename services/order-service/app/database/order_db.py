# Copy code from artifact above
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings


class OrderDatabase:
    """
    Order Service Database Manager
    Encapsulates all database operations for Order Service
    True microservice isolation - no shared DB code
    """
    
    def __init__(self):
        """Initialize order database engine"""
        self.engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    
    def create_tables(self):
        """Create all order-related tables (orders + order_items)"""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)


# Singleton instance for Order Service
order_db = OrderDatabase()


# Dependency Injection helper
def get_order_session():
    """
    FastAPI Dependency: Provides DB session to routes
    Automatically closes after request
    """
    with order_db.get_session() as session:
        yield session