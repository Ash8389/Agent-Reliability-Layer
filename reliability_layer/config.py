"""
Configuration settings for the Reliability Layer.
"""

from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Reliability Layer configuration settings."""
#     default_runs: int = 3
#     default_timeout: int = 30
#     default_mode: str = 'stabilize'
#     log_level: str = 'INFO'
#     max_concurrent_runs: int = 10

#     class Config:
#         env_prefix = "RELIABILITY_"

class Settings(BaseSettings):
    groq_api_key: str = ""
    reliability_default_runs: int = 3
    reliability_default_timeout: int = 30
    reliability_default_mode: str = "stabilize"
    reliability_log_level: str = "INFO"
    reliability_max_concurrent_runs: int = 10

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
