import pytest
from app.database import payment_db, PaymentDatabase
from app.config import settings


class TestPaymentDatabase:
    """Test suite for Payment Database"""
    
    def test_payment_db_instance_exists(self):
        """Test that payment_db singleton exists"""
        assert payment_db is not None
        assert isinstance(payment_db, PaymentDatabase)
    
    def test_database_engine_created(self):
        """Test that database engine is created"""
        assert payment_db.engine is not None
    
    def test_database_url_from_settings(self):
        """Test that database URL is loaded from settings"""
        assert settings.database_url is not None
        assert "postgresql" in settings.database_url
    
    def test_get_session_returns_session(self):
        """Test that get_session returns a valid session"""
        session = payment_db.get_session()
        assert session is not None
        session.close()
    
    def test_settings_has_payment_gateway_config(self):
        """Test that settings include payment gateway configurations"""
        assert hasattr(settings, 'payfast_merchant_id')
        assert hasattr(settings, 'stripe_api_key')
