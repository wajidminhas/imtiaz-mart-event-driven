

"""
Event Publisher using Dapr Pub/Sub

Publishes inventory events to Kafka via Dapr sidecar
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
        # Dapr sidecar HTTP endpoint (port 3504 for inventory-service)
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
            topic: Kafka topic name (e.g., "inventory.low-stock")
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
                        print(f"   Product: {event_data.get('product_name', 'N/A')}")
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

def publish_inventory_low_stock(stock_data: dict) -> bool:
    """
    Publish Inventory Low Stock Event
    
    Topic: inventory.low-stock
    Consumers: Notification Service (alert admin), Product Service (mark as low stock)
    
    Event Data:
    - product_id: int
    - product_name: str
    - current_quantity: int
    - threshold: int
    - timestamp: str
    """
    return event_publisher.publish_event(
        topic="inventory.low-stock",
        event_data=stock_data
    )


def publish_inventory_out_of_stock(stock_data: dict) -> bool:
    """
    Publish Inventory Out of Stock Event
    
    Topic: inventory.out-of-stock
    Consumers: Notification Service (alert admin), Product Service (mark as unavailable)
    
    Event Data:
    - product_id: int
    - product_name: str
    - timestamp: str
    """
    return event_publisher.publish_event(
        topic="inventory.out-of-stock",
        event_data=stock_data
    )


def publish_inventory_restocked(stock_data: dict) -> bool:
    """
    Publish Inventory Restocked Event
    
    Topic: inventory.restocked
    Consumers: Notification Service, Product Service (mark as available)
    
    Event Data:
    - product_id: int
    - product_name: str
    - new_quantity: int
    - restocked_at: str
    """
    return event_publisher.publish_event(
        topic="inventory.restocked",
        event_data=stock_data
    )


def publish_inventory_updated(inventory_data: dict) -> bool:
    """
    Publish Inventory Updated Event
    
    Topic: inventory.updated
    Consumers: Analytics Service
    
    Event Data:
    - product_id: int
    - product_name: str
    - old_quantity: int
    - new_quantity: int
    - updated_at: str
    """
    return event_publisher.publish_event(
        topic="inventory.updated",
        event_data=inventory_data
    )