"""
Event Publishers for User Service
Publishes events to Kafka via Dapr
"""

import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add shared proto folder to Python path
shared_proto_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "proto"
sys.path.insert(0, str(shared_proto_path))

# Import the generated protobuf class
from user_registered_pb2 import UserRegistered

# Dapr configuration
DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "order-pubsub"
TOPIC_NAME = "user.registered"


class EventPublisher:
    """Centralized event publisher for user service"""
    
    def __init__(self, dapr_port: int = DAPR_HTTP_PORT):
        self.dapr_port = dapr_port
        self.pubsub_name = PUBSUB_NAME
    
    def publish_user_registered(self, user_id: Optional[int] , email: str, first_name: str, last_name: str):
        """Publish user registered event"""
        if user_id is None:
            print("⚠️ Skipping publish: user_id is None")
            return False
        event = UserRegistered()
        event.user_id = user_id
        event.email = email
        event.first_name = first_name
        event.last_name = last_name
        event.timestamp = int(datetime.now().timestamp())
        
        # Serialize to bytes
        event_data = event.SerializeToString()
        
        # Publish via Dapr
        dapr_url = f"http://localhost:{self.dapr_port}/v1.0/publish/{self.pubsub_name}/{TOPIC_NAME}"
        
        try:
            response = requests.post(
                dapr_url,
                data=event_data,
                headers={"Content-Type": "application/octet-stream"},
                timeout=5
            )
            response.raise_for_status()
            
            print(f"✅ Published event: user.registered for user_id={user_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to publish event: {e}")
            return False


# Create singleton instance
event_publisher = EventPublisher()