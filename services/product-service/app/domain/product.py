

class Product:
    def __init__(
        self,
        name: str,
        description: str,          # ← For NLP / embeddings
        price: float,
        category: str,             # ← e.g., "Grocery > Dairy > Milk"
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
        self.category = category
        self.brand = brand
        self.tags = tags or []
        self.image_url = image_url
        self.weight_grams = weight_grams
        self.is_active = is_active