

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import List

from app.models.product_model import ProductCreate, ProductUpdate, ProductRead
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.database import get_product_session


# Create router with prefix and tags
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def get_product_service(
    session: Session = Depends(get_product_session)
) -> ProductService:
    """
    Dependency Injection: Creates service with repository
    
    Flow:
    1. FastAPI injects DB session
    2. Create repository with session
    3. Create service with repository
    4. Return service to route handler
    """
    repository = ProductRepository(session)
    return ProductService(repository)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product",
    description="Create a new product in the catalog"
)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Create Product Endpoint
    
    - **name**: Product name (required)
    - **description**: Product description (optional)
    - **price**: Product price (must be > 0)
    - **stock_quantity**: Available stock (default: 0)
    - **is_active**: Product status (default: true)
    """
    return await service.create_product(product_data)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get product by ID",
    description="Retrieve a single product by its ID"
)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get product by ID"""
    return await service.get_product(product_id)


@router.get(
    "/",
    response_model=List[ProductRead],
    summary="Get all products",
    description="Retrieve all products with pagination"
)
async def get_all_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    active_only: bool = Query(True, description="Return only active products"),
    service: ProductService = Depends(get_product_service)
):
    """
    Get all products with pagination
    
    - **skip**: Offset for pagination (default: 0)
    - **limit**: Max items to return (default: 100, max: 500)
    - **active_only**: Filter active products only (default: true)
    """
    return await service.get_all_products(skip, limit, active_only)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update product",
    description="Update an existing product"
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    """
    Update product by ID
    
    Only provided fields will be updated
    """
    return await service.update_product(product_id, product_data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete product",
    description="Soft delete product (mark as inactive)"
)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Soft delete product (marks as inactive)
    
    Product data is preserved for historical records
    """
    return await service.delete_product(product_id)


@router.get(
    "/{product_id}/stock",
    summary="Check product stock",
    description="Check if product is in stock"
)
async def check_stock(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    """
    Check product stock availability
    
    Returns stock quantity and availability status
    """
    return await service.check_stock(product_id)