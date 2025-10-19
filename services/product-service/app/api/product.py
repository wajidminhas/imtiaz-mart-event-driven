

from fastapi import APIRouter, Depends
from app.services.product_service import ProductService
from app.repositories.product_repo import ProductRepository
from app.database import get_session
from dapr.clients import DaprClient  # or HTTP client

router = APIRouter()

def get_dapr_client():
    return DaprClient()  # or use HTTP if preferred

@router.post("/products")
def create_product(
    name: str,
    description: str,
    price: float,
    category: str,
    brand: str = "",
    tags: list[str] = None,
    session=Depends(get_session),
    dapr=Depends(get_dapr_client)
):
    repo = ProductRepository(session)
    service = ProductService(repo=repo, dapr_publisher=dapr)
    product = service.create_product(name, description, price, category, brand, tags)
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "created_at": product.created_at
    }