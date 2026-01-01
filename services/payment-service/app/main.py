from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import payment_router
from app.config import settings
from app.database import payment_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Modern FastAPI approach (replaces on_event)
    """
    # Startup
    print("🚀 Starting Payment Service...")
    print(f"📊 Database: {settings.database_url}")
    payment_db.create_tables()
    print("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Payment Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Payment Service API for Imtiaz Mart - Handles PayFast and Stripe payments",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payment_router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check"""
    return {
        "service": settings.app_name,
        "status": "running",
        "version": "0.1.0",
        "port": 8002
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.app_name
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,  # Payment service port
        reload=True
    )
