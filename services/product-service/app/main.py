


from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import product_db
from app.routers import product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan Events: Startup and Shutdown
    
    Startup:
    - Create database tables
    - Initialize connections
    
    Shutdown:
    - Close connections (if needed)
    """
    # Startup
    print(" Starting Product Service...")
    product_db.create_tables()
    print(" Database tables created")
    
    yield
    
    # Shutdown
    print(" Shutting down Product Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Product Service API for Imtiaz Mart",
    version="1.0.0",
    lifespan=lifespan
)


# Include routers
app.include_router(product_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": settings.app_name,
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "service": settings.app_name,
        "status": "healthy",
        "database": "connected"
    }