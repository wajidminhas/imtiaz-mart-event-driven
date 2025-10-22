

# app/repositories/category_repo.py
from sqlmodel import Session, select
from app.models.category import CategoryModel
from app.domain.category import Category # If needed for validation or conversion
from datetime import datetime, timezone

class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, category: Category) -> CategoryModel:
        # Convert domain Category to DB CategoryModel
        category_model = CategoryModel(name=category.name, description=category.description)
        self.session.add(category_model)
        self.session.commit()
        self.session.refresh(category_model)
        return category_model

    def get_by_id(self, category_id: str) -> CategoryModel | None:
        return self.session.get(CategoryModel, category_id)

    def get_by_name(self, name: str) -> CategoryModel | None:
        statement = select(CategoryModel).where(CategoryModel.name == name)
        return self.session.exec(statement).first()

    def list_all(self, is_active: bool | None = True) -> list[CategoryModel]:
        statement = select(CategoryModel)
        if is_active is not None:
            statement = statement.where(CategoryModel.is_active == is_active)
        return self.session.exec(statement).all()

    def update(self, category_id: str, **updates) -> CategoryModel | None:
        category = self.get_by_id(category_id)
        if not category:
            return None
        for key, value in updates.items():
            if hasattr(category, key):
                setattr(category, key, value)
        category.updated_at = datetime.now(timezone.utc) # Update timestamp
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def soft_delete(self, category_id: str) -> CategoryModel | None:
        category = self.get_by_id(category_id)
        if not category:
            return None
        category.is_active = False
        category.deleted_at = datetime.now(timezone.utc)
        category.updated_at = datetime.now(timezone.utc)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
