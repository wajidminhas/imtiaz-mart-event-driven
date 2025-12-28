from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime
from app.models.payment import Payment, PaymentCreate, PaymentUpdate, PaymentStatus


class PaymentRepository:
    """
    Payment Repository - handles all database operations for payments
    Follows Repository Pattern for clean separation of concerns
    """
    
    def __init__(self, session: Session):
        """Initialize repository with database session"""
        self.session = session
    
    def create(self, payment_data: PaymentCreate) -> Payment:
        """
        Create a new payment record
        
        Args:
            payment_data: PaymentCreate schema with payment details
            
        Returns:
            Created Payment object with generated ID
        """
        # Convert PaymentCreate to Payment (table model)
        payment = Payment.model_validate(payment_data)
        
        # Add to session and commit
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        
        return payment
    
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Get payment by ID
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment object or None if not found
        """
        statement = select(Payment).where(Payment.id == payment_id)
        return self.session.exec(statement).first()
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
        """
        Get all payments for a specific user
        
        Args:
            user_id: User ID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Payment objects
        """
        statement = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        return list(self.session.exec(statement).all())
    
    def get_by_order_id(self, order_id: int) -> Optional[Payment]:
        """
        Get payment by order ID
        
        Args:
            order_id: Order ID
            
        Returns:
            Payment object or None if not found
        """
        statement = select(Payment).where(Payment.order_id == order_id)
        return self.session.exec(statement).first()
    
    def update_status(
        self, 
        payment_id: int, 
        status: PaymentStatus,
        provider_transaction_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        failure_code: Optional[str] = None
    ) -> Optional[Payment]:
        """
        Update payment status and related fields
        
        Args:
            payment_id: Payment ID
            status: New payment status
            provider_transaction_id: Transaction ID from payment provider
            failure_reason: Reason for failure (if status is FAILED)
            failure_code: Error code from payment provider
            
        Returns:
            Updated Payment object or None if not found
        """
        payment = self.get_by_id(payment_id)
        
        if not payment:
            return None
        
        # Update status
        payment.status = status
        payment.updated_at = datetime.now()
        
        # Update provider transaction ID if provided
        if provider_transaction_id:
            payment.provider_transaction_id = provider_transaction_id
        
        # If completed, set completed_at timestamp
        if status == PaymentStatus.COMPLETED:
            payment.completed_at = datetime.now()
        
        # If failed, store failure details
        if status == PaymentStatus.FAILED:
            payment.failure_reason = failure_reason
            payment.failure_code = failure_code
        
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        
        return payment
    
    def update(self, payment_id: int, payment_update: PaymentUpdate) -> Optional[Payment]:
        """
        Update payment with partial data
        
        Args:
            payment_id: Payment ID
            payment_update: PaymentUpdate schema with fields to update
            
        Returns:
            Updated Payment object or None if not found
        """
        payment = self.get_by_id(payment_id)
        
        if not payment:
            return None
        
        # Update only provided fields
        update_data = payment_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(payment, key, value)
        
        payment.updated_at = datetime.now()
        
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        
        return payment
    
    def get_by_status(
        self, 
        status: PaymentStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payment]:
        """
        Get all payments with a specific status
        
        Args:
            status: Payment status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Payment objects
        """
        statement = (
            select(Payment)
            .where(Payment.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        return list(self.session.exec(statement).all())
    
    def delete(self, payment_id: int) -> bool:
        """
        Delete a payment (soft delete - not recommended for payment records)
        
        Args:
            payment_id: Payment ID
            
        Returns:
            True if deleted, False if not found
        """
        payment = self.get_by_id(payment_id)
        
        if not payment:
            return False
        
        self.session.delete(payment)
        self.session.commit()
        
        return True
