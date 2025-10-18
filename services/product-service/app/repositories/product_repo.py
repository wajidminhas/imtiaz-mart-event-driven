# services/product-service/app/repositories/product_repo.py

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session
from app.models.product import ProductModel
from app.domain.product import Product


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, product: Product) -> ProductModel:
        now = datetime.now(timezone.utc)
        product_model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            brand=product.brand,
            tags=",".join(product.tags) if product.tags else "",
            image_url=product.image_url,
            is_active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        self.session.add(product_model)
        self.session.commit()
        self.session.refresh(product_model)
        return product_model

    def get_by_id(self, product_id: str) -> Optional[ProductModel]:
        return self.session.get(ProductModel, product_id)

    def update(self, product_id: str, **updates) -> Optional[ProductModel]:
        product = self.get_by_id(product_id)
        if not product or product.deleted_at is not None:
            return None

        for key, value in updates.items():
            if hasattr(product, key) and key not in ["id", "created_at"]:
                setattr(product, key, value)

        product.updated_at = datetime.now(timezone.utc)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def soft_delete(self, product_id: str) -> Optional[ProductModel]:
        product = self.get_by_id(product_id)
        if not product or product.deleted_at is not None:
            return None

        now = datetime.now(timezone.utc)
        product.deleted_at = now
        product.is_active = False
        product.updated_at = now
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product