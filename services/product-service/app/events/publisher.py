"""
Event Publisher using Dapr Pub/Sub

Publishes events to Kafka via Dapr sidecar
Dapr handles: connection, retries, error handling
"""

import json
from typing import Any
from app.config import settings
from urllib.request import Request, urlopen
from urllib.error import URLError


class EventPublisher:
    """
    Event Publisher - Publishes events to Kafka via Dapr

    Pattern: Singleton (one instance for entire service)
    """

    def __init__(self):
        """Initialize Dapr endpoint"""
        self.pubsub_name = settings.pubsub_name  # "imtiaz-pubsub" from .env
        # Dapr sidecar HTTP endpoint (default port for Dapr HTTP API)
        self.dapr_http_endpoint = f"http://localhost:3501"  # Dapr default HTTP port

    def publish_event(
        self,
        topic: str,
        event_data: Any,
        use_protobuf: bool = False
    ) -> bool:
        """
        Publish event to Kafka via Dapr using HTTP API

        Args:
            topic: Kafka topic name (e.g., "product.created")
            event_data: Event data (dict or Protobuf message)
            use_protobuf: If True, event_data is Protobuf message

        Returns:
            True if published successfully, False otherwise

        Example:
            publisher.publish_event(
                topic="product.created",
                event_data={"product_id": 1, "name": "Laptop"}
            )
        """
        try:
            # Convert to JSON string
            event_json = json.dumps(event_data)

            # Create the request URL to Dapr sidecar HTTP endpoint
            url = f"{self.dapr_http_endpoint}/v1.0/publish/{self.pubsub_name}/{topic}"

            # Create the HTTP request
            req = Request(
                url=url,
                data=event_json.encode('utf-8'),
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            # Make HTTP POST request to Dapr sidecar
            with urlopen(req) as response:
                if response.status == 200:
                    print(f"✅ Published event to topic: {topic}")
                    print(f"   Data: {event_data}")
                    return True
                else:
                    print(f"❌ Failed to publish event to {topic}: HTTP {response.status}")
                    return False

        except URLError as e:
            print(f"❌ Failed to publish event to {topic}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Failed to publish event to {topic}: {str(e)}")
            return False


# Singleton instance
event_publisher = EventPublisher()


# Helper functions for specific events
def publish_product_created(product_data: dict) -> bool:
    """
    Publish Product Created Event

    Topic: product.created
    Consumers: Inventory Service, Order Service
    """
    return event_publisher.publish_event(
        topic="product.created",
        event_data=product_data
    )


def publish_product_updated(product_data: dict) -> bool:
    """
    Publish Product Updated Event

    Topic: product.updated
    Consumers: Inventory Service, Order Service
    """
    return event_publisher.publish_event(
        topic="product.updated",
        event_data=product_data
    )


def publish_product_deleted(product_id: int, product_name: str) -> bool:
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

    return event_publisher.publish_event(
        topic="product.deleted",
        event_data=event_data
    )