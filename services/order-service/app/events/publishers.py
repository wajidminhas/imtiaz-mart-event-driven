

"""
Event Publisher using Dapr Pub/Sub

Publishes order events to Kafka via Dapr sidecar
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
        # Dapr sidecar HTTP endpoint (port 3503 for order-service)
        self.dapr_http_endpoint = f"http://localhost:{settings.dapr_http_port}"
    
    def publish_event(
        self, 
        topic: str, 
        event_data: Any, 
        use_protobuf: bool = False
    ) -> bool:
        """
        Publish event to Kafka via Dapr using HTTP API
        
        Args:
            topic: Kafka topic name (e.g., "order.created")
            event_data: Event data (dict or Protobuf message)
            use_protobuf: If True, event_data is Protobuf message
        
        Returns:
            True if published successfully, False otherwise
        """
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
                        print(f"   Event: {event_data.get('order_number', 'N/A')}")
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

def publish_order_created(order_data: dict) -> bool:
    """
    Publish Order Created Event
    
    Topic: order.created
    Consumers: Payment Service, Inventory Service, Notification Service
    
    Event Data:
    - order_id: int
    - order_number: str
    - user_id: int
    - total_amount: float
    - status: str
    - items: list of products
    - created_at: str
    """
    return event_publisher.publish_event(
        topic="order.created",
        event_data=order_data
    )


def publish_order_updated(order_data: dict) -> bool:
    """
    Publish Order Updated Event
    
    Topic: order.updated
    Consumers: Notification Service, Analytics Service
    
    Event Data:
    - order_id: int
    - order_number: str
    - user_id: int
    - old_status: str
    - new_status: str
    - updated_at: str
    """
    return event_publisher.publish_event(
        topic="order.updated",
        event_data=order_data
    )


def publish_order_cancelled(order_data: dict) -> bool:
    """
    Publish Order Cancelled Event
    
    Topic: order.cancelled
    Consumers: Payment Service (refund), Inventory Service (release stock), Notification Service
    
    Event Data:
    - order_id: int
    - order_number: str
    - user_id: int
    - total_amount: float
    - cancelled_at: str
    """
    return event_publisher.publish_event(
        topic="order.cancelled",
        event_data=order_data
    )


def publish_order_completed(order_data: dict) -> bool:
    """
    Publish Order Completed Event
    
    Topic: order.completed
    Consumers: Notification Service, Analytics Service
    
    Event Data:
    - order_id: int
    - order_number: str
    - user_id: int
    - total_amount: float
    - completed_at: str
    """
    return event_publisher.publish_event(
        topic="order.completed",
        event_data=order_data
    )