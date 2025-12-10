"""
Event Consumers for Inventory Service

Subscribes to events from other services via Dapr Pub/Sub
Handles: product.created, order.created, order.cancelled
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List, Any
from app.database import get_inventory_session


# Create router for Dapr subscriptions
router = APIRouter()


# ============================================
# CLOUD EVENT MODELS
# ============================================

class CloudEvent(BaseModel):
    """Dapr CloudEvent wrapper"""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: dict
    topic: str
    pubsubname: str


# ============================================
# DAPR SUBSCRIPTION ENDPOINT
# ============================================

@router.get("/dapr/subscribe")
def subscribe():
    """Tell Dapr which topics to subscribe to"""
    subscriptions = [
        {
            "pubsubname": "imtiaz-pubsub",
            "topic": "product.created",
            "route": "/events/product-created"
        },
        {
            "pubsubname": "imtiaz-pubsub",
            "topic": "order.created",
            "route": "/events/order-created"
        },
        {
            "pubsubname": "imtiaz-pubsub",
            "topic": "order.cancelled",
            "route": "/events/order-cancelled"
        }
    ]
    return subscriptions


# ============================================
# EVENT HANDLERS
# ============================================

@router.post("/events/product-created")
async def handle_product_created(event: CloudEvent):
    """Handle product.created events"""
    # Import here to avoid circular import
    from app.services.inventory_service import InventoryService
    from app.repositories.inventory_repository import InventoryRepository
    
    try:
        print("=" * 60)
        print("📦 PRODUCT CREATED EVENT RECEIVED!")
        print("=" * 60)
        
        product_data = event.data
        print(f"Product ID: {product_data.get('product_id')}")
        print(f"Name: {product_data.get('name')}")
        
        with next(get_inventory_session()) as session:
            repo = InventoryRepository(session)
            service = InventoryService(repo)
            await service.handle_product_created(product_data)
        
        print("=" * 60)
        return {"status": "SUCCESS"}
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "RETRY"}


@router.post("/events/order-created")
async def handle_order_created(event: CloudEvent):
    """Handle order.created events"""
    from app.services.inventory_service import InventoryService
    from app.repositories.inventory_repository import InventoryRepository
    
    try:
        print("=" * 60)
        print("🛒 ORDER CREATED EVENT RECEIVED!")
        print("=" * 60)
        
        order_data = event.data
        print(f"Order ID: {order_data.get('order_id')}")
        
        with next(get_inventory_session()) as session:
            repo = InventoryRepository(session)
            service = InventoryService(repo)
            await service.handle_order_created(order_data)
        
        print("=" * 60)
        return {"status": "SUCCESS"}
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "RETRY"}


@router.post("/events/order-cancelled")
async def handle_order_cancelled(event: CloudEvent):
    """Handle order.cancelled events"""
    from app.services.inventory_service import InventoryService
    from app.repositories.inventory_repository import InventoryRepository
    
    try:
        print("=" * 60)
        print("❌ ORDER CANCELLED EVENT RECEIVED!")
        print("=" * 60)
        
        order_data = event.data
        print(f"Order ID: {order_data.get('order_id')}")
        
        with next(get_inventory_session()) as session:
            repo = InventoryRepository(session)
            service = InventoryService(repo)
            await service.handle_order_cancelled(order_data)
        
        print("=" * 60)
        return {"status": "SUCCESS"}
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "RETRY"}