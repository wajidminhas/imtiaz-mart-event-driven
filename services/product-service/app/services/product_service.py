# app/services/product_service.py

from app.domain.product import Product
from app.repositories.product_repo import ProductRepository
from app.repositories.category_repo import CategoryRepository # Import the class
from shared.events.product_created_pb2 import ProductCreated # Import the generated event class
# Import other generated event classes if needed (e.g., ProductUpdated, ProductDeleted)
# from shared.events.product_updated_pb2 import ProductUpdated
# from shared.events.product_deleted_pb2 import ProductDeleted
import uuid
from datetime import datetime, timezone # Import timezone for consistency if needed

class ProductService:
    def __init__(self, repo: ProductRepository, category_repo: CategoryRepository, dapr_publisher):
        # Receive instances of dependencies via constructor (Dependency Injection)
        self.repo = repo
        self.category_repo = category_repo # Store the instance passed from outside
        self.dapr_publisher = dapr_publisher

    def create_product(self, name: str, description: str, price: float, category_id: str, brand: str = "", tags: list[str] | None = None):
        # 1. Validate category exists using the injected repository
        category = self.category_repo.get_by_id(category_id)
        if not category or not category.is_active:
            raise ValueError(f"Category with ID {category_id} does not exist or is inactive.")

        # 2. Create domain object (validates core attributes like name, price)
        # Pass the validated category_id to the domain object
        domain_product = Product(name, description, price, category_id, brand, tags or [])

        # 3. Save to DB (returns model with ID)
        product_model = self.repo.create(domain_product)

        # 4. Emit event
        event = ProductCreated(
            product_id=product_model.id,
            name=product_model.name,
            description=product_model.description,
            price=product_model.price,
            # category_id=product_model.category_id, # Use the ID, not the relationship object
            category_id=product_model.category_id, # Assuming ProductModel has category_id
            brand=product_model.brand,
            tags=product_model.tags.split(",") if product_model.tags else [], # Assuming tags are stored as comma-separated string
            image_url=product_model.image_url or ""
        )

        # Publish the event using Dapr
        # Ensure pubsub_name matches the name in your Dapr component file (e.g., pubsub-kafka.yaml)
        # Ensure topic_name matches the topic name used by other services listening for this event
        self.dapr_publisher.publish(
            pubsub_name="kafka-pubsub", # Or "product-pubsub" if that's the name in your component file
            topic_name="product-created",
            data=event.SerializeToString()
        )
        return product_model

    # Add other methods like get_product, list_products, update_product, delete_product
    # Remember to publish relevant events (ProductUpdated, ProductDeleted) in update/delete methods
    # Example for get_product:
    def get_product(self, product_id: str):
        return self.repo.get_by_id(product_id)

    def list_products(self, category_id: str | None = None):
        return self.repo.list_all(category_id=category_id)

    def update_product(self, product_id: str, **updates):
        # Validate category_id if it's being updated
        if 'category_id' in updates:
             category = self.category_repo.get_by_id(updates['category_id'])
             if not category or not category.is_active:
                 raise ValueError(f"Category with ID {updates['category_id']} does not exist or is inactive.")

        product_model = self.repo.update(product_id, **updates)
        if product_model:
            # Publish ProductUpdated event here
            # from shared.events.product_updated_pb2 import ProductUpdated
            # event = ProductUpdated(...)
            # self.dapr_publisher.publish(...)
            pass # Placeholder for event publishing logic
        return product_model

    def delete_product(self, product_id: str):
        product_model = self.repo.soft_delete(product_id)
        if product_model:
            # Publish ProductDeleted event here
            # from shared.events.product_deleted_pb2 import ProductDeleted
            # event = ProductDeleted(...)
            # self.dapr_publisher.publish(...)
            pass # Placeholder for event publishing logic
        return product_model

# --- Example of how this service would be instantiated (typically in your API layer or dependency injection setup) ---
# product_repo_instance = ProductRepository(session=some_sqlmodel_session)
# category_repo_instance = CategoryRepository(session=some_sqlmodel_session) # Same session or different if needed
# dapr_publisher_instance = DaprClient() # Or however you initialize it
# product_service = ProductService(repo=product_repo_instance, category_repo=category_repo_instance, dapr_publisher=dapr_publisher_instance)