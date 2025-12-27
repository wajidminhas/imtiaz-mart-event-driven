from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status following industry standards"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    EXPIRED = "expired"
    CHARGEBACK = "chargeback"


class PaymentMethod(str, Enum):
    """Payment methods supported"""
    PAYFAST = "payfast"
    STRIPE = "stripe"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"


class PaymentBase(SQLModel):
    """
    Base Payment Schema - shared fields
    Used for inheritance by other schemas
    """
    order_id: int = Field(foreign_key="orders.id", index=True)
    user_id: int = Field(index=True)
    amount: float = Field(gt=0, description="Payment amount (must be positive)")
    currency: str = Field(default="PKR", max_length=3)
    payment_method: PaymentMethod
    payment_provider: str = Field(max_length=50)
    
    provider_transaction_id: Optional[str] = Field(default=None, max_length=255, index=True)
    provider_payment_id: Optional[str] = Field(default=None, max_length=255)
    
    description: Optional[str] = Field(default=None, max_length=500)
    payment_metadata: Optional[str] = Field(default=None)  # Changed from 'metadata'


class Payment(PaymentBase, table=True):
    """
    Payment Database Model - actual table in PostgreSQL
    """
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    
    refunded_amount: float = Field(default=0.0, ge=0)
    
    failure_reason: Optional[str] = Field(default=None, max_length=500)
    failure_code: Optional[str] = Field(default=None, max_length=50)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    expired_at: Optional[datetime] = Field(default=None)


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment (API request body)"""
    pass


class PaymentUpdate(SQLModel):
    """Schema for updating payment (API request body)"""
    status: Optional[PaymentStatus] = None
    provider_transaction_id: Optional[str] = Field(default=None, max_length=255)
    provider_payment_id: Optional[str] = Field(default=None, max_length=255)
    refunded_amount: Optional[float] = Field(default=None, ge=0)
    failure_reason: Optional[str] = Field(default=None, max_length=500)
    failure_code: Optional[str] = Field(default=None, max_length=50)
    completed_at: Optional[datetime] = None


class PaymentRead(PaymentBase):
    """Schema for reading payment (API response)"""
    id: int
    status: PaymentStatus
    refunded_amount: float
    failure_reason: Optional[str]
    failure_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
