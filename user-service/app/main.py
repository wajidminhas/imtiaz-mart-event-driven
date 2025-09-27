

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import create_db_and_tables
from app.models.user import User
from contextlib import asynccontextmanager
from app.routers.users import router as users_router
# Create FastAPI application instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    create_db_and_tables()
    yield
    # Shutdown code (if any)
app = FastAPI(lifespan=lifespan,
              title="Imtiaz Marketplace - User Service",
    description="User management microservice for Imtiaz Marketplace",
    version="1.0.0"
)

app.include_router(
    users_router
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "User Service is running!", "service": "user-service", "version": "1.0.0"}

# Health check for monitoring
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}