

from fastapi import APIRouter, Depends, HTTPException
from app.services.product_service import ProductService
from app.repositories.product_repo import ProductRepository
from app.database import get_session
from dapr.clients import DaprClient  # or HTTP client
from typing import Optional, List
from app.database import get_session
from app.repositories.category_repo import CategoryRepository  # Import CategoryRepository

router = APIRouter()

def get_dapr_client():
    return DaprClient()  # or use HTTP if preferred

def get_product_service(
    session=Depends(get_session),
    dapr_client=Depends(get_dapr_client)
) -> ProductService:
    """Dependency to get ProductService instance with required dependencies."""
    product_repo = ProductRepository(session)
    category_repo = CategoryRepository(session) # Create CategoryRepo instance
    return ProductService(repo=product_repo, category_repo=category_repo, dapr_publisher=dapr_client)

# --- Product Endpoints ---

@router.post("/", status_code=201)
def create_product(
    name: str,
    description: str,
    price: float,
    category_id: str, # Accept category_id as a string parameter
    brand: str = "",
    tags: Optional[List[str]] = None, # Accept tags as a list
    image_url: str = "", # Add image_url parameter
    product_service: ProductService = Depends(get_product_service) # Inject ProductService
):
    """
    Create a new product.
    """
    try:
        # Call the service method which handles validation, saving, and event publishing
        product = product_service.create_product(
            name=name,
            description=description,
            price=price,
            category_id=category_id, # Pass the category_id
            brand=brand,
            tags=tags,
            image_url=image_url
        )
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category_id": product.category_id, # Return the associated category_id
            "brand": product.brand,
            "tags": product.tags.split(",") if product.tags else [], # Assuming tags are stored as comma-separated string
            "image_url": product.image_url,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }
    except ValueError as e: # Catch validation errors (e.g., category not found)
        raise HTTPException(status_code=400, detail=str(e))
   

    #  ************************** GET BY ID ENDPOINTS  **************************
    
  
@router.get("/{product_id}", status_code=200)
def get_product(
    product_id: str,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve a single product by its ID.
    """
    product = product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category_id": product.category_id,
        "brand": product.brand,
        "tags": product.tags.split(",") if product.tags else [],
        "image_url": product.image_url,
        "is_active": product.is_active,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        # "deleted_at": product.deleted_at.isoformat() if product.deleted_at else None, # Include if needed for soft-deleted items
    }
    
#  *************************** LIST ENDPOINTS  **************************

@router.get("/", status_code=200)
def list_products(
    category_id: Optional[str] = None, # Query parameter for filtering
    is_active: Optional[bool] = True, # Query parameter for filtering active status
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve a list of products, optionally filtered by category ID and active status.
    """
    # Note: The current ProductService.list_products only takes category_id.
    # You might want to enhance ProductService and ProductRepository to accept is_active filter too.
    # For now, filtering by is_active is not implemented in the service/repo layer based on the previous code.
    products = product_service.list_products(category_id=category_id)
    # Optional: Apply is_active filter in the API layer if not done in the service/repo layer
    if is_active is not None:
        products = [p for p in products if p.is_active == is_active]

    return [
        {
            "id": prod.id,
            "name": prod.name,
            "description": prod.description,
            "price": prod.price,
            "category_id": prod.category_id,
            "brand": prod.brand,
            "tags": prod.tags.split(",") if prod.tags else [],
            "image_url": prod.image_url,
            "is_active": prod.is_active,
            "created_at": prod.created_at.isoformat() if prod.created_at else None,
            "updated_at": prod.updated_at.isoformat() if prod.updated_at else None,
        }
        for prod in products
    ]
    

#  *************************** UPDATE ENDPOINTS  **************************

@router.put("/{product_id}", status_code=200)
def update_product(
    product_id: str,
    name: str = None,
    description: str = None,
    price: float = None,
    category_id: str = None, # Allow updating category_id
    brand: str = None,
    tags: Optional[List[str]] = None, # Allow updating tags
    image_url: str = None, # Allow updating image_url
    product_service: ProductService = Depends(get_product_service)
):
    """
    Update an existing product.
    """
    try:
        # Prepare updates dictionary, only including non-None values passed in.
        updates = {}
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description
        if price is not None:
            updates['price'] = price
        if category_id is not None:
            updates['category_id'] = category_id
        if brand is not None:
            updates['brand'] = brand
        if tags is not None:
            updates['tags'] = ",".join(tags) # Assuming tags are stored as comma-separated string
        if image_url is not None:
            updates['image_url'] = image_url

        updated_product = product_service.update_product(product_id=product_id, **updates)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "id": updated_product.id,
            "name": updated_product.name,
            "description": updated_product.description,
            "price": updated_product.price,
            "category_id": updated_product.category_id,
            "brand": updated_product.brand,
            "tags": updated_product.tags.split(",") if updated_product.tags else [],
            "image_url": updated_product.image_url,
            "is_active": updated_product.is_active,
            "updated_at": updated_product.updated_at.isoformat() if updated_product.updated_at else None,
        }
    except ValueError as e: # Catch validation errors (e.g., category not found if category_id is updated)
        raise HTTPException(status_code=400, detail=str(e))


    #  ************************** DELETE ENDPOINTS  **************************
    
@router.delete("/{product_id}", status_code=204) # 204 No Content is standard for successful deletes
def delete_product(
    product_id: str,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Delete (soft delete) a product.
    """
    deleted_product = product_service.delete_product(product_id=product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    # Return 204 No Content on successful deletion
    return

    
