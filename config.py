import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
  
    DATABASE_URL: str
    GEMINI_APIKEY:str
    
    DEBUG: bool = False


    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()