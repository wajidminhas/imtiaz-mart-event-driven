from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4
from datetime import datetime, timezone
from .category import CategoryModel

class ProductModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: str
    price: float
    category_id: str = Field(foreign_key="categorymodel.id") # Links to CategoryModel's id
    category: CategoryModel = Relationship(back_populates="products") # Uncomment if needed
    brand: Optional[str] = "" # Made optional
    tags: Optional[str] = ""  # Made optional, store as JSON string or use ARRAY if PostgreSQL
    image_url: Optional[str] = "" # Made optional
    weight_grams: Optional[int] = None # Uncommented and made optional
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # 🔹 Soft delete (recommended over hard delete in event-driven systems)
    deleted_at: Optional[datetime] = None