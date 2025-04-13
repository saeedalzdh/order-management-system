import logging
from datetime import date
from typing import Any

from kombu.exceptions import OperationalError

from app.core.celery import celery_app
from app.domains.analytics.repository import AnalyticsRepository

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self) -> None:
        self.analytics_repo = AnalyticsRepository()

    async def get_hourly_status_metrics(
            self,
            from_date: date,
            to_date: date,
            hour: int | None = None,
            status: int | None = None
    ) -> list[dict[str, Any]]:
        """Get hourly status metrics within a date range"""
        metrics = await self.analytics_repo.get_hourly_status_metrics(from_date, to_date, hour, status)

        response = []
        for metric in metrics:
            response.append({
                "date": metric.date.isoformat() if metric.date else None,
                "hour": metric.hour,
                "status": metric.status,
                "count": metric.count,
                "total_duration": metric.total_duration,
                "average_duration": metric.avg_duration
            })

        return response

    async def get_hourly_order_metrics(
            self,
            from_date: date,
            to_date: date,
            hour: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get hourly order throughput metrics within a date range"""
        metrics = await self.analytics_repo.get_hourly_order_metrics(
            from_date, to_date, hour
        )

        response = []
        for metric in metrics:
            response.append({
                "date": metric.date.isoformat() if metric.date else None,
                "hour": metric.hour,
                "throughput": metric.throughput
            })

        return response

    async def get_customer_lifetime_metrics(self, customer_id: int) -> dict[str, Any]:
        """Get lifetime metrics for a specific customer"""
        customer_exists = await self.analytics_repo.customer_exists(customer_id)
        if not customer_exists:
            raise ValueError(f"Customer {customer_id} not found")

        metric = await self.analytics_repo.get_customer_lifetime_metrics(customer_id)
        if not metric:
            raise ValueError(f"No metrics found for customer {customer_id}")

        return {
            "customer_id": metric.customer_id,
            "order_count": metric.order_count,
            "first_order_at": metric.first_order_at.isoformat() if metric.first_order_at else None,
            "last_order_at": metric.last_order_at.isoformat() if metric.last_order_at else None,
            "avg_order_frequency_days": metric.avg_order_frequency_days
        }

    async def list_customer_lifetime_metrics(
            self,
            min_order_count: int | None = None,
            from_date: date | None = None,
            to_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """List lifetime metrics for all customers with optional filtering"""
        metrics = await self.analytics_repo.list_customer_lifetime_metrics(
            min_order_count, from_date, to_date
        )

        items = []
        for metric in metrics:
            items.append({
                "customer_id": metric.customer_id,
                "order_count": metric.order_count,
                "first_order_at": metric.first_order_at.isoformat() if metric.first_order_at else None,
                "last_order_at": metric.last_order_at.isoformat() if metric.last_order_at else None,
                "avg_order_frequency_days": metric.avg_order_frequency_days
            })

        return items

    async def get_analytics_jobs_status(self, job_name: str | None = None) -> dict[str, Any]:
        """Get the status of analytics background jobs"""
        job_statuses = await self.analytics_repo.get_job_statuses(job_name)

        if job_name and not job_statuses:
            raise ValueError(f"Job {job_name} not found")

        active_tasks: dict[str, list[dict[str, Any]]] = {}
        scheduled_tasks: dict[str, list[dict[str, Any]]] = {}

        try:
            # get task information from Celery inspector
            inspector = celery_app.control.inspect()  # type: ignore[attr-defined]

            active_tasks = inspector.active() or {}
            scheduled_tasks = inspector.scheduled() or {}

            # filter by job name if specified
            if job_name:
                active_filtered = {}
                scheduled_filtered = {}

                for worker, tasks in active_tasks.items():
                    filtered_tasks = [t for t in tasks if job_name in t.get("name", "")]
                    if filtered_tasks:
                        active_filtered[worker] = filtered_tasks

                for worker, tasks in scheduled_tasks.items():
                    filtered_tasks = [t for t in tasks if job_name in t.get("name", "")]
                    if filtered_tasks:
                        scheduled_filtered[worker] = filtered_tasks

                active_tasks = active_filtered
                scheduled_tasks = scheduled_filtered
        except (OperationalError, ConnectionRefusedError) as e:
            logger.warning(f"Could not connect to Celery broker: {str(e)}")
        except Exception as e:
            logger.error(f"Error inspecting Celery tasks: {str(e)}")

        return {
            "jobs": job_statuses,
            "active_tasks": active_tasks,
            "scheduled_tasks": scheduled_tasks
        }
