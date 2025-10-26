# services/product-service/app/models/product_model.py (or product.py)

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    # Import CategoryModel for type checking only
    from .category import CategoryModel # Adjust path if file is named category.py

class ProductModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: str
    price: float
    category_id: str = Field(foreign_key="categorymodel.id") # Links to CategoryModel's table
    # Use string annotation for the relationship
    category: "CategoryModel" = Relationship(back_populates="products")
    brand: Optional[str] = ""
    tags: Optional[str] = ""
    image_url: Optional[str] = ""
    weight_grams: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None