from tortoise import fields, models
from tortoise.indexes import Index


class HourlyStatusMetric(models.Model):
    id = fields.IntField(primary_key=True)
    date = fields.DateField()
    hour = fields.IntField()
    status = fields.IntField()
    count = fields.IntField()
    total_duration = fields.IntField()
    avg_duration = fields.FloatField()

    class Meta:
        table = "analytics_hourly_status_metrics"
        unique_together = (("date", "hour", "status"),)
        indexes = [
            Index(fields=["date"]),
            Index(fields=["status"])
        ]


class HourlyOrderMetric(models.Model):
    id = fields.IntField(primary_key=True)
    date = fields.DateField()
    hour = fields.IntField()
    throughput = fields.IntField()

    class Meta:
        table = "analytics_hourly_order_metrics"
        unique_together = (("date", "hour"),)
        indexes = [
            Index(fields=["date"]),
        ]


class CustomerLifetimeMetric(models.Model):
    id = fields.IntField(primary_key=True)
    customer_id = fields.IntField(unique=True)
    order_count = fields.IntField()
    first_order_at = fields.DatetimeField()
    last_order_at = fields.DatetimeField()
    avg_order_frequency_days = fields.FloatField(null=True)

    class Meta:
        table = "analytics_customer_lifetime_metrics"
        indexes = [
            Index(fields=["customer_id"]),
            Index(fields=["order_count"])
        ]
