from tortoise import Model, fields
from tortoise.fields.relational import ForeignKeyRelation
from tortoise.indexes import Index


class Customer(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    phone = fields.CharField(max_length=20, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    orders: fields.ReverseRelation["Order"]

    class Meta:
        table = "customers"

class Address(Model):
    id = fields.IntField(primary_key=True)
    city = fields.CharField(max_length=100)
    street = fields.CharField(max_length=255)
    postal_code = fields.CharField(max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "addresses"

class Order(Model):
    id = fields.IntField(primary_key=True)
    channel_order_id = fields.CharField(max_length=255)
    account_id = fields.CharField(max_length=255)
    brand_id = fields.CharField(max_length=255)
    pickup_time = fields.DatetimeField()
    customer: ForeignKeyRelation[Customer] = fields.ForeignKeyField(
        "orders.Customer", related_name="orders"
    )
    address: ForeignKeyRelation[Address] = fields.ForeignKeyField(
        "orders.Address", related_name="orders"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    items: fields.ReverseRelation["OrderItem"]
    status_history: fields.ReverseRelation["OrderStatusHistory"]

    class Meta:
        table = "orders"

class OrderItem(Model):
    id = fields.IntField(primary_key=True)
    order: ForeignKeyRelation[Order] = fields.ForeignKeyField(
        "orders.Order", related_name="items"
    )
    name = fields.CharField(max_length=255)
    plu = fields.CharField(max_length=50)
    quantity = fields.IntField()

    class Meta:
        table = "order_items"

class OrderStatusHistory(Model):
    id = fields.IntField(primary_key=True)
    order: ForeignKeyRelation[Order] = fields.ForeignKeyField(
        "orders.Order", related_name="status_history"
    )
    status = fields.IntField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    duration = fields.IntField(null=True)

    class Meta:
        table = "order_status_history"
        indexes = [Index(fields=["order_id", "timestamp"])]
