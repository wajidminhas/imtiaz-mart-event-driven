# tests/unit/test_domain_category.py

import pytest
from app.domain.category import Category

def test_category_creation_with_valid_data():
    """
    Test that a Category object can be created successfully
    with a valid name and an optional description.
    """
    # Given: Valid inputs for a category
    name = "Electronics"
    description = "Devices and gadgets"

    # When: Creating a Category instance
    category = Category(name=name, description=description)

    # Then: The object should be created with the correct attributes
    assert category.name == name
    assert category.description == description
    # Note: We don't explicitly set is_active in the domain model,
    # it might be handled by the service/repo layer or the SQLModel default.

def test_category_rejects_empty_name():
    """
    Test that creating a Category with an empty name raises a ValueError.
    """
    # Given: An empty name
    name = ""

    # When/Then: Creating a Category should raise ValueError
    with pytest.raises(ValueError, match="Category name cannot be empty or just whitespace."):
        Category(name=name)

def test_category_rejects_whitespace_only_name():
    """
    Test that creating a Category with a name containing only whitespace raises a ValueError.
    """
    # Given: A name with only whitespace
    name = "   "

    # When/Then: Creating a Category should raise ValueError
    with pytest.raises(ValueError, match="Category name cannot be empty or just whitespace."):
        Category(name=name)

# Example of a potential update test (if your Category domain model has an update method)
# def test_category_update():
#     """
#     Test updating the name and description of a Category.
#     """
#     # Given: An existing Category
#     initial_name = "Old Category"
#     initial_description = "This is the old description"
#     category = Category(name=initial_name, description=initial_description)
#
#     # When: Updating its attributes
#     new_name = "New Category"
#     new_description = "This is the new description"
#     category.update(name=new_name, description=new_description)
#
#     # Then: The attributes should be updated correctly
#     assert category.name == new_name
#     assert category.description == new_description
#
# def test_category_update_name_rejects_empty():
#     """
#     Test that updating a Category's name with an empty string raises a ValueError.
#     """
#     # Given: An existing Category
#     category = Category(name="Valid Name", description="Valid Description")
#
#     # When/Then: Updating the name to an empty string should raise ValueError
#     with pytest.raises(ValueError, match="Category name cannot be empty or just whitespace."):
#         category.update(name="")