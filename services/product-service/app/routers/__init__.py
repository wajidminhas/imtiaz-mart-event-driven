

from .product_router import router as product_router

__all__ = ["product_router"]
"""
```



## **What You Learned:** 📚

### **FastAPI Concepts:**
✅ **APIRouter** - Modular route organization  
✅ **Depends()** - Dependency Injection magic  
✅ **response_model** - Auto validation & documentation  
✅ **status_code** - Proper HTTP status codes  
✅ **Query()** - Query parameter validation  

### **Dependency Injection Chain:**


get_product_session() 
    → Creates DB Session
    → Passed to ProductRepository
    → Passed to ProductService
    → Used in route handler
    
    """