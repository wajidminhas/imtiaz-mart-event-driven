import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import Optional

# Add shared proto path
shared_proto_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "proto"
sys.path.insert(0, str(shared_proto_path))

# Import the generated protobuf class
from payment_completed_pb2 import PaymentCompleted

# Dapr configuration
DAPR_HTTP_PORT = 3502  # Payment service Dapr port
PUBSUB_NAME = "imtiaz-pubsub"
TOPIC_NAME = "payment.completed"


class EventPublisher:
    """Centralized event publisher for payment service"""
    
    def __init__(self, dapr_port: int = DAPR_HTTP_PORT):
        self.dapr_port = dapr_port
        self.pubsub_name = PUBSUB_NAME
    
    def publish_payment_completed(
        self, 
        payment_id: int, 
        order_id: int, 
        amount: float, 
        payment_method: str,
        status: str
    ):
        """Publish payment completed event"""
        if payment_id is None:
            print("⚠️ Skipping publish: payment_id is None")
            return False
        
        try:
            event = PaymentCompleted()
            
            # Set fields (convert types to match protobuf)
            event.payment_id = str(payment_id)
            event.order_id = str(order_id)
            event.amount = float(amount)
            event.payment_method = str(payment_method)
            event.status = str(status)
            event.timestamp = int(datetime.utcnow().timestamp() * 1000)
            
            # Serialize to bytes
            event_data = event.SerializeToString()
            
            # Publish via Dapr
            dapr_url = f"http://localhost:{self.dapr_port}/v1.0/publish/{self.pubsub_name}/{TOPIC_NAME}"
            
            response = requests.post(
                dapr_url,
                data=event_data,
                headers={"Content-Type": "application/octet-stream"},
                timeout=5
            )
            response.raise_for_status()
            
            print(f"✅ Published event: {TOPIC_NAME} for payment_id={payment_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish event: {e}")
            import traceback
            traceback.print_exc()
            return False


# Global instance
event_publisher = EventPublisher()
