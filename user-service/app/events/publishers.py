# user-service/app/events/publisher.py
import requests
import time
from ...user_registered_pb2 import UserRegistered
def publish_user_registered(user_id: str, email: str, full_name: str):
    """Publish UserRegistered event to Kafka via Dapr."""
    event = UserRegistered(
        user_id=user_id,
        email=email,
        full_name=full_name,
        created_at=int(time.time())
    )
    response = requests.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/user-registered",
        data=event.SerializeToString(),
        headers={"Content-Type": "application/octet-stream"}
    )
    response.raise_for_status()