# app/services/category_service.py

from app.repositories.category_repo import CategoryRepository
from app.domain.category import Category
# Import the generated Protobuf event classes for Category
from shared.events.category_created_pb2 import CategoryCreated
from shared.events.category_updated_pb2 import CategoryUpdated
from shared.events.category_deleted_pb2 import CategoryDeleted
from datetime import datetime, timezone # Import timezone for consistent timestamp formatting

class CategoryService:
    def __init__(self, repo: CategoryRepository, dapr_publisher):
        self.repo = repo
        self.dapr_publisher = dapr_publisher

    def create_category(self, name: str, description: str | None = None):
        # 1. Validate domain object
        domain_category = Category(name, description)

        # 2. Save to DB
        category_model = self.repo.create(domain_category)

        # 3. Publish event
        event = CategoryCreated(
            category_id=category_model.id,
            name=category_model.name,
            description=category_model.description or "",
            is_active=category_model.is_active,
            created_at=category_model.created_at.isoformat(), # Convert datetime to ISO string
        )
        # Ensure pubsub_name matches your Dapr component name (e.g., kafka-pubsub)
        self.dapr_publisher.publish(
            pubsub_name="kafka-pubsub", # Or "category-pubsub" if that's your component name
            topic_name="category-created", # Topic name for creation events
            data=event.SerializeToString()
        )
        return category_model

    def get_category(self, category_id: str):
        """Retrieve a single category by ID."""
        return self.repo.get_by_id(category_id)

    def list_categories(self, is_active: bool | None = True):
        """Retrieve a list of categories, optionally filtered by active status."""
        return self.repo.list_all(is_active=is_active)

    def update_category(self, category_id: str, name: str | None = None, description: str | None = None):
        """Update a category and publish an update event."""
        # Get the existing category to check existence and get old data if needed for the event
        existing_category_model = self.repo.get_by_id(category_id)
        if not existing_category_model:
            # Consider raising an exception or returning None/False
            raise ValueError(f"Category with ID {category_id} not found.") # Or return None

        # Prepare updates dictionary, only include non-None values
        updates = {}
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description

        # Perform the update in the repository
        updated_category_model = self.repo.update(category_id, **updates)
        if updated_category_model:
            # Publish the update event
            event = CategoryUpdated(
                category_id=updated_category_model.id,
                name=updated_category_model.name,
                description=updated_category_model.description or "",
                is_active=updated_category_model.is_active,
                updated_at=updated_category_model.updated_at.isoformat(), # Convert datetime to ISO string
            )
            self.dapr_publisher.publish(
                pubsub_name="kafka-pubsub", # Or "category-pubsub"
                topic_name="category-updated", # Topic name for update events
                data=event.SerializeToString()
            )
        return updated_category_model

    def delete_category(self, category_id: str):
        """Soft delete a category and publish a delete event."""
        # Perform the soft delete in the repository
        deleted_category_model = self.repo.soft_delete(category_id)
        if deleted_category_model:
            # Publish the delete event
            event = CategoryDeleted(
                category_id=deleted_category_model.id,
                name=deleted_category_model.name, # Include name for context in the event
                deleted_at=deleted_category_model.deleted_at.isoformat(), # Convert datetime to ISO string
            )
            self.dapr_publisher.publish(
                pubsub_name="kafka-pubsub", # Or "category-pubsub"
                topic_name="category-deleted", # Topic name for deletion events
                data=event.SerializeToString()
            )
        return deleted_category_model

# --- Example of how this service would be instantiated (typically in your API layer or dependency injection setup) ---
# category_repo_instance = CategoryRepository(session=some_sqlmodel_session)
# dapr_publisher_instance = DaprClient() # Or however you initialize it
# category_service = CategoryService(repo=category_repo_instance, dapr_publisher=dapr_publisher_instance)