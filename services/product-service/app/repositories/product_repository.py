

from typing import Optional, List
from sqlmodel import Session, select
# from app.models.product import Product, ProductCreate, ProductUpdate

from datetime import datetime

from app.models.product_model import ProductCreate, ProductUpdate, Product


class ProductRepository:
    """
    Repository Pattern: All Product database operations
    OOP Design: Encapsulates data access logic
    """
    
    def __init__(self, session: Session):
        """
        Initialize with database session
        Dependency Injection: session provided by FastAPI
        """
        self.session = session
    
    def create(self, product_data: ProductCreate) -> Product:
        """Create new product in database"""
        product = Product.model_validate(product_data)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        statement = select(Product).where(Product.id == product_id)
        return self.session.exec(statement).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        statement = select(Product).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_active_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get only active products"""
        statement = select(Product).where(
            Product.is_active == True
        ).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update existing product"""
        product = self.get_by_id(product_id)
        if not product:
            return None
        
        # Update only provided fields
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product
    
    def soft_delete(self, product_id: int) -> bool:
        """Soft delete: mark product as inactive"""
        product = self.get_by_id(product_id)
        if not product:
            return False
        
        product.is_active = False
        product.updated_at = datetime.utcnow()
        self.session.add(product)
        self.session.commit()
        return True
    
    def hard_delete(self, product_id: int) -> bool:
        """Hard delete: permanently remove (use carefully!)"""
        product = self.get_by_id(product_id)
        if not product:
            return False
        
        self.session.delete(product)
        self.session.commit()
        return True