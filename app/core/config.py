import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = False
    database_url: str | None = os.environ.get("DATABASE_URL")
    redis_url: str | None = os.environ.get("REDIS_URL")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
    redis_db: int = int(os.environ.get("REDIS_DB", 0))
    redis_expiration_time: int = int(os.environ.get("REDIS_EXPIRATION_TIME", 60 * 60 * 24 * 7))  # 7 days
    redis_job_names: list[str] = ["hourly_metrics", "customer_metrics"]
    aggregate_hourly_metrics_interval: int = int(os.environ.get("AGGREGATE_HOURLY_METRICS_INTERVAL", 3600))  # 1 hour
    update_customer_metrics_interval: int = int(os.environ.get("UPDATE_CUSTOMER_METRICS_INTERVAL", 86400))  # 1 day


@lru_cache
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()


settings = get_settings()
