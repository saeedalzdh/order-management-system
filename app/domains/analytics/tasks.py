import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from typing import Any, TypeVar, cast

from tortoise import Tortoise
from tortoise.functions import Count, Sum

from app.core.cache import set_job_status
from app.core.celery import celery_app
from app.core.database import TORTOISE_ORM
from app.domains.analytics.models import CustomerLifetimeMetric, HourlyOrderMetric, HourlyStatusMetric
from app.domains.orders.models import Customer, Order, OrderStatusHistory

logger = logging.getLogger(__name__)

T = TypeVar("T")


def tortoise_task(task_func: Callable[..., Awaitable[T]]) -> Any:
    """Decorator to initialize Tortoise ORM for celery tasks"""
    task_name = f"app.domains.analytics.tasks.{task_func.__name__}"

    @celery_app.task(name=task_name)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()

        async def run_task() -> T:
            await Tortoise.init(config=TORTOISE_ORM)
            try:
                return await task_func(*args, **kwargs)
            finally:
                await Tortoise.close_connections()

        return loop.run_until_complete(run_task())

    return wrapper


@tortoise_task
async def aggregate_hourly_metrics(target_hour: str | None = None) -> str:
    """Aggregate metrics for a specific hour or the previous hour if not specified"""
    try:
        await set_job_status("hourly_metrics", {"status": "running"})

        if target_hour:
            target_hour_dt = datetime.fromisoformat(target_hour)
        else:
            now = datetime.now(timezone.utc)
            target_hour_dt = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            logger.info(f"Current UTC time: {now}, using previous hour: {target_hour_dt}")

        target_date = target_hour_dt.date()
        hour = target_hour_dt.hour
        hour_start = target_hour_dt
        hour_end = hour_start + timedelta(hours=1)

        logger.info(f"Processing hourly metrics for {target_date} hour {hour}")

        status_results = await OrderStatusHistory.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).group_by("status").annotate(
            count=Count("id"),
            total_duration=Sum("duration")
        ).values("status", "count", "total_duration")

        logger.info(f"Retrieved {len(status_results)} status results")
        for result in status_results:
            total_duration = result["total_duration"] or 0
            average_duration = total_duration / result["count"] if result["count"] > 0 else 0
            await HourlyStatusMetric.update_or_create(
                date=target_date,
                hour=hour,
                status=result["status"],
                defaults={
                    "count": result["count"],
                    "total_duration": total_duration,
                    "avg_duration": average_duration
                }
            )

        total_orders = await Order.filter(
            created_at__gte=hour_start,
            created_at__lt=hour_end
        ).count()

        await HourlyOrderMetric.update_or_create(
            date=target_date,
            hour=hour,
            defaults={"throughput": total_orders}
        )

        await set_job_status("hourly_metrics", {
            "status": "completed",
            "processed_date": target_date.isoformat(),
            "processed_hour": hour,
            "order_count": total_orders,
            "status_count": len(status_results)
        })

        return f"Processed metrics for {target_date} hour {hour}"

    except Exception as e:
        logger.error(f"Error processing hourly metrics: {str(e)}")
        await set_job_status("hourly_metrics", {
            "status": "failed",
            "error": str(e)
        })
        raise


@tortoise_task
async def update_customer_metrics(customer_id: int | None = None) -> str:
    """Update customer lifetime metrics for a specific customer or all customers"""
    try:
        await set_job_status("customer_metrics", {"status": "running"})

        if customer_id:
            customers = await Customer.filter(id=customer_id).prefetch_related("orders")
            if not customers:
                return f"Customer with ID {customer_id} not found"
        else:
            # batch processing for all customers
            batch_size = 100
            offset = 0
            processed_count = 0

            while True:
                customers_batch = await Customer.all().offset(offset).limit(batch_size).prefetch_related("orders")
                if not customers_batch:
                    break

                processed_count += await _process_customer_batch(customers_batch)
                offset += batch_size

            await set_job_status("customer_metrics", {
                "status": "completed",
                "processed_customers": processed_count
            })

            return f"Updated metrics for {processed_count} customers"

        # For single customer case
        processed_count = await _process_customer_batch(customers)

        await set_job_status("customer_metrics", {
            "status": "completed",
            "processed_customers": processed_count
        })

        return f"Updated metrics for {processed_count} customers"

    except Exception as e:
        logger.error(f"Error updating customer metrics: {str(e)}")
        await set_job_status("customer_metrics", {
            "status": "failed",
            "error": str(e)
        })
        raise


async def _process_customer_batch(customers: list[Customer]) -> int:
    """Process a batch of customers and return count of processed records"""
    processed_count = 0
    metrics_to_update = []

    for customer in customers:
        orders = sorted(customer.orders, key=lambda o: o.created_at)
        if not orders:
            continue

        order_count = len(orders)
        first_order_at = orders[0].created_at
        last_order_at = orders[-1].created_at

        avg_frequency = None
        if order_count > 1:
            total_days = (last_order_at - first_order_at).days
            avg_frequency = total_days / (order_count - 1) if total_days > 0 else 0

        metrics_to_update.append({
            "customer_id": customer.id,
            "defaults": {
                "order_count": order_count,
                "first_order_at": first_order_at,
                "last_order_at": last_order_at,
                "avg_order_frequency_days": avg_frequency
            }
        })
        processed_count += 1

    # bulk update in batches of 50
    for i in range(0, len(metrics_to_update), 50):
        batch = metrics_to_update[i:i + 50]
        for metric in batch:
            await CustomerLifetimeMetric.update_or_create(
                customer_id=metric["customer_id"],
                defaults=cast(dict[str, Any], metric["defaults"])
            )

    return processed_count
