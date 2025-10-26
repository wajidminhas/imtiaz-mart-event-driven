

class Product:
    def __init__(
        self,
        name: str,
        description: str,          # ← For NLP / embeddings
        price: float,
        category: str,             # ← e.g., "Grocery > Dairy > Milk"
        category_id: str = "",     # ← For faster lookup
        brand: str = "",           # ← Critical for recommendations
        tags: list[str] = None,    # ← ["organic", "best-seller", "halal"]
        image_url: str = "",
        weight_grams: int = None,  # ← For logistics + similarity
        is_active: bool = True
    ):
        # Validation
        if not name.strip(): raise ValueError("Name required")
        if price <= 0: raise ValueError("Price must be greater than zero")
        if not category.strip(): raise ValueError("Category required")
        
        self.name = name
        self.description = description
        self.price = price
        self.category_id = self._validate_category_id(category_id) # Validate the ID string
        self.brand = brand
        self.tags = tags or []
        self.image_url = image_url
        self.weight_grams = weight_grams
        self.is_active = is_active
        
    def _validate_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty or just whitespace.")
        return name.strip()

    def _validate_price(self, price: float) -> float:
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        return price

    def _validate_category_id(self, category_id: str) -> str:
        # Add logic to validate the category_id format if necessary
        # For now, just ensure it's not empty
        if not category_id:
            raise ValueError("Category ID cannot be empty.")
        return category_id

# Example usage (for testing or reference):
# try:
#     prod = Product(name="  Valid Name  ", description="A product", price=10.0, category_id="some-uuid")
#     print(f"Created product: {prod.name.strip()}, {prod.price}, {prod.category_id}")
# except ValueError as e:
#     print(f"Validation error: {e}")
