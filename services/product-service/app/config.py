from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings - loads from environment variables"""
    
    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/product_db"
    
    # API Configuration
    app_name: str = "Product Service"
    debug: bool = True
    
    # Dapr Configuration
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    pubsub_name: str = "imtiaz-pubsub"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Create singleton instance
settings = Settings()