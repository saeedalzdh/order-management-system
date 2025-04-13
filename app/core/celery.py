from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "analytics",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.domains.analytics.tasks"]
)

celery_app.conf.beat_schedule = {
    "aggregate-hourly-metrics": {
        "task": "app.domains.analytics.tasks.aggregate_hourly_metrics",
        "schedule": settings.aggregate_hourly_metrics_interval,  # Run hourly by default
        "args": (None,),
    },
    "update-customer-metrics": {
        "task": "app.domains.analytics.tasks.update_customer_metrics",
        "schedule": settings.update_customer_metrics_interval,  # Run daily by default
        "args": (None,),
    },
}

celery_app.conf.timezone = "UTC"
