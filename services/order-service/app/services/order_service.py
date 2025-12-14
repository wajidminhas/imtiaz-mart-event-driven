

from typing import List, Optional
from app.models.order_model import (
    Order, OrderCreate, OrderUpdate, OrderRead, 
    OrderStatus, OrderItemCreate
)
from app.repositories.order_repository import OrderRepository
from fastapi import HTTPException, status
from app.events.publishers import (
    publish_order_created,
    publish_order_updated,
    publish_order_cancelled
)
from datetime import datetime
import httpx


class OrderService:
    """
    Order Service: Business Logic Layer
    
    Responsibilities:
    - Business rules and validation
    - Orchestrate repository calls
    - Verify products exist (call Product Service via Dapr)
    - Calculate totals
    - Publish events
    - Handle errors and exceptions
    """
    
    def __init__(self, repository: OrderRepository):
        """
        Dependency Injection: Repository injected from route
        OOP Principle: Service depends on abstraction (repository)
        """
        self.repository = repository
        self.product_service_url = "http://imtiaz-product-service:8001"
    
    async def verify_product(self, product_id: int) -> dict:
    """Verify product exists and get details from Product Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.product_service_url}/products/{product_id}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {product_id} not found"
                )
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to verify product: {str(e)}"
        )
    
    async def calculate_order_total(self, items: List[OrderItemCreate]) -> tuple[float, List[dict]]:
        """
        Calculate order total and prepare items data
        Verifies each product exists and calculates subtotals
        
        Returns: (total_amount, items_data)
        """
        total_amount = 0.0
        items_data = []
        
        for item in items:
            # Verify product exists and get current price
            product = await self.verify_product(item.product_id)
            
            # Check if product is active
            if not product.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product['name']} is not available"
                )
            
            # Check stock availability
            if product.get('stock_quantity', 0) < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product['name']}. Available: {product['stock_quantity']}"
                )
            
            # Calculate subtotal
            price = product['price']
            subtotal = price * item.quantity
            total_amount += subtotal
            
            # Prepare item data for database
            items_data.append({
                'product_id': item.product_id,
                'product_name': product['name'],
                'quantity': item.quantity,
                'price_per_unit': price,
                'subtotal': subtotal
            })
        
        return total_amount, items_data
    
    def generate_order_number(self) -> str:
        """Generate unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD-{timestamp}"
    
    async def create_order(self, order_data: OrderCreate) -> OrderRead:
        """
        Create new order with business logic
        
        Business Rules:
        - All products must exist and be active
        - Sufficient stock must be available
        - Calculate correct totals
        - Generate unique order number
        """
        try:
            # 1. Validate and calculate totals
            total_amount, items_data = await self.calculate_order_total(order_data.items)
            
            # 2. Generate order number
            order_number = self.generate_order_number()
            
            # 3. Create order via repository
            order = self.repository.create(order_data, order_number, total_amount)
            
            # 4. Add order items
            self.repository.add_order_items(order.id, items_data)
            
            # 5. Refresh order to get items
            order = self.repository.get_by_id(order.id)
            
            # 6. Publish order.created event 🔥
            event_data = {
                "order_id": order.id,
                "order_number": order.order_number,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "status": order.status,
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "price_per_unit": item.price_per_unit,
                        "subtotal": item.subtotal
                    }
                    for item in order.items
                ],
                "created_at": order.created_at.isoformat()
            }
            publish_order_created(event_data)
            
            return OrderRead.model_validate(order)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create order: {str(e)}"
            )
    
    async def get_order(self, order_id: int) -> OrderRead:
        """Get order by ID"""
        order = self.repository.get_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        return OrderRead.model_validate(order)
    
    async def get_user_orders(
        self, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[OrderRead]:
        """Get all orders for a user"""
        orders = self.repository.get_by_user_id(user_id, skip, limit)
        return [OrderRead.model_validate(order) for order in orders]
    
    async def get_all_orders(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[OrderStatus] = None
    ) -> List[OrderRead]:
        """Get all orders with optional status filter"""
        if status_filter:
            orders = self.repository.get_by_status(status_filter, skip, limit)
        else:
            orders = self.repository.get_all(skip, limit)
        
        return [OrderRead.model_validate(order) for order in orders]
    
    async def update_order_status(
        self, 
        order_id: int, 
        new_status: OrderStatus
    ) -> OrderRead:
        """
        Update order status with business logic
        
        Business Rules:
        - Cannot go from DELIVERED back to SHIPPED
        - Cannot change CANCELLED orders
        """
        order = self.repository.get_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # Business rule: Cannot change cancelled orders
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update status of cancelled order"
            )
        
        # Update status
        updated_order = self.repository.update_status(order_id, new_status)
        
        # Publish order.updated event 🔥
        event_data = {
            "order_id": updated_order.id,
            "order_number": updated_order.order_number,
            "user_id": updated_order.user_id,
            "old_status": order.status,
            "new_status": new_status,
            "updated_at": updated_order.updated_at.isoformat()
        }
        publish_order_updated(event_data)
        
        return OrderRead.model_validate(updated_order)
    
    async def cancel_order(self, order_id: int) -> dict:
        """
        Cancel order with business logic
        
        Business Rules:
        - Cannot cancel shipped or delivered orders
        """
        order = self.repository.get_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # Check if can cancel
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status}"
            )
        
        # Cancel order
        success = self.repository.cancel_order(order_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel order"
            )
        
        # Publish order.cancelled event 🔥
        event_data = {
            "order_id": order.id,
            "order_number": order.order_number,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "cancelled_at": datetime.utcnow().isoformat()
        }
        publish_order_cancelled(event_data)
        
        return {
            "message": f"Order {order.order_number} cancelled successfully",
            "order_id": order_id,
            "order_number": order.order_number
        }
