from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel import Session
from typing import List
from app.models.payment import (
    PaymentCreate, 
    PaymentUpdate, 
    PaymentRead, 
    PaymentStatus,
    PaymentMethod
)
from app.services.payment_service import PaymentService
from app.repositories.payment_repository import PaymentRepository
from app.database import get_payment_session


# Create router with prefix and tags
router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


def get_payment_service(
    session: Session = Depends(get_payment_session)
) -> PaymentService:
    """
    Dependency Injection: Creates service with repository
    
    Flow:
    1. FastAPI injects DB session
    2. Create repository with session
    3. Create service with repository
    4. Return service to route handler
    """
    repository = PaymentRepository(session)
    return PaymentService(repository)


@router.post(
    "/",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new payment",
    description="Initiate a new payment for an order"
)
def create_payment(
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service)
):
    """
    Create a new payment
    
    - **order_id**: ID of the order being paid
    - **user_id**: ID of the user making payment
    - **amount**: Payment amount (must be positive)
    - **currency**: Currency code (default: PKR)
    - **payment_method**: Payment method (payfast, stripe, card, bank_transfer)
    - **payment_provider**: Payment gateway provider name
    """
    return service.create_payment(payment)


@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
    summary="Get payment by ID",
    description="Retrieve payment details by payment ID"
)
def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """Get payment by ID"""
    return service.get_payment(payment_id)


@router.get(
    "/order/{order_id}",
    response_model=PaymentRead,
    summary="Get payment by order ID",
    description="Retrieve payment details by order ID"
)
def get_payment_by_order(
    order_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """Get payment associated with an order"""
    return service.get_payment_by_order(order_id)


@router.get(
    "/user/{user_id}",
    response_model=List[PaymentRead],
    summary="Get user's payments",
    description="Retrieve all payments for a specific user"
)
def get_user_payments(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    service: PaymentService = Depends(get_payment_service)
):
    """Get all payments for a user"""
    return service.get_user_payments(user_id, skip, limit)


@router.get(
    "/status/{status}",
    response_model=List[PaymentRead],
    summary="Get payments by status",
    description="Retrieve all payments with a specific status"
)
def get_payments_by_status(
    status: PaymentStatus,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    service: PaymentService = Depends(get_payment_service)
):
    """Get payments filtered by status"""
    return service.get_payments_by_status(status, skip, limit)


@router.post(
    "/{payment_id}/complete",
    response_model=PaymentRead,
    summary="Complete payment",
    description="Mark a payment as completed after successful processing"
)
def complete_payment(
    payment_id: int,
    provider_transaction_id: str = Query(..., description="Transaction ID from payment gateway"),
    service: PaymentService = Depends(get_payment_service)
):
    """
    Complete a payment
    
    This endpoint is typically called by payment gateway webhooks
    or after receiving confirmation from the payment provider
    """
    return service.complete_payment(payment_id, provider_transaction_id)


@router.post(
    "/{payment_id}/fail",
    response_model=PaymentRead,
    summary="Mark payment as failed",
    description="Mark a payment as failed with reason"
)
def fail_payment(
    payment_id: int,
    failure_reason: str = Query(..., description="Reason for payment failure"),
    failure_code: str = Query(None, description="Error code from payment gateway"),
    service: PaymentService = Depends(get_payment_service)
):
    """
    Mark payment as failed
    
    This endpoint is called when payment processing fails
    """
    return service.fail_payment(payment_id, failure_reason, failure_code)


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentRead,
    summary="Refund payment",
    description="Process a full or partial refund for a completed payment"
)
def refund_payment(
    payment_id: int,
    refund_amount: float = Query(None, gt=0, description="Amount to refund (None for full refund)"),
    refund_reason: str = Query(None, description="Reason for refund"),
    service: PaymentService = Depends(get_payment_service)
):
    """
    Refund a payment
    
    - If refund_amount is None, full refund is processed
    - If refund_amount is specified, partial refund is processed
    """
    return service.refund_payment(payment_id, refund_amount, refund_reason)


@router.get(
    "/",
    response_model=List[PaymentRead],
    summary="List all payments",
    description="Get paginated list of all payments (admin endpoint)"
)
def list_payments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    service: PaymentService = Depends(get_payment_service)
):
    """
    List all payments (admin endpoint)
    
    This should be protected with admin authentication in production
    """
    # For now, we'll list pending payments as an example
    # In production, you'd want proper admin authentication
    return service.get_payments_by_status(PaymentStatus.PENDING, skip, limit)
