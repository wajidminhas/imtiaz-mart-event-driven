# services/product-service/app/models/category_model.py (or category.py)

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid as uuid4
from datetime import datetime, timezone

if TYPE_CHECKING:
    # Import ProductModel for type checking only
    from .product import ProductModel # Adjust path if file is named product.py

class CategoryModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    # Use string annotation for the relationship
    products: list["ProductModel"] = Relationship(back_populates="category")