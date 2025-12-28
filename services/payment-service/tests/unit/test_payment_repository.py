import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from app.models.payment import Payment, PaymentCreate, PaymentStatus, PaymentMethod
from app.repositories.payment_repository import PaymentRepository


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


class TestPaymentRepository:
    """Test suite for PaymentRepository"""
    
    def test_create_payment(self, payment_repository):
        """Test creating a new payment"""
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=100.50,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        
        created_payment = payment_repository.create(payment_data)
        
        assert created_payment.id is not None
        assert created_payment.order_id == 1
        assert created_payment.user_id == 1
        assert created_payment.amount == 100.50
        assert created_payment.status == PaymentStatus.PENDING
    
    def test_get_payment_by_id(self, payment_repository):
        """Test retrieving a payment by ID"""
        # Create a payment first
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=200.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        created_payment = payment_repository.create(payment_data)
        
        # Retrieve it
        retrieved_payment = payment_repository.get_by_id(created_payment.id)
        
        assert retrieved_payment is not None
        assert retrieved_payment.id == created_payment.id
        assert retrieved_payment.amount == 200.00
    
    def test_get_payment_by_id_not_found(self, payment_repository):
        """Test retrieving a non-existent payment returns None"""
        payment = payment_repository.get_by_id(99999)
        assert payment is None
    
    def test_get_payments_by_user_id(self, payment_repository):
        """Test retrieving all payments for a user"""
        # Create multiple payments for the same user
        for i in range(3):
            payment_data = PaymentCreate(
                order_id=i + 1,
                user_id=1,
                amount=100.00 * (i + 1),
                currency="PKR",
                payment_method=PaymentMethod.PAYFAST,
                payment_provider="payfast"
            )
            payment_repository.create(payment_data)
        
        # Retrieve all payments for user
        user_payments = payment_repository.get_by_user_id(user_id=1)
        
        assert len(user_payments) == 3
        assert all(p.user_id == 1 for p in user_payments)
    
    def test_get_payment_by_order_id(self, payment_repository):
        """Test retrieving payment by order ID"""
        payment_data = PaymentCreate(
            order_id=123,
            user_id=1,
            amount=500.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        created_payment = payment_repository.create(payment_data)
        
        # Retrieve by order_id
        payment = payment_repository.get_by_order_id(order_id=123)
        
        assert payment is not None
        assert payment.order_id == 123
    
    def test_update_payment_status(self, payment_repository):
        """Test updating payment status"""
        # Create payment
        payment_data = PaymentCreate(
            order_id=1,
            user_id=1,
            amount=100.00,
            currency="PKR",
            payment_method=PaymentMethod.PAYFAST,
            payment_provider="payfast"
        )
        created_payment = payment_repository.create(payment_data)
        
        # Update status to COMPLETED
        updated_payment = payment_repository.update_status(
            payment_id=created_payment.id,
            status=PaymentStatus.COMPLETED,
            provider_transaction_id="txn_123456"
        )
        
        assert updated_payment.status == PaymentStatus.COMPLETED
        assert updated_payment.provider_transaction_id == "txn_123456"
        assert updated_payment.completed_at is not None
