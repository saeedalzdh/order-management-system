import json
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

if settings.redis_url:
    redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
else:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )


async def set_job_status(job_name: str, status_data: dict[str, Any]) -> None:
    """
    Update the status of a background job in Redis
    """
    status_data["updated_at"] = datetime.utcnow().isoformat()

    key = f"job_status:{job_name}"
    await redis_client.set(key, json.dumps(status_data))
    await redis_client.expire(key, settings.redis_expiration_time)


async def get_job_status(job_name: str) -> dict[str, Any] | None:
    """
    Retrieve the current status of a background job from Redis
    """
    key = f"job_status:{job_name}"
    status_json = await redis_client.get(key)

    if status_json:
        return json.loads(status_json)  # type: ignore[no-any-return]
    return None


async def clear_job_status(job_name: str) -> None:
    """
    Remove job status from Redis
    """
    key = f"job_status:{job_name}"
    await redis_client.delete(key)
