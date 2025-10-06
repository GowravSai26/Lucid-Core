from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Get the absolute path to the Backend/.env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379"
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "lucid-artifacts"
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")

settings = Settings()

# Debug print to confirm loading
print("\n🔧 Loaded Environment Configuration:")
print(f"  DATABASE_URL  → {settings.DATABASE_URL}")
print(f"  REDIS_URL     → {settings.REDIS_URL}")
print(f"  S3_ENDPOINT   → {settings.S3_ENDPOINT}")
print(f"  S3_BUCKET     → {settings.S3_BUCKET}")
print(f"  OPENAI_API_KEY→ {'✅ Present' if settings.OPENAI_API_KEY else '❌ Not Provided'}\n")
