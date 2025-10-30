from sqlmodel import create_engine, Session, SQLModel
from app.config import settings


class ProductDatabase:
    """
    Product Service Database Manager
    Encapsulates all database operations for Product Service
    True microservice isolation - no shared DB code
    """
    
    def __init__(self):
        """Initialize product database engine"""
        self.engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    
    def create_tables(self):
        """Create all product-related tables"""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)


# Singleton instance for Product Service
product_db = ProductDatabase()


# Dependency Injection helper
def get_product_session():
    """
    FastAPI Dependency: Provides DB session to routes
    Automatically closes after request
    """
    with product_db.get_session() as session:
        yield session