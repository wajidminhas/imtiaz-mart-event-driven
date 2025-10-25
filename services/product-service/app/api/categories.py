
# app/api/categories.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.category_service import CategoryService
from app.repositories.category_repo import CategoryRepository
from app.database import get_session
from dapr.clients import DaprClient
from datetime import datetime # For formatting datetime in responses if needed

router = APIRouter(prefix="/categories", tags=["categories"])

def get_dapr_client():
    # Ensure this matches how you initialize the Dapr client in your environment
    # (e.g., locally with dapr run, or in ACA)
    return DaprClient()

def get_category_service(session=Depends(get_session), dapr_client=Depends(get_dapr_client)) -> CategoryService:
    """Dependency to get CategoryService instance with required dependencies."""
    repo = CategoryRepository(session)
    return CategoryService(repo=repo, dapr_publisher=dapr_client)

# --- Category Endpoints ---

@router.post("/", status_code=201)
def create_category(
    name: str,
    description: str = None,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Create a new category.
    """
    try:
        category = category_service.create_category(name=name, description=description)
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Consider catching other potential exceptions from the service/db layer if needed

@router.get("/{category_id}", status_code=200)
def get_category(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Retrieve a single category by its ID.
    """
    category = category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "is_active": category.is_active,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }

@router.get("/", status_code=200)
def list_categories(
    is_active: bool = True, # Default to showing only active categories
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Retrieve a list of categories, optionally filtered by active status.
    """
    categories = category_service.list_categories(is_active=is_active)
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "is_active": cat.is_active,
            "created_at": cat.created_at.isoformat() if cat.created_at else None,
            "updated_at": cat.updated_at.isoformat() if cat.updated_at else None,
        }
        for cat in categories
    ]

@router.put("/{category_id}", status_code=200)
def update_category(
    category_id: str,
    name: str = None,
    description: str = None,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Update an existing category.
    """
    try:
        updated_category = category_service.update_category(category_id=category_id, name=name, description=description)
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return {
            "id": updated_category.id,
            "name": updated_category.name,
            "description": updated_category.description,
            "is_active": updated_category.is_active,
            "updated_at": updated_category.updated_at.isoformat() if updated_category.updated_at else None,
        }
    except ValueError as e: # Catch validation errors from the service
        raise HTTPException(status_code=400, detail=str(e))
    # Consider catching other potential exceptions from the service/db layer if needed

@router.delete("/{category_id}", status_code=204) # 204 No Content is standard for successful deletes
def delete_category(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Delete (soft delete) a category.
    """
    deleted_category = category_service.delete_category(category_id=category_id)
    if not deleted_category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Return 204 No Content on successful deletion
    return
