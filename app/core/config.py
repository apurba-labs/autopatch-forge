import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("AutoPatchForge")


# ---------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------

class Settings(BaseSettings):
    """
    Application configuration loaded from .env
    """

    # -------------------------------------------------------------
    # Fireworks AI
    # -------------------------------------------------------------
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_BASE_URL: str = "https://api.fireworks.ai/inference/v1"

    # -------------------------------------------------------------
    # AI Models
    # -------------------------------------------------------------
    PATCH_PLANNER_MODEL: str = (
        "accounts/fireworks/models/gemma-3-27b-it"
    )

    RISK_ASSESSOR_MODEL: str = (
        "accounts/fireworks/models/gemma-3-27b-it"
    )

    # -------------------------------------------------------------
    # Development
    # -------------------------------------------------------------
    ENABLE_AI_PATCH_PLANNER: bool = True

    # -------------------------------------------------------------
    # Pydantic Settings
    # -------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()