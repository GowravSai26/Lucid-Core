from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import os

# ✅ Force-load .env from Backend directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str | None = None
    S3_ENDPOINT: str | None = None
    S3_BUCKET: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    class Config:
        env_file = env_path
        extra = "ignore"

settings = Settings()

# Debug Print
print("\n🔧 Loaded Environment Configuration:")
print(f"  DATABASE_URL  → {settings.DATABASE_URL}")
print(f"  REDIS_URL     → {settings.REDIS_URL}")
print(f"  GEMINI_API_KEY→ {'✅ Provided' if settings.GEMINI_API_KEY else '❌ Not Provided'}\n")
