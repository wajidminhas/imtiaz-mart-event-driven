import pytest
from datetime import datetime
from app.models.payment import (
    Payment, 
    PaymentCreate, 
    PaymentRead, 
    PaymentUpdate,
    PaymentStatus,
    PaymentMethod
)


class TestPaymentModel:
    """Test suite for Payment model"""
    
    def test_payment_create_valid_data(self):
        """Test creating a payment with valid data"""
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,  # Added user_id
            amount=100.50,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        assert payment_data.order_id == 1
        assert payment_data.user_id == 1
        assert payment_data.amount == 100.50
        assert payment_data.currency == "PKR"
        assert payment_data.payment_method == PaymentMethod.PAYFAST
    
    def test_payment_amount_must_be_positive(self):
        """Test that payment amount must be greater than 0"""
        with pytest.raises(ValueError):
            PaymentCreate(
                order_id=1,
                user_id=1,  # Added user_id
                amount=-10.0,  # Invalid: negative amount
                currency="PKR",
                payment_method=PaymentMethod.PAYFAST,
                payment_provider="payfast"
            )
    
    def test_payment_default_currency_is_pkr(self):
        """Test that default currency is PKR"""
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,  # Added user_id
            amount=100.0,
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        assert payment_data.currency == "PKR"
    
    def test_payment_status_enum(self):
        """Test payment status enum values"""
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.COMPLETED == "completed"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.REFUNDED == "refunded"
    
    def test_payment_method_enum(self):
        """Test payment method enum values"""
        assert PaymentMethod.PAYFAST == "payfast"
        assert PaymentMethod.STRIPE == "stripe"
        assert PaymentMethod.CARD == "card"
    
    def test_payment_with_optional_fields(self):
        """Test creating payment with optional fields"""
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=250.75,
            currency="USD",
            payment_method=PaymentMethod.STRIPE,
            payment_provider="stripe",
            description="Test payment for order #1",
            provider_transaction_id="txn_123456",
            payment_metadata='{"customer_email": "test@example.com"}'
        )
        
        assert payment_data.description == "Test payment for order #1"
        assert payment_data.provider_transaction_id == "txn_123456"
        assert payment_data.payment_metadata is not None
