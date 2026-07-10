import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("autopatchforge")

class Settings(BaseSettings):
    """
    Application configuration.
    """
    app_env: str = Field(
        default="production",
        alias="APP_ENV",
    )
    api_base_url: str = Field(
        default="http://localhost/autopatch/api",
        alias="API_BASE_URL",
    )
    
    # Fireworks AI
    fireworks_api_key: str = Field(
        default="",
        alias="FIREWORKS_API_KEY"
    )
    
    # AI Models
    patch_planner_model: str = Field(
        default="accounts/fireworks/models/gemma-4-31b-it",
        alias="PATCH_PLANNER_MODEL"
    )
    risk_assessor_model: str = Field(
        default="accounts/fireworks/models/gemma-4-31b-it",
        alias="RISK_ASSESSOR_MODEL"
    )
    
    # Development
    enable_ai_patch_planner: bool = Field(
        default=True,
        alias="ENABLE_AI_PATCH_PLANNER"
    )

    # Natively check both files. Rightmost items take priority.
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Initialize settings
settings = Settings()

# Log the actual loaded state instead of guessing ahead of time
logger.info("Configuration successfully loaded. Current Environment: %s", settings.app_env)
