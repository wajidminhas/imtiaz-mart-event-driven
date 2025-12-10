

from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime

from app.models.inventory_model import (
    Inventory, InventoryCreate, InventoryUpdate,
    StockMovement, StockMovementCreate, StockMovementType
)


class InventoryRepository:
    """
    Repository Pattern: All Inventory database operations
    OOP Design: Encapsulates data access logic
    """
    
    def __init__(self, session: Session):
        """
        Initialize with database session
        Dependency Injection: session provided by FastAPI
        """
        self.session = session
    
    # ============================================
    # INVENTORY OPERATIONS
    # ============================================
    
    def create(self, inventory_data: InventoryCreate) -> Inventory:
        """Create new inventory record"""
        inventory = Inventory.model_validate(inventory_data)
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory
    
    def get_by_id(self, inventory_id: int) -> Optional[Inventory]:
        """Get inventory by ID"""
        statement = select(Inventory).where(Inventory.id == inventory_id)
        return self.session.exec(statement).first()
    
    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        """Get inventory by product ID"""
        statement = select(Inventory).where(Inventory.product_id == product_id)
        return self.session.exec(statement).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Inventory]:
        """Get all inventory records with pagination"""
        statement = select(Inventory).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_low_stock_items(self) -> List[Inventory]:
        """Get items with stock below threshold"""
        statement = select(Inventory).where(
            Inventory.quantity < Inventory.low_stock_threshold
        )
        return list(self.session.exec(statement).all())
    
    def get_out_of_stock_items(self) -> List[Inventory]:
        """Get items with zero stock"""
        statement = select(Inventory).where(Inventory.quantity == 0)
        return list(self.session.exec(statement).all())
    
    def update(self, inventory_id: int, inventory_data: InventoryUpdate) -> Optional[Inventory]:
        """Update existing inventory"""
        inventory = self.get_by_id(inventory_id)
        if not inventory:
            return None
        
        # Update only provided fields
        update_data = inventory_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(inventory, key, value)
        
        inventory.updated_at = datetime.utcnow()
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory
    
    def update_quantity(self, product_id: int, quantity_change: int) -> Optional[Inventory]:
        """
        Update inventory quantity (add or subtract)
        quantity_change: positive to add, negative to subtract
        """
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            return None
        
        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            return None  # Cannot go negative
        
        inventory.quantity = new_quantity
        inventory.updated_at = datetime.utcnow()
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory
    
    def reserve_stock(self, product_id: int, quantity: int) -> bool:
        """
        Reserve stock for an order
        Moves quantity from available to reserved
        """
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            return False
        
        # Check if enough stock available
        if inventory.quantity < quantity:
            return False
        
        inventory.quantity -= quantity
        inventory.reserved_quantity += quantity
        inventory.updated_at = datetime.utcnow()
        self.session.add(inventory)
        self.session.commit()
        return True
    
    def release_reserved_stock(self, product_id: int, quantity: int) -> bool:
        """
        Release reserved stock (when order cancelled)
        Moves quantity from reserved back to available
        """
        inventory = self.get_by_product_id(product_id)
        if not inventory:
            return False
        
        if inventory.reserved_quantity < quantity:
            return False
        
        inventory.reserved_quantity -= quantity
        inventory.quantity += quantity
        inventory.updated_at = datetime.utcnow()
        self.session.add(inventory)
        self.session.commit()
        return True
    
    # ============================================
    # STOCK MOVEMENT OPERATIONS (Audit Trail)
    # ============================================
    
    def create_stock_movement(self, movement_data: StockMovementCreate) -> StockMovement:
        """Create stock movement record (audit trail)"""
        movement = StockMovement.model_validate(movement_data)
        self.session.add(movement)
        self.session.commit()
        self.session.refresh(movement)
        return movement
    
    def get_movements_by_product(self, product_id: int, skip: int = 0, limit: int = 50) -> List[StockMovement]:
        """Get all movements for a product"""
        statement = select(StockMovement).where(
            StockMovement.product_id == product_id
        ).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_movements_by_order(self, order_id: int) -> List[StockMovement]:
        """Get all movements for an order"""
        statement = select(StockMovement).where(
            StockMovement.order_id == order_id
        ).order_by(StockMovement.created_at.desc())
        return list(self.session.exec(statement).all())
    
    def get_all_movements(self, skip: int = 0, limit: int = 100) -> List[StockMovement]:
        """Get all stock movements with pagination"""
        statement = select(StockMovement).order_by(
            StockMovement.created_at.desc()
        ).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())