from .publishers import (
    event_publisher,
    publish_inventory_low_stock,
    publish_inventory_out_of_stock,
    publish_inventory_restocked,
    publish_inventory_updated
)

# Import router directly, not the module
from .consumers import router as event_consumer_router

__all__ = [
    "event_publisher",
    "publish_inventory_low_stock",
    "publish_inventory_out_of_stock",
    "publish_inventory_restocked",
    "publish_inventory_updated",
    "event_consumer_router"
]
