# services/product-service/app/domain/category.py

from typing import Optional

class Category:
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = self._validate_name(name)
        self.description = description
        # is_active can be handled by the service/repo layer if needed, or set here with a default
        # self.is_active = True

    def _validate_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty or just whitespace.")
        return name.strip()

    def update(self, name: Optional[str] = None, description: Optional[str] = None):
        """Update category attributes with validation."""
        if name is not None:
            self.name = self._validate_name(name)
        if description is not None:
            self.description = description

# Example usage (for testing or reference):
# try:
#     cat = Category(name="  Dairy  ", description="Milk, Eggs, Cheese")
#     print(f"Created category: {cat.name}, {cat.description}")
#     cat.update(name="Dairy Products", description="Fresh dairy items")
#     print(f"Updated category: {cat.name}, {cat.description}")
# except ValueError as e:
#     print(f"Validation error: {e}")