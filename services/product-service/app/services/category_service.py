# app/services/category_service.py
from app.repositories.category_repo import CategoryRepository
from app.domain.category import Category
from shared.events.category_created_pb2 import CategoryCreated # Import generated event class
# ... other imports for update/delete events ...

class CategoryService:
    def __init__(self, repo: CategoryRepository, dapr_publisher):
        self.repo = repo
        self.dapr_publisher = dapr_publisher

    def create_category(self, name: str, description: str | None = None):
        # Validate domain object
        domain_category = Category(name, description)
        # Save to DB
        category_model = self.repo.create(domain_category)
        # Publish event
        event = CategoryCreated(
            category_id=category_model.id,
            name=category_model.name,
            description=category_model.description or "",
            # ... other relevant fields ...
        )
        self.dapr_publisher.publish(pubsub_name="kafka-pubsub", topic_name="category-created", data=event.SerializeToString())
        return category_model

    # ... implement update, get, list, delete methods ...
    # In delete, publish CategoryDeleted event
    # In update, publish CategoryUpdated event