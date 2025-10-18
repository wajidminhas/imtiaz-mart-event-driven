from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import uuid4
from datetime import datetime, timezone

class ProductModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: str
    price: float
    category: str
    brand: str
    tags: str  # Store as JSON string or use ARRAY if PostgreSQL
    image_url: str
    # weight_grams: Optional[int]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # 🔹 Soft delete (recommended over hard delete in event-driven systems)
    deleted_at: Optional[datetime] = None

    # 🔹 Override SQLModel's pre-update hook to auto-update `updated_at`
    # def __setattr__(self, name, value):
    #     if name == "updated_at":
    #         super().__setattr__(name, value)
    #     elif name != "created_at":
    #         # Auto-update timestamp on any field change (except creation)
    #         if hasattr(self, 'updated_at') and name in self.model_fields:
    #             object.__setattr__(self, 'updated_at', datetime.now(timezone.utc))
    #         super().__setattr__(name, value)

# services/product-service/app/models/product.py

