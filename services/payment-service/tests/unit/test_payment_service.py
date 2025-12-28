import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session, create_engine, SQLModel
from app.models.payment import Payment, PaymentCreate, PaymentStatus, PaymentMethod
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(in_memory_db):
    """Create a database session for testing"""
    with Session(in_memory_db) as session:
        yield session


@pytest.fixture
def payment_repository(db_session):
    """Create PaymentRepository instance"""
    return PaymentRepository(db_session)


@pytest.fixture
def payment_service(payment_repository):
    """Create PaymentService instance"""
    return PaymentService(payment_repository)


class TestPaymentService:
    """Test suite for PaymentService"""
    
    def test_create_payment_success(self, payment_service):
        """Test creating a payment successfully"""
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=100.50,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        with patch('app.services.payment_service.publish_payment_initiated') as mock_publish:
            mock_publish.return_value = True
            
            payment = payment_service.create_payment(payment_data)
            
            assert payment.id is not None
            assert payment.status == PaymentStatus.PENDING
            assert payment.amount == 100.50
            mock_publish.assert_called_once()
    
    def test_get_payment_by_id(self, payment_service):
        """Test getting payment by ID"""
        # Create a payment first
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=200.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        with patch('app.services.payment_service.publish_payment_initiated'):
            created = payment_service.create_payment(payment_data)
        
        # Get it
        payment = payment_service.get_payment(created.id)
        
        assert payment is not None
        assert payment.id == created.id
    
    def test_get_payment_not_found_raises_exception(self, payment_service):
        """Test that getting non-existent payment raises exception"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            payment_service.get_payment(99999)
        
        assert exc_info.value.status_code == 404
    
    def test_complete_payment_success(self, payment_service):
        """Test completing a payment"""
        # Create payment
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=300.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        with patch('app.services.payment_service.publish_payment_initiated'):
            payment = payment_service.create_payment(payment_data)
        
        # Complete payment
        with patch('app.services.payment_service.publish_payment_completed') as mock_publish:
            mock_publish.return_value = True
            
            completed = payment_service.complete_payment(
                payment_id=payment.id,
                provider_transaction_id="txn_123456"
            )
            
            assert completed.status == PaymentStatus.COMPLETED
            assert completed.provider_transaction_id == "txn_123456"
            assert completed.completed_at is not None
            mock_publish.assert_called_once()
    
    def test_fail_payment_success(self, payment_service):
        """Test failing a payment"""
        # Create payment
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=150.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        with patch('app.services.payment_service.publish_payment_initiated'):
            payment = payment_service.create_payment(payment_data)
        
        # Fail payment
        with patch('app.services.payment_service.publish_payment_failed') as mock_publish:
            mock_publish.return_value = True
            
            failed = payment_service.fail_payment(
                payment_id=payment.id,
                failure_reason="Insufficient funds",
                failure_code="INSUFFICIENT_FUNDS"
            )
            
            assert failed.status == PaymentStatus.FAILED
            assert failed.failure_reason == "Insufficient funds"
            mock_publish.assert_called_once()
