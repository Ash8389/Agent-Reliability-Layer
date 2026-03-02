"""
Configuration settings for the Reliability Layer.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Reliability Layer configuration settings."""
    default_runs: int = 3
    default_timeout: int = 30
    default_mode: str = 'stabilize'
    log_level: str = 'INFO'
    max_concurrent_runs: int = 10

    class Config:
        env_prefix = "RELIABILITY_"


settings = Settings()
