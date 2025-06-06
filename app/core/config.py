"""Application configuration settings using Pydantic."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "Flights API"
    app_version: str = "0.1.0"
    debug: bool = False
    mongodb_url: str = "mongodb://localhost:27017/flights"
    seed_data: bool = False
    
    class Config:
        """Pydantic config."""
        
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""


# Create a global settings instance
settings = Settings()
