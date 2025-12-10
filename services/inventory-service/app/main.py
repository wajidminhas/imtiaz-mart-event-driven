

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.database import inventory_db
from app.routers import inventory_router
from app.events import event_consumer_router


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
    print("🚀 Starting Inventory Service...")
    inventory_db.create_tables()
    print("✅ Database tables created")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Inventory Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Inventory Service API for Imtiaz Mart - Manages stock levels, tracks movements, and handles inventory events",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(inventory_router)
app.include_router(event_consumer_router)  # Event consumers for Dapr


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