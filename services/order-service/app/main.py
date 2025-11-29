

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import order_db
from app.routers import order_router


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
    print("🚀 Starting Order Service...")
    order_db.create_tables()
    print("✅ Database tables created")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Order Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Order Service API for Imtiaz Mart - Handles order creation, tracking, and management",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(order_router)


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
        "database": "connected",
        "port": settings.service_port
    }