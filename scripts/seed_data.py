import asyncio
import logging
import random
from datetime import datetime, timedelta

from app.core.database import TORTOISE_ORM
from app.domains.orders.models import Address, Customer, Order, OrderItem, OrderStatusHistory
from tortoise import Tortoise

logger = logging.getLogger(__name__)


async def seed_data() -> None:
    await Tortoise.init(config=TORTOISE_ORM)

    customer_data: list[dict[str, str]] = [
        {"name": "John Doe", "phone": "123-456-7890"},
        {"name": "Jane Smith", "phone": "234-567-8901"},
        {"name": "Bob Johnson", "phone": "345-678-9012"},
    ]

    customers = []
    for data in customer_data:
        customer, _ = await Customer.get_or_create(defaults=data, phone=data["phone"])
        customers.append(customer)

    address_data: list[dict[str, str]] = [
        {"city": "New York", "street": "123 Broadway", "postal_code": "10001"},
        {"city": "Los Angeles", "street": "456 Hollywood Blvd", "postal_code": "90028"},
        {"city": "Chicago", "street": "789 Michigan Ave", "postal_code": "60611"},
    ]

    addresses = []
    for data in address_data:
        address, _ = await Address.get_or_create(defaults=data, city=data["city"], street=data["street"])
        addresses.append(address)

    now = datetime.utcnow()

    order_statuses = [1, 2, 3, 4, 5]

    food_items = [
        {"name": "Cheeseburger", "plu": "CB001"},
        {"name": "Fries", "plu": "FR001"},
        {"name": "Chicken Sandwich", "plu": "CS001"},
        {"name": "Pizza", "plu": "PZ001"},
        {"name": "Salad", "plu": "SL001"},
        {"name": "Ice Cream", "plu": "IC001"},
    ]

    for _index in range(20):
        customer = random.choice(customers)
        address = random.choice(addresses)

        pickup_time = now + timedelta(hours=random.randint(1, 24))

        order = await Order.create(
            channel_order_id=f"ORD-{random.randint(10000, 99999)}",
            account_id=f"ACC-{random.randint(100, 999)}",
            brand_id=f"BR-{random.randint(10, 99)}",
            pickup_time=pickup_time,
            customer=customer,
            address=address,
        )

        for _ in range(random.randint(1, 4)):
            item = random.choice(food_items)
            await OrderItem.create(
                order=order,
                name=item["name"],
                plu=item["plu"],
                quantity=random.randint(1, 3)
            )

        current_time = now - timedelta(hours=random.randint(1, 48))
        last_status_time = current_time

        for status in range(1, random.randint(2, 6)):
            if status > len(order_statuses):
                break

            current_status = order_statuses[status - 1]
            current_time = last_status_time + timedelta(minutes=random.randint(5, 30))

            duration = None
            if status > 1:
                duration = int((current_time - last_status_time).total_seconds())

            await OrderStatusHistory.create(
                order=order,
                status=current_status,
                timestamp=current_time,
                duration=duration
            )

            last_status_time = current_time

    logger.info(
        f"Added {len(customers)} customers, {len(addresses)} addresses, and 20 orders with items and status history")

    await Tortoise.close_connections()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_data())
