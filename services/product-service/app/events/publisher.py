"""
Event Publisher using Dapr Pub/Sub

Publishes events to Kafka via Dapr sidecar
Dapr handles: connection, retries, error handling
"""

import json
from typing import Any
from app.config import settings
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import time


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

    import time
from urllib.error import URLError, HTTPError

def publish_event(self, topic: str, event_data: Any, use_protobuf: bool = False) -> bool:
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            event_json = json.dumps(event_data)
            url = f"{self.dapr_http_endpoint}/v1.0/publish/{self.pubsub_name}/{topic}"
            
            req = Request(
                url=url,
                data=event_json.encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urlopen(req, timeout=5) as response:
                if response.status in (200, 204):
                    print(f"✅ Published event to topic: {topic}")
                    return True
                else:
                    print(f"❌ Failed: HTTP {response.status}")
                    return False
                    
        except URLError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Retry {attempt + 1}/{max_retries} for {topic}: {e.reason}")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed after {max_retries} attempts: {e.reason}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
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