from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Payment Service Configuration
    Loads from environment variables or .env file
    """
    
    # Application Settings
    app_name: str = "Payment Service"
    debug: bool = False
    
    # Database Settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/payment_db"
    
    # PayFast Settings (Local Payment Gateway)
    payfast_merchant_id: str = ""
    payfast_merchant_key: str = ""
    payfast_passphrase: str = ""
    payfast_url: str = "https://sandbox.payfast.co.za/eng/process"
    
    # Stripe Settings (International Payment Gateway)
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    
    # Dapr Settings
    pubsub_name: str = "imtiaz-pubsub"
    dapr_grpc_port: int = 50001
    dapr_http_port: int = 3500
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance
    Only loads once during application lifetime
    """
    return Settings()


# Global settings instance
settings = get_settings()
