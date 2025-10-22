

# app/domain/category.py
from typing import Optional

class Category:
    def __init__(self, name: str, description: Optional[str] = None):
        if not name.strip():
            raise ValueError("Category name cannot be empty")
        self.name = name.strip()
        self.description = description
        # is_active could be set here if needed, default True

    def update(self, name: Optional[str] = None, description: Optional[str] = None):
        # Validation for updates
        if name is not None:
            if not name.strip():
                raise ValueError("Category name cannot be empty")
            self.name = name.strip()
        if description is not None:
            self.description = description