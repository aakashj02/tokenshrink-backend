import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TokenShrink API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Credentials
    OPENAI_API_KEY: str
    
    # Pricing per 1M tokens for gpt-4o-mini
    INPUT_TOKEN_PRICE_PER_MILLION: float = 0.15
    OUTPUT_TOKEN_PRICE_PER_MILLION: float = 0.60

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings(_env_file=".env" if os.path.exists(".env") else None)