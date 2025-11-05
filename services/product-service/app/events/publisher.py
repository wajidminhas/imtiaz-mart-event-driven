

"""
Event Publisher using Dapr Pub/Sub

Publishes events to Kafka via Dapr sidecar
Dapr handles: connection, retries, error handling
"""

from dapr.clients import DaprClient
from google.protobuf.json_format import MessageToDict
import json
from typing import Any
from app.config import settings


class EventPublisher:
    """
    Event Publisher - Publishes events to Kafka via Dapr
    
    Pattern: Singleton (one instance for entire service)
    """
    
    def __init__(self):
        """Initialize Dapr client"""
        self.pubsub_name = settings.pubsub_name  # "imtiaz-pubsub" from .env
        self.dapr_client = None
    
    def _get_client(self) -> DaprClient:
        """
        Get or create Dapr client (lazy initialization)
        
        Why lazy? 
        - Don't create connection until needed
        - Avoid connection errors during testing
        """
        if self.dapr_client is None:
            self.dapr_client = DaprClient()
        return self.dapr_client
    
    async def publish_event(
        self, 
        topic: str, 
        event_data: Any,
        use_protobuf: bool = False
    ) -> bool:
        """
        Publish event to Kafka via Dapr
        
        Args:
            topic: Kafka topic name (e.g., "product.created")
            event_data: Event data (dict or Protobuf message)
            use_protobuf: If True, event_data is Protobuf message
        
        Returns:
            True if published successfully, False otherwise
        
        Example:
            await publisher.publish_event(
                topic="product.created",
                event_data={"product_id": 1, "name": "Laptop"}
            )
        """
        try:
            client = self._get_client()
            
            # Convert Protobuf to dict if needed
            if use_protobuf:
                event_dict = MessageToDict(event_data)
            else:
                event_dict = event_data
            
            # Convert to JSON string
            event_json = json.dumps(event_dict)
            
            # Publish to Dapr
            # Dapr will forward to Kafka
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=event_json,
                data_content_type="application/json"
            )
            
            print(f"✅ Published event to topic: {topic}")
            print(f"   Data: {event_dict}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish event to {topic}: {str(e)}")
            return False
    
    def close(self):
        """Close Dapr client connection"""
        if self.dapr_client:
            self.dapr_client.close()
            self.dapr_client = None


# Singleton instance
event_publisher = EventPublisher()


# Helper functions for specific events
async def publish_product_created(product_data: dict) -> bool:
    """
    Publish Product Created Event
    
    Topic: product.created
    Consumers: Inventory Service, Order Service
    """
    return await event_publisher.publish_event(
        topic="product.created",
        event_data=product_data
    )


async def publish_product_updated(product_data: dict) -> bool:
    """
    Publish Product Updated Event
    
    Topic: product.updated
    Consumers: Inventory Service, Order Service
    """
    return await event_publisher.publish_event(
        topic="product.updated",
        event_data=product_data
    )


async def publish_product_deleted(product_id: int, product_name: str) -> bool:
    """
    Publish Product Deleted Event
    
    Topic: product.deleted
    Consumers: Inventory Service, Order Service
    """
    event_data = {
        "product_id": product_id,
        "name": product_name,
        "deleted_at": None  # Will add timestamp in service
    }
    
    return await event_publisher.publish_event(
        topic="product.deleted",
        event_data=event_data
    )