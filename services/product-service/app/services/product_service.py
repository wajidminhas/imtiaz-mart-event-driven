from app.domain.product import Product
from app.repositories.product_repo import ProductRepository
from shared.events.product_created_pb2 import ProductCreated
import uuid

class ProductService:
    def __init__(self, repo: ProductRepository, dapr_publisher):
        self.repo = repo
        self.dapr_publisher = dapr_publisher

    def create_product(self, name: str, description: str, price: float, category: str, brand: str = "", tags=None):
        # 1. Create domain object (validates automatically)
        product = Product(name, description, price, category, brand, tags or [])
        
        # 2. Save to DB (returns model with ID)
        product_model = self.repo.create(product)
        
        # 3. Emit event
        event = ProductCreated(
            product_id=product_model.id,
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            brand=product.brand,
            tags=product.tags,
            image_url=product.image_url or ""
        )
        
        self.dapr_publisher.publish("product-pubsub", "product-created", event)
        return product_model