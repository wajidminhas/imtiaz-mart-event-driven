"""
Configuration Management for Product Service
Uses Pydantic Settings for type-safe configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Product Service"
    debug: bool = False
    api_version: str = "v1"
    
    # Database Configuration
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "product_db"
    db_host: str = "localhost"
    db_port: int = 5432
    database_url: str | None = None
    
    # Dapr Configuration
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    dapr_host: str = "localhost"  # ✨ NEW: Configurable host for Docker
    pubsub_name: str = "order-pubsub"
    
    # Kafka Configuration (for reference)
    kafka_bootstrap_servers: str = "localhost:9092"
    
    # API Configuration
    api_prefix: str = "/api/v1"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def get_database_url(self) -> str:
        """
        Construct database URL if not provided directly
        Useful for both local and Docker environments
        """
        if self.database_url:
            return self.database_url
        
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.db_port}/{self.postgres_db}"
        )
    
    @property
    def dapr_pubsub_url(self) -> str:
        """Construct Dapr publish URL"""
        return f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}"


@lru_cache
def get_settings() -> Settings:
    """
    Create cached settings instance
    Uses lru_cache to avoid recreating on every call
    """
    return Settings()


# Convenience exports
settings = get_settings()