"""
Event Publishers for User Service
Publishes events to Kafka via Dapr
"""

import sys
import requests
from pathlib import Path
from datetime import datetime

# Add shared proto folder to Python path
shared_proto_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "proto"
sys.path.insert(0, str(shared_proto_path))

# Import the generated protobuf class
from user_registered_pb2 import UserRegistered

# Dapr configuration
DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "order-pubsub"
TOPIC_NAME = "user.registered"


def publish_user_registered_event(user_id: int, email: str, first_name: str, last_name: str):
    event = UserRegistered()
    event.user_id = str(user_id)
    event.email = email
    event.first_name = first_name
    event.last_name = last_name
    event.timestamp = int(datetime.utcnow().timestamp())
    # ... rest of publishing code
    
    # Step 2: Serialize to bytes
    event_data = event.SerializeToString()
    
    # Step 3: Publish via Dapr
    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"
    
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