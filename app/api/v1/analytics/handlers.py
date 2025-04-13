from datetime import date
from typing import Any

from fastapi import Depends, HTTPException, Path, Query

from app.domains.analytics.service import AnalyticsService


async def get_hourly_status_metrics_handler(
        from_date: date = Query(..., description="Start date (inclusive)"),
        to_date: date = Query(..., description="End date (inclusive)"),
        hour: int | None = Query(None, description="Filter by specific hour (0-23)"),
        status: int | None = Query(None, description="Filter by status code"),
        analytics_service: AnalyticsService = Depends()
) -> list[dict[str, Any]]:
    """Get hourly status metrics within a date range"""
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")

    if hour is not None and not 0 <= hour <= 23:
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")

    return await analytics_service.get_hourly_status_metrics(from_date, to_date, hour, status)


async def get_hourly_order_metrics_handler(
        from_date: date = Query(..., description="Start date (inclusive)"),
        to_date: date = Query(..., description="End date (inclusive)"),
        hour: int | None = Query(None, description="Filter by specific hour (0-23)"),
        analytics_service: AnalyticsService = Depends()
) -> list[dict[str, Any]]:
    """Get hourly order throughput metrics within a date range"""
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")

    if hour is not None and not 0 <= hour <= 23:
        raise HTTPException(status_code=400, detail="Hour must be between 0 and 23")

    return await analytics_service.get_hourly_order_metrics(from_date, to_date, hour)


async def get_customer_lifetime_metrics_handler(
        customer_id: int = Path(..., description="Customer ID"),
        analytics_service: AnalyticsService = Depends()
) -> dict[str, Any]:
    """Get lifetime metrics for a specific customer"""
    try:
        return await analytics_service.get_customer_lifetime_metrics(customer_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")


async def list_customer_lifetime_metrics_handler(
        min_order_count: int | None = Query(None, description="Minimum number of orders"),
        from_date: date | None = Query(None, description="Filter by last order date (from)"),
        to_date: date | None = Query(None, description="Filter by last order date (to)"),
        analytics_service: AnalyticsService = Depends()
) -> list[dict[str, Any]]:
    """List lifetime metrics for all customers with optional filtering"""
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before or equal to to_date")

    return await analytics_service.list_customer_lifetime_metrics(
        min_order_count, from_date, to_date
    )

async def get_analytics_jobs_status_handler(
        job_name: str | None = Query(None, description="Filter by job name"),
        analytics_service: AnalyticsService = Depends()
) -> dict[str, Any]:
    """Get the status of analytics background jobs"""
    try:
        return await analytics_service.get_analytics_jobs_status(job_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
