from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings - loads from environment variables"""
    
    # Database Configuration
    database_url: str    
    
    # API Configuration
    app_name: str = "Inventory Service"
    debug: bool = True
    service_port: int = 8004
    
    # Dapr Configuration
    dapr_http_port: int = 3504
    dapr_grpc_port: int = 50005
    pubsub_name: str = "imtiaz-pubsub"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
