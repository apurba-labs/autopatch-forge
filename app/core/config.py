# app/core/config.py
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure production-ready logging immediately
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AutoPatchForge")

class Settings(BaseSettings):
    # Core API keys and routing configuration
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"
    AMD_CLOUD_GEMMA_ENDPOINT: str = "http://localhost:8000/v1"
    
    # Models mapped out for our multi-agent architecture
    LOG_PARSER_MODEL: str = "accounts/fireworks/models/llama-v3-70b-instruct"
    GEMMA_AUDITOR_MODEL: str = "google/gemma-2-27b-it"

    # Pydantic v2 automatic env file loader configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()