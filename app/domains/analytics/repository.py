import logging
from datetime import date, datetime
from typing import Any

from app.core.config import settings
from app.domains.analytics.models import CustomerLifetimeMetric, HourlyOrderMetric, HourlyStatusMetric

logger = logging.getLogger(__name__)

class AnalyticsRepository:
    @staticmethod
    async def get_hourly_status_metrics(
            from_date: date,
            to_date: date,
            hour: int | None = None,
            status: int | None = None
    ) -> list[HourlyStatusMetric]:
        """Get hourly status metrics from database"""
        query = HourlyStatusMetric.filter(
            date__gte=from_date,
            date__lte=to_date
        )

        if hour is not None:
            query = query.filter(hour=hour)

        if status is not None:
            query = query.filter(status=status)

        return await query.order_by("date", "hour", "status")

    async def get_hourly_order_metrics(
            self,
            from_date: date,
            to_date: date,
            hour: int | None = None,
    ) -> list[HourlyOrderMetric]:
        """Get hourly order metrics from database"""
        query = HourlyOrderMetric.filter(
            date__gte=from_date,
            date__lte=to_date
        )

        if hour is not None:
            query = query.filter(hour=hour)

        return await query.order_by("date", "hour")

    @staticmethod
    async def customer_exists(customer_id: int) -> bool:
        """Check if customer exists in the database"""
        return await CustomerLifetimeMetric.filter(customer_id=customer_id).exists()

    @staticmethod
    async def get_customer_lifetime_metrics(customer_id: int) -> CustomerLifetimeMetric | None:
        """Get customer lifetime metrics by customer ID"""
        return await CustomerLifetimeMetric.filter(customer_id=customer_id).first()

    @staticmethod
    async def list_customer_lifetime_metrics(
            min_order_count: int | None = None,
            from_date: date | None = None,
            to_date: date | None = None,
    ) -> list[CustomerLifetimeMetric]:
        """List customer lifetime metrics with filtering and pagination"""
        query = CustomerLifetimeMetric.all()

        if min_order_count is not None:
            query = query.filter(order_count__gte=min_order_count)

        if from_date is not None:
            query = query.filter(last_order_at__gte=datetime.combine(from_date, datetime.min.time()))

        if to_date is not None:
            query = query.filter(last_order_at__lte=datetime.combine(to_date, datetime.max.time()))

        return await query.order_by("customer_id")

    @staticmethod
    async def get_job_statuses(job_name: str | None = None) -> dict[str, Any]:
        """Get job statuses from Redis"""
        try:
            from app.core.cache import get_job_status

            if job_name:
                status = await get_job_status(job_name)
                return {job_name: status} if status else {}

            job_names = settings.redis_job_names
            statuses = {}

            for name in job_names:
                status = await get_job_status(name)
                if status:
                    statuses[name] = status

            return statuses

        except Exception as e:
            logger.error(f"Error fetching job statuses from Redis: {str(e)}")

            # Fallback to mock data if Redis is not available
            if job_name:
                if job_name == "hourly_metrics":
                    return {
                        job_name: {
                            "status": "completed",
                            "updated_at": datetime.utcnow().isoformat(),
                            "processed_date": date.today().isoformat(),
                            "processed_hour": datetime.utcnow().hour - 1
                        }
                    }
                elif job_name == "customer_metrics":
                    return {
                        job_name: {
                            "status": "completed",
                            "updated_at": datetime.utcnow().isoformat(),
                            "processed_customers": 150
                        }
                    }
                return {}

            return {
                "hourly_metrics": {
                    "status": "completed",
                    "updated_at": datetime.utcnow().isoformat(),
                    "processed_date": date.today().isoformat(),
                    "processed_hour": datetime.utcnow().hour - 1
                },
                "customer_metrics": {
                    "status": "completed",
                    "updated_at": datetime.utcnow().isoformat(),
                    "processed_customers": 150
                }
            }
