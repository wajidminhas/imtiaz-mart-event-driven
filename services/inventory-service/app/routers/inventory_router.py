

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import List

from app.models.inventory_model import (
    InventoryCreate, InventoryUpdate, InventoryRead,
    StockMovementRead, StockAdjustment
)
from app.services.inventory_service import InventoryService
from app.repositories.inventory_repository import InventoryRepository
from app.database import get_inventory_session


# Create router with prefix and tags
router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


def get_inventory_service(
    session: Session = Depends(get_inventory_session)
) -> InventoryService:
    """
    Dependency Injection: Creates service with repository
    
    Flow:
    1. FastAPI injects DB session
    2. Create repository with session
    3. Create service with repository
    4. Return service to route handler
    """
    repository = InventoryRepository(session)
    return InventoryService(repository)


@router.post(
    "/",
    response_model=InventoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create inventory record",
    description="Create inventory record for a product"
)
async def create_inventory(
    inventory_data: InventoryCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Create Inventory Record
    
    - **product_id**: Product ID (required)
    - **product_name**: Product name (required)
    - **quantity**: Initial stock quantity (default: 0)
    - **low_stock_threshold**: Alert threshold (default: 10)
    """
    return await service.create_inventory(inventory_data)


@router.get(
    "/{inventory_id}",
    response_model=InventoryRead,
    summary="Get inventory by ID",
    description="Retrieve inventory record by ID"
)
async def get_inventory(
    inventory_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get inventory by ID"""
    return await service.get_inventory(inventory_id)


@router.get(
    "/product/{product_id}",
    response_model=InventoryRead,
    summary="Get inventory by product ID",
    description="Retrieve inventory for a specific product"
)
async def get_inventory_by_product(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get inventory by product ID
    
    Returns stock level, reserved quantity, and availability status
    """
    return await service.get_inventory_by_product(product_id)


@router.get(
    "/",
    response_model=List[InventoryRead],
    summary="Get all inventory",
    description="Retrieve all inventory records with pagination"
)
async def get_all_inventory(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get all inventory records
    
    - **skip**: Offset for pagination (default: 0)
    - **limit**: Max items to return (default: 100, max: 500)
    """
    return await service.get_all_inventory(skip, limit)


@router.get(
    "/alerts/low-stock",
    response_model=List[InventoryRead],
    summary="Get low stock items",
    description="Retrieve items with stock below threshold"
)
async def get_low_stock_items(
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get low stock items
    
    Returns all products where current quantity is below the low stock threshold
    """
    return await service.get_low_stock_items()


@router.post(
    "/adjust",
    response_model=InventoryRead,
    summary="Adjust stock",
    description="Manual stock adjustment (add or remove stock)"
)
async def adjust_stock(
    adjustment: StockAdjustment,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Adjust Stock Manually
    
    - **product_id**: Product to adjust (required)
    - **quantity_change**: Amount to add (positive) or remove (negative)
    - **notes**: Reason for adjustment (optional)
    
    Business Rules:
    - Cannot reduce stock below zero
    - Creates audit trail in stock movements
    - Publishes events for low stock / out of stock
    """
    return await service.adjust_stock(adjustment)


@router.get(
    "/movements/product/{product_id}",
    response_model=List[StockMovementRead],
    summary="Get product stock movements",
    description="Get stock movement history for a product"
)
async def get_product_movements(
    product_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get Stock Movement History for Product
    
    Returns audit trail of all stock changes:
    - IN: Stock added (restock)
    - OUT: Stock removed (order)
    - RETURN: Stock returned (order cancelled)
    - ADJUSTMENT: Manual adjustment
    """
    return await service.get_product_movements(product_id, skip, limit)