from app.domain.product import Product
from app.repositories.product_repo import ProductRepository
from shared.events.product_created_pb2 import ProductCreated
import uuid
from datetime import datetime
from app.repositories.category_repo import CategoryRepository

class ProductService:
    def __init__(self, repo: ProductRepository, dapr_publisher, category_repo=CategoryRepository):
        self.repo = repo
        self.category_repo = None  # To be set externally if needed
        self.dapr_publisher = dapr_publisher

    def create_product(self, name: str, description: str, price: float, category_id: str, brand: str = "", tags=None):
        # 1. Create domain object (validates automatically)
        domain_product = Product(name, description, price, category_id, brand, tags or [])
        
        # Validate category exists
        category = self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise ValueError(f"Category with ID {category_id} does not exist or is inactive.")

        # 2. Save to DB (returns model with ID)
        product_model = self.repo.create(domain_product)
        
        # 3. Emit event
        event = ProductCreated(
            product_id=product_model.id,
            name=product_model.name,
            description=product_model.description,
            price=product_model.price,
            category=product_model.category,
            brand=product_model.brand,
            tags=product_model.tags,
            image_url=product_model.image_url or ""
        )
        
        self.dapr_publisher.publish(pubsub_name="product-pubsub", topic_name="product-created", data = event.SerializeToString())
        return product_model