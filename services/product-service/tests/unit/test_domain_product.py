
from app.domain.product import Product
from app.services.product_service import ProductService
from unittest.mock import Mock



# def test_product_requires_name_and_price():
#     try:
#         Product("", -10, "Grocery")
#         assert False
#     except ValueError:
#         pass

# def test_product_can_have_tags_and_brand():
#     p = Product("Milk", "Fresh cow milk", 25.0, "Dairy", brand="Nestlé", tags=["fresh", "dairy"])
#     assert p.brand == "Nestlé"
#     assert "fresh" in p.tags

def test_product_creation_with_valid_data():
    # Given
    name = "Fresh Milk"
    description = "1L full cream milk"
    price = 25.0
    category = "Dairy"

    # When
    product = Product(name=name, description=description, price=price, category=category)

    # Then
    assert product.name == "Fresh Milk"
    assert product.price == 25.0
    assert product.category == "Dairy"
    assert product.is_active is True

def test_product_rejects_invalid_price():
    # Given
    name = "Bread"
    description = "Whole wheat loaf"
    invalid_price = -10.0
    category = "Bakery"

    # When / Then
    try:
        Product(name=name, description=description, price=invalid_price, category=category)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Price must be greater than zero" in str(e)


def test_create_product_saves_and_emits_event():
    # Given
    mock_repo = Mock()
    mock_repo.save.return_value = Mock(id="prod-123")
    mock_publisher = Mock()
    
    service = ProductService(repo=mock_repo, dapr_publisher=mock_publisher)
    
    # When
    result = service.create_product(
        name="Milk",
        description="1L full cream",
        price=25.0,
        category="Dairy"
    )

    # Then
    mock_repo.save.assert_called_once()
    mock_publisher.publish.assert_called_once()
    assert result.id == "prod-123"
    
