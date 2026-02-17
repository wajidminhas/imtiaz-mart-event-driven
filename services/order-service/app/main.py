from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import order_db
from app.routers import order_router
import time
from urllib.request import urlopen, Request
from urllib.error import URLError
import asyncio


async def wait_for_dapr_async(max_retries: int = 30, retry_delay: int = 2) -> bool:
    """
    Wait for Dapr sidecar to be ready (non-blocking)
    This runs AFTER the app starts listening
    """
    dapr_health_url = f"http://localhost:{settings.dapr_http_port}/v1.0/healthz"
    
    print(f"⏳ Checking for Dapr sidecar on port {settings.dapr_http_port}...")
    
    for attempt in range(max_retries):
        try:
            req = Request(dapr_health_url, method="GET")
            with urlopen(req, timeout=2) as response:
                if response.status == 204:
                    print(f"✅ Dapr sidecar is ready!")
                    return True
        except URLError:
            if attempt < max_retries - 1:
                print(f"⏳ Attempt {attempt + 1}/{max_retries}: Waiting for Dapr...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"⚠️ Dapr sidecar not ready after {max_retries} attempts")
                print(f"⚠️ Events may fail to publish until Dapr starts")
                return False
        except Exception as e:
            print(f"⚠️ Error checking Dapr health: {e}")
            await asyncio.sleep(retry_delay)
    
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan Events: Startup and Shutdown
    
    Startup:
    - Create database tables
    - Start background task to wait for Dapr
    
    Shutdown:
    - Close connections (if needed)
    """
    # Startup
    print("🚀 Starting Order Service...")
    
    order_db.create_tables()
    print("✅ Database tables created")
    
    # Check for Dapr in background (non-blocking)
    asyncio.create_task(wait_for_dapr_async())
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Order Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Order Service API for Imtiaz Mart",
    version="1.0.0",
    lifespan=lifespan
)


# Include routers
app.include_router(order_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
