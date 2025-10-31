

from typing import List, Optional
from app.models.product_model import Product, ProductCreate, ProductUpdate, ProductRead
from app.repositories.product_repository import ProductRepository
from fastapi import HTTPException, status


class ProductService:
    """
    Product Service: Business Logic Layer
    
    Responsibilities:
    - Business rules and validation
    - Orchestrate repository calls
    - Publish events (coming next)
    - Handle errors and exceptions
    """
    
    def __init__(self, repository: ProductRepository):
        """
        Dependency Injection: Repository injected from route
        OOP Principle: Service depends on abstraction (repository)
        """
        self.repository = repository
    
    async def create_product(self, product_data: ProductCreate) -> ProductRead:
        """
        Create new product with business logic
        
        Business Rules:
        - Name must be unique (add later)
        - Price must be positive (validated in model)
        - Stock cannot be negative (validated in model)
        """
        try:
            # Create product via repository
            product = self.repository.create(product_data)
            
            # TODO: Publish product.created event to Kafka
            # await self.publish_product_created(product)
            
            return ProductRead.model_validate(product)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )
    
    async def get_product(self, product_id: int) -> ProductRead:
        """Get product by ID"""
        product = self.repository.get_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        return ProductRead.model_validate(product)
    
    async def get_all_products(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[ProductRead]:
        """
        Get all products with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            active_only: Return only active products
        """
        if active_only:
            products = self.repository.get_active_products(skip, limit)
        else:
            products = self.repository.get_all(skip, limit)
        
        return [ProductRead.model_validate(p) for p in products]
    
    async def update_product(
        self, 
        product_id: int, 
        product_data: ProductUpdate
    ) -> ProductRead:
        """
        Update product with business logic
        
        Business Rules:
        - Product must exist
        - Cannot update to negative price/stock
        """
        # Check if product exists
        existing_product = self.repository.get_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # Update via repository
        updated_product = self.repository.update(product_id, product_data)
        
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product"
            )
        
        # TODO: Publish product.updated event
        # await self.publish_product_updated(updated_product)
        
        return ProductRead.model_validate(updated_product)
    
    async def delete_product(self, product_id: int) -> dict:
        """
        Soft delete product (mark as inactive)
        
        Business Rules:
        - Product must exist
        - Use soft delete to maintain history
        """
        success = self.repository.soft_delete(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # TODO: Publish product.deleted event
        # await self.publish_product_deleted(product_id)
        
        return {
            "message": f"Product {product_id} deleted successfully",
            "product_id": product_id
        }
    
    async def check_stock(self, product_id: int) -> dict:
        """
        Check product stock availability
        Business logic for inventory checks
        """
        product = self.repository.get_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        return {
            "product_id": product.id,
            "product_name": product.name,
            "stock_quantity": product.stock_quantity,
            "in_stock": product.stock_quantity > 0,
            "is_active": product.is_active
        }