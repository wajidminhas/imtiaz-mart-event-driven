

# services/product-service/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
# from adatabase import create_db_and_tables, get_session
from app.database import create_db_and_tables
# from app.api.products import router as products_router
from app.api.product import router as products_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Imtiaz Marketplace - Product Service",
    description="Product catalog microservice for Imtiaz Marketplace",
    version="1.0.0"
)

app.include_router(products_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Product Service is running!", "service": "product-service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}