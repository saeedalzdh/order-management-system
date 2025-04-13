from typing import Any

from fastapi import APIRouter

from app.api.v1.analytics.handlers import (
    get_analytics_jobs_status_handler,
    get_customer_lifetime_metrics_handler,
    get_hourly_order_metrics_handler,
    get_hourly_status_metrics_handler,
    list_customer_lifetime_metrics_handler,
)
from app.api.v1.analytics.schemas import (
    CustomerLifetimeMetric,
    HourlyOrderMetric,
    HourlyStatusMetric,
)

router = APIRouter(tags=["Analytics"], prefix="/analytics")

router.add_api_route(
    path="/status-metrics",
    endpoint=get_hourly_status_metrics_handler,
    methods=["GET"],
    response_model=list[HourlyStatusMetric],
    status_code=200,
    responses={
        400: {"description": "Invalid date parameters"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/order-metrics",
    endpoint=get_hourly_order_metrics_handler,
    methods=["GET"],
    response_model=list[HourlyOrderMetric],
    status_code=200,
    responses={
        400: {"description": "Invalid date parameters"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/customers/{customer_id}/lifetime-orders",
    endpoint=get_customer_lifetime_metrics_handler,
    methods=["GET"],
    response_model=CustomerLifetimeMetric,
    status_code=200,
    responses={
        404: {"description": "Customer not found"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/customers/lifetime-orders",
    endpoint=list_customer_lifetime_metrics_handler,
    methods=["GET"],
    response_model=list[CustomerLifetimeMetric],
    status_code=200,
    responses={
        400: {"description": "Invalid parameters"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/jobs/status",
    endpoint=get_analytics_jobs_status_handler,
    methods=["GET"],
    response_model=dict[str, Any],
    status_code=200,
    responses={
        500: {"description": "Server error"}
    }
)
