

from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime

from app.models.order_model import (
    Order, OrderCreate, OrderUpdate, OrderStatus,
    OrderItem, OrderItemCreate
)


class OrderRepository:
    """
    Repository Pattern: All Order database operations
    OOP Design: Encapsulates data access logic
    """
    
    def __init__(self, session: Session):
        """
        Initialize with database session
        Dependency Injection: session provided by FastAPI
        """
        self.session = session
    
    def create(self, order_data: OrderCreate, order_number: str, total_amount: float) -> Order:
        """
        Create new order with items in database
        More complex than Product - creates Order + OrderItems
        """
        # Create main order
        order = Order(
            user_id=order_data.user_id,
            order_number=order_number,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address,
            notes=order_data.notes,
            status=OrderStatus.PENDING
        )
        
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        
        return order
    
    def add_order_items(self, order_id: int, items_data: List[dict]) -> List[OrderItem]:
        """
        Add items to an order
        items_data: list of dicts with product info and quantities
        """
        order_items = []
        
        for item in items_data:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=item['quantity'],
                price_per_unit=item['price_per_unit'],
                subtotal=item['subtotal']
            )
            self.session.add(order_item)
            order_items.append(order_item)
        
        self.session.commit()
        return order_items
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items"""
        statement = select(Order).where(Order.id == order_id)
        return self.session.exec(statement).first()
    
    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        statement = select(Order).where(Order.order_number == order_number)
        return self.session.exec(statement).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders with pagination"""
        statement = select(Order).offset(skip).limit(limit).order_by(Order.created_at.desc())
        return list(self.session.exec(statement).all())
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders for a specific user"""
        statement = select(Order).where(
            Order.user_id == user_id
        ).offset(skip).limit(limit).order_by(Order.created_at.desc())
        return list(self.session.exec(statement).all())
    
    def get_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by status (pending, confirmed, shipped, etc.)"""
        statement = select(Order).where(
            Order.status == status
        ).offset(skip).limit(limit).order_by(Order.created_at.desc())
        return list(self.session.exec(statement).all())
    
    def update(self, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        """Update existing order"""
        order = self.get_by_id(order_id)
        if not order:
            return None
        
        # Update only provided fields
        update_data = order_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)
        
        order.updated_at = datetime.utcnow()
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order
    
    def update_status(self, order_id: int, new_status: OrderStatus) -> Optional[Order]:
        """Update order status (common operation)"""
        order = self.get_by_id(order_id)
        if not order:
            return None
        
        order.status = new_status
        order.updated_at = datetime.utcnow()
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order (only if not shipped/delivered)"""
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        # Can only cancel if not shipped or delivered
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        self.session.add(order)
        self.session.commit()
        return True
    
    def hard_delete(self, order_id: int) -> bool:
        """Hard delete: permanently remove (use carefully!)"""
        order = self.get_by_id(order_id)
        if not order:
            return False
        
        # Delete order items first (foreign key constraint)
        for item in order.items:
            self.session.delete(item)
        
        # Then delete order
        self.session.delete(order)
        self.session.commit()
        return True