

from typing import List, Optional
from app.models.inventory_model import (
    Inventory, InventoryCreate, InventoryUpdate, InventoryRead,
    StockMovement, StockMovementCreate, StockMovementRead,
    StockMovementType, StockAdjustment
)
from app.repositories.inventory_repository import InventoryRepository
from fastapi import HTTPException, status
from app.events.publishers import (
    publish_inventory_low_stock,
    publish_inventory_out_of_stock,
    publish_inventory_restocked
)
from datetime import datetime


class InventoryService:
    """
    Inventory Service: Business Logic Layer
    
    Responsibilities:
    - Business rules and validation
    - Orchestrate repository calls
    - Handle stock reservations
    - Publish events (low stock, out of stock)
    - Process events from other services (order created, cancelled)
    - Handle errors and exceptions
    """
    
    def __init__(self, repository: InventoryRepository):
        """
        Dependency Injection: Repository injected from route
        OOP Principle: Service depends on abstraction (repository)
        """
        self.repository = repository
    
    # ============================================
    # INVENTORY OPERATIONS
    # ============================================
    
    async def create_inventory(self, inventory_data: InventoryCreate) -> InventoryRead:
        """Create new inventory record"""
        try:
            # Check if inventory already exists for this product
            existing = self.repository.get_by_product_id(inventory_data.product_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Inventory already exists for product {inventory_data.product_id}"
                )
            
            # Create inventory
            inventory = self.repository.create(inventory_data)
            
            # Create stock movement for initial stock
            if inventory.quantity > 0:
                movement = StockMovementCreate(
                    product_id=inventory.product_id,
                    product_name=inventory.product_name,
                    movement_type=StockMovementType.IN,
                    quantity=inventory.quantity,
                    notes="Initial stock"
                )
                self.repository.create_stock_movement(movement)
            
            return self._to_inventory_read(inventory)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create inventory: {str(e)}"
            )
    
    async def get_inventory(self, inventory_id: int) -> InventoryRead:
        """Get inventory by ID"""
        inventory = self.repository.get_by_id(inventory_id)
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory with ID {inventory_id} not found"
            )
        
        return self._to_inventory_read(inventory)
    
    async def get_inventory_by_product(self, product_id: int) -> InventoryRead:
        """Get inventory by product ID"""
        inventory = self.repository.get_by_product_id(product_id)
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory for product {product_id} not found"
            )
        
        return self._to_inventory_read(inventory)
    
    async def get_all_inventory(self, skip: int = 0, limit: int = 100) -> List[InventoryRead]:
        """Get all inventory records"""
        inventories = self.repository.get_all(skip, limit)
        return [self._to_inventory_read(inv) for inv in inventories]
    
    async def get_low_stock_items(self) -> List[InventoryRead]:
        """Get items with low stock"""
        inventories = self.repository.get_low_stock_items()
        return [self._to_inventory_read(inv) for inv in inventories]
    
    async def adjust_stock(self, adjustment: StockAdjustment) -> InventoryRead:
        """
        Manual stock adjustment (add or remove stock)
        
        Business Rules:
        - Cannot go below zero
        - Must record movement for audit
        """
        inventory = self.repository.get_by_product_id(adjustment.product_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory for product {adjustment.product_id} not found"
            )
        
        # Update quantity
        updated_inventory = self.repository.update_quantity(
            adjustment.product_id,
            adjustment.quantity_change
        )
        
        if not updated_inventory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reduce stock below zero"
            )
        
        # Record movement
        movement = StockMovementCreate(
            product_id=adjustment.product_id,
            product_name=inventory.product_name,
            movement_type=StockMovementType.ADJUSTMENT,
            quantity=adjustment.quantity_change,
            notes=adjustment.notes or "Manual adjustment"
        )
        self.repository.create_stock_movement(movement)
        
        # Check if restocked and publish event
        if adjustment.quantity_change > 0 and inventory.quantity == 0:
            publish_inventory_restocked({
                "product_id": updated_inventory.product_id,
                "product_name": updated_inventory.product_name,
                "new_quantity": updated_inventory.quantity,
                "restocked_at": datetime.utcnow().isoformat()
            })
        
        return self._to_inventory_read(updated_inventory)
    
    # ============================================
    # EVENT HANDLERS (Consume from Kafka)
    # ============================================
    
    async def handle_product_created(self, event_data: dict):
        """
        Handle product.created event
        Automatically create inventory record for new product
        """
        try:
            # Check if inventory already exists
            existing = self.repository.get_by_product_id(event_data['product_id'])
            if existing:
                return  # Already exists, skip
            
            # Create inventory with initial stock from product
            inventory_data = InventoryCreate(
                product_id=event_data['product_id'],
                product_name=event_data['name'],
                quantity=event_data.get('stock_quantity', 0),
                low_stock_threshold=10
            )
            
            await self.create_inventory(inventory_data)
            print(f"✅ Created inventory for product {event_data['product_id']}")
        
        except Exception as e:
            print(f"❌ Error handling product.created: {e}")
    
    async def handle_order_created(self, event_data: dict):
        """
        Handle order.created event
        Reduce stock for ordered items
        """
        try:
            order_id = event_data['order_id']
            items = event_data.get('items', [])
            
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                # Get inventory
                inventory = self.repository.get_by_product_id(product_id)
                if not inventory:
                    print(f"⚠️ Inventory not found for product {product_id}")
                    continue
                
                # Reduce stock
                updated = self.repository.update_quantity(product_id, -quantity)
                if not updated:
                    print(f"⚠️ Failed to reduce stock for product {product_id}")
                    continue
                
                # Record movement
                movement = StockMovementCreate(
                    product_id=product_id,
                    product_name=item['product_name'],
                    movement_type=StockMovementType.OUT,
                    quantity=-quantity,
                    order_id=order_id,
                    notes=f"Order {event_data['order_number']}"
                )
                self.repository.create_stock_movement(movement)
                
                # Check for low stock and publish events
                if updated.quantity == 0:
                    publish_inventory_out_of_stock({
                        "product_id": product_id,
                        "product_name": updated.product_name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif updated.quantity < updated.low_stock_threshold:
                    publish_inventory_low_stock({
                        "product_id": product_id,
                        "product_name": updated.product_name,
                        "current_quantity": updated.quantity,
                        "threshold": updated.low_stock_threshold,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                print(f"✅ Reduced stock for product {product_id}: {quantity} units")
        
        except Exception as e:
            print(f"❌ Error handling order.created: {e}")
    
    async def handle_order_cancelled(self, event_data: dict):
        """
        Handle order.cancelled event
        Return stock for cancelled order items
        """
        try:
            order_id = event_data['order_id']
            
            # Get movements for this order
            movements = self.repository.get_movements_by_order(order_id)
            
            for movement in movements:
                if movement.movement_type == StockMovementType.OUT:
                    # Return the stock (reverse the OUT movement)
                    product_id = movement.product_id
                    quantity = abs(movement.quantity)  # Convert negative to positive
                    
                    updated = self.repository.update_quantity(product_id, quantity)
                    if updated:
                        # Record return movement
                        return_movement = StockMovementCreate(
                            product_id=product_id,
                            product_name=movement.product_name,
                            movement_type=StockMovementType.RETURN,
                            quantity=quantity,
                            order_id=order_id,
                            notes=f"Order {event_data.get('order_number', order_id)} cancelled"
                        )
                        self.repository.create_stock_movement(return_movement)
                        
                        print(f"✅ Returned stock for product {product_id}: {quantity} units")
        
        except Exception as e:
            print(f"❌ Error handling order.cancelled: {e}")
    
    # ============================================
    # STOCK MOVEMENT OPERATIONS
    # ============================================
    
    async def get_product_movements(
        self, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[StockMovementRead]:
        """Get stock movement history for a product"""
        movements = self.repository.get_movements_by_product(product_id, skip, limit)
        return [StockMovementRead.model_validate(m) for m in movements]
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _to_inventory_read(self, inventory: Inventory) -> InventoryRead:
        """Convert Inventory model to InventoryRead with computed fields"""
        return InventoryRead(
            id=inventory.id,
            product_id=inventory.product_id,
            product_name=inventory.product_name,
            quantity=inventory.quantity,
            reserved_quantity=inventory.reserved_quantity,
            low_stock_threshold=inventory.low_stock_threshold,
            available_quantity=inventory.quantity - inventory.reserved_quantity,
            is_low_stock=inventory.quantity < inventory.low_stock_threshold,
            is_out_of_stock=inventory.quantity == 0,
            created_at=inventory.created_at,
            updated_at=inventory.updated_at
        )