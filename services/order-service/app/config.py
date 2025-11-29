from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings - loads from environment variables"""
    
    # Database Configuration
    database_url: str    
    
    # API Configuration
    app_name: str = "Order Service"
    debug: bool = True
    service_port: int = 8003  # Different port from product (8001)
    
    # Dapr Configuration
    dapr_http_port: int = 3503  # Different from product (3501)
    dapr_grpc_port: int = 50004  # Different from product (50002)
    pubsub_name: str = "imtiaz-pubsub"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
