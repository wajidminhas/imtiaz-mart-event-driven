

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import List, Optional

from app.models.order_model import OrderCreate, OrderUpdate, OrderRead, OrderStatus
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.database import get_order_session


# Create router with prefix and tags
router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_order_service(
    session: Session = Depends(get_order_session)
) -> OrderService:
    """
    Dependency Injection: Creates service with repository
    
    Flow:
    1. FastAPI injects DB session
    2. Create repository with session
    3. Create service with repository
    4. Return service to route handler
    """
    repository = OrderRepository(session)
    return OrderService(repository)


@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new order",
    description="Create a new order with items"
)
async def create_order(
    order_data: OrderCreate,
    service: OrderService = Depends(get_order_service)
):
    """
    Create Order Endpoint
    
    - **user_id**: User placing the order (required)
    - **shipping_address**: Delivery address (required)
    - **notes**: Additional notes (optional)
    - **items**: List of products with quantities (required)
    
    The service will:
    - Verify all products exist
    - Check stock availability
    - Calculate total amount
    - Generate order number
    - Create order and items
    - Publish order.created event
    """
    return await service.create_order(order_data)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Get order by ID",
    description="Retrieve a single order by its ID with all items"
)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """Get order by ID with all items"""
    return await service.get_order(order_id)


@router.get(
    "/",
    response_model=List[OrderRead],
    summary="Get all orders",
    description="Retrieve all orders with optional filters"
)
async def get_all_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get all orders with pagination and filtering
    
    - **skip**: Offset for pagination (default: 0)
    - **limit**: Max items to return (default: 100, max: 500)
    - **status**: Filter by status (optional) - pending, confirmed, shipped, delivered, cancelled
    """
    return await service.get_all_orders(skip, limit, status)


@router.get(
    "/user/{user_id}",
    response_model=List[OrderRead],
    summary="Get user's orders",
    description="Retrieve all orders for a specific user"
)
async def get_user_orders(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service)
):
    """
    Get all orders for a specific user
    
    - **user_id**: User ID to filter orders
    - **skip**: Offset for pagination
    - **limit**: Max items to return
    """
    return await service.get_user_orders(user_id, skip, limit)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Update order status",
    description="Update the status of an existing order"
)
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    service: OrderService = Depends(get_order_service)
):
    """
    Update order status
    
    - **order_id**: Order to update
    - **new_status**: New status (pending, confirmed, processing, shipped, delivered, cancelled)
    
    Business Rules:
    - Cannot change cancelled orders
    - Cannot go backwards (e.g., delivered → shipped)
    
    Publishes order.updated event
    """
    return await service.update_order_status(order_id, new_status)


@router.post(
    "/{order_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel order",
    description="Cancel an existing order"
)
async def cancel_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Cancel order
    
    Business Rules:
    - Cannot cancel shipped or delivered orders
    
    Publishes order.cancelled event
    """
    return await service.cancel_order(order_id)