# services/product-service/app/database.py

import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Import models at the module level so they are registered with SQLModel.metadata
# Adjust import paths based on your chosen filenames (e.g., product_model/category_model or product/category)
from app.models import product_model # Or from app.models import product
from app.models import category_model # Or from app.models import category
# Or import specific models:
# from app.models.product_model import ProductModel
# from app.models.category_model import CategoryModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("PRODUCT_DB_NAME")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=300)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session