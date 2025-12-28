from typing import List, Optional
from app.models.payment import Payment, PaymentCreate, PaymentUpdate, PaymentStatus
from app.repositories.payment_repository import PaymentRepository
from fastapi import HTTPException, status
from app.events.publisher import (
    publish_payment_initiated,
    publish_payment_completed,
    publish_payment_failed,
    publish_payment_refunded
)
from datetime import datetime


class PaymentService:
    """
    Payment Service: Business Logic Layer
    
    Responsibilities:
    - Business rules and validation
    - Orchestrate repository calls
    - Publish events to Kafka
    - Handle errors and exceptions
    """
    
    def __init__(self, repository: PaymentRepository):
        """
        Dependency Injection: Repository injected from route
        """
        self.repository = repository
    
    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """
        Create a new payment and publish event
        
        Args:
            payment_data: Payment creation data
            
        Returns:
            Created Payment object
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Create payment in database
            payment = self.repository.create(payment_data)
            
            # Prepare event data
            event_data = {
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "user_id": payment.user_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method.value,
                "payment_provider": payment.payment_provider,
                "status": payment.status.value,
                "created_at": payment.created_at.isoformat()
            }
            
            # Publish event
            publish_payment_initiated(event_data)
            
            return payment
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create payment: {str(e)}"
            )
    
    def get_payment(self, payment_id: int) -> Payment:
        """
        Get payment by ID
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment object
            
        Raises:
            HTTPException: If payment not found
        """
        payment = self.repository.get_by_id(payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found"
            )
        
        return payment
    
    def get_user_payments(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """
        Get all payments for a user
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of Payment objects
        """
        return self.repository.get_by_user_id(user_id, skip, limit)
    
    def get_payment_by_order(self, order_id: int) -> Payment:
        """
        Get payment by order ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Payment object
            
        Raises:
            HTTPException: If payment not found
        """
        payment = self.repository.get_by_order_id(order_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment for order {order_id} not found"
            )
        
        return payment
    
    def complete_payment(
        self,
        payment_id: int,
        provider_transaction_id: str
    ) -> Payment:
        """
        Mark payment as completed
        
        Args:
            payment_id: Payment ID
            provider_transaction_id: Transaction ID from payment gateway
            
        Returns:
            Updated Payment object
            
        Raises:
            HTTPException: If payment not found or update fails
        """
        # Get payment
        payment = self.get_payment(payment_id)
        
        # Business rule: Can only complete pending or processing payments
        if payment.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete payment with status {payment.status}"
            )
        
        # Update payment status
        updated_payment = self.repository.update_status(
            payment_id=payment_id,
            status=PaymentStatus.COMPLETED,
            provider_transaction_id=provider_transaction_id
        )
        
        # Prepare event data
        event_data = {
            "payment_id": updated_payment.id,
            "order_id": updated_payment.order_id,
            "user_id": updated_payment.user_id,
            "amount": updated_payment.amount,
            "currency": updated_payment.currency,
            "payment_method": updated_payment.payment_method.value,
            "provider_transaction_id": provider_transaction_id,
            "status": PaymentStatus.COMPLETED.value,
            "completed_at": updated_payment.completed_at.isoformat()
        }
        
        # Publish event
        publish_payment_completed(event_data)
        
        return updated_payment
    
    def fail_payment(
        self,
        payment_id: int,
        failure_reason: str,
        failure_code: Optional[str] = None
    ) -> Payment:
        """
        Mark payment as failed
        
        Args:
            payment_id: Payment ID
            failure_reason: Reason for failure
            failure_code: Error code from payment gateway
            
        Returns:
            Updated Payment object
            
        Raises:
            HTTPException: If payment not found or update fails
        """
        # Get payment
        payment = self.get_payment(payment_id)
        
        # Update payment status
        updated_payment = self.repository.update_status(
            payment_id=payment_id,
            status=PaymentStatus.FAILED,
            failure_reason=failure_reason,
            failure_code=failure_code
        )
        
        # Prepare event data
        event_data = {
            "payment_id": updated_payment.id,
            "order_id": updated_payment.order_id,
            "user_id": updated_payment.user_id,
            "amount": updated_payment.amount,
            "currency": updated_payment.currency,
            "payment_method": updated_payment.payment_method.value,
            "status": PaymentStatus.FAILED.value,
            "failure_reason": failure_reason,
            "failure_code": failure_code
        }
        
        # Publish event
        publish_payment_failed(event_data)
        
        return updated_payment
    
    def refund_payment(
        self,
        payment_id: int,
        refund_amount: Optional[float] = None,
        refund_reason: Optional[str] = None
    ) -> Payment:
        """
        Process payment refund
        
        Args:
            payment_id: Payment ID
            refund_amount: Amount to refund (None = full refund)
            refund_reason: Reason for refund
            
        Returns:
            Updated Payment object
            
        Raises:
            HTTPException: If payment not found or refund invalid
        """
        # Get payment
        payment = self.get_payment(payment_id)
        
        # Business rule: Can only refund completed payments
        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only refund completed payments"
            )
        
        # Calculate refund amount
        if refund_amount is None:
            refund_amount = payment.amount
        
        # Validate refund amount
        total_refunded = payment.refunded_amount + refund_amount
        if total_refunded > payment.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund amount exceeds payment amount"
            )
        
        # Determine new status
        if total_refunded == payment.amount:
            new_status = PaymentStatus.REFUNDED
        else:
            new_status = PaymentStatus.PARTIALLY_REFUNDED
        
        # Update payment
        payment_update = PaymentUpdate(
            status=new_status,
            refunded_amount=total_refunded
        )
        
        updated_payment = self.repository.update(payment_id, payment_update)
        
        # Prepare event data
        event_data = {
            "payment_id": updated_payment.id,
            "order_id": updated_payment.order_id,
            "user_id": updated_payment.user_id,
            "original_amount": updated_payment.amount,
            "refund_amount": refund_amount,
            "total_refunded": total_refunded,
            "status": new_status.value,
            "refund_reason": refund_reason
        }
        
        # Publish event
        publish_payment_refunded(event_data)
        
        return updated_payment
    
    def get_payments_by_status(
        self,
        status: PaymentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Get all payments with specific status
        
        Args:
            status: Payment status to filter by
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of Payment objects
        """
        return self.repository.get_by_status(status, skip, limit)
