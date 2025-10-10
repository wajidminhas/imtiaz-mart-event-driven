

"""
Database connection and session management
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.config import settings


# Create database engine
engine = create_engine(
    settings.get_database_url,
    echo=settings.debug,  # SQL logging in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_size=5,          # Connection pool size
    max_overflow=10       # Additional connections if pool is full
)


def create_db_and_tables():
    """
    Create all database tables
    Called on application startup
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions
    Ensures session is properly closed after use
    
    Usage in FastAPI:
        @app.get("/products")
        def get_products(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


# For direct usage in scripts/tests
def get_session_context():
    """
    Context manager for direct session usage
    
    Usage:
        with get_session_context() as session:
            result = session.exec(select(Product)).all()
    """
    return Session(engine)