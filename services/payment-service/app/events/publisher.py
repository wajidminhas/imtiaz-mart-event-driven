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
        self.pubsub_name = settings.pubsub_name  # ✅ Use from config instead of hardcoding
        self.dapr_http_endpoint = f"http://localhost:{settings.dapr_http_port}"
    
    def publish_event(
        self, 
        topic: str, 
        event_data: Any, 
        use_protobuf: bool = False
    ) -> bool:
        """
        Publish event to Kafka via Dapr using HTTP API
        """
        max_retries = 3
        retry_delay = 1
        
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
                        print(f"   Data: {event_data}")
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


# Helper functions for payment events
def publish_payment_initiated(payment_data: dict) -> bool:
    """Publish Payment Initiated Event"""
    return event_publisher.publish_event(
        topic="payment.initiated",
        event_data=payment_data
    )


def publish_payment_completed(payment_data: dict) -> bool:
    """Publish Payment Completed Event"""
    return event_publisher.publish_event(
        topic="payment.completed",
        event_data=payment_data
    )


def publish_payment_failed(payment_data: dict) -> bool:
    """Publish Payment Failed Event"""
    return event_publisher.publish_event(
        topic="payment.failed",
        event_data=payment_data
    )


def publish_payment_refunded(payment_data: dict) -> bool:
    """Publish Payment Refunded Event"""
    return event_publisher.publish_event(
        topic="payment.refunded",
        event_data=payment_data
    )
