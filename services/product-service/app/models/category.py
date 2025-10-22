

# Using SQLModel (like your ProductModel)
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from datetime import datetime, timezone
from .product import ProductModel

class CategoryModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True}) # e.g., "Dairy", "Bakery" - Should be unique
    description: Optional[str] = None # e.g., "Fresh milk, eggs, cheese"
    # parent_id: Optional[str] = Field(default=None, foreign_key="categorymodel.id") # For subcategories (e.g., Dairy -> Milk -> Cow's Milk)
    is_active: bool = True # To enable/disable categories without deleting

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None # If soft-deleted
    products: list["ProductModel"] = Relationship(back_populates="category") # Links back to ProductModel