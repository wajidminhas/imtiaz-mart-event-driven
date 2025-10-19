# tests/unit/test_product_service.py

from unittest.mock import Mock
from app.services.product_service import ProductService
from app.domain.product import Product

def test_create_product_saves_to_repo_and_publishes_event():
    # Given
    mock_repo = Mock()
    mock_repo.create.return_value = Mock(
        id="prod-123",
        name="Milk",
        price=25.0,
        category="Dairy"
    )
    mock_publisher = Mock()
    
    service = ProductService(repo=mock_repo, dapr_publisher=mock_publisher)
    
    # When
    result = service.create_product(
        name="Milk",
        description="1L full cream milk",
        price=25.0,
        category="Dairy"
    )
    
    # Then
    assert result.id == "prod-123"
    mock_repo.create.assert_called_once()
    mock_publisher.publish.assert_called_once()