from tortoise.transactions import in_transaction

from app.api.v1.orders.schemas import Address, Customer, Order, OrderCreate, OrderItem, OrderStatus, OrderStatusEnum
from app.domains.orders.models import Order as OrderModel
from app.domains.orders.models import OrderItem as OrderItemModel
from app.domains.orders.models import OrderStatusHistory


class OrderRepository:
    @staticmethod
    def _order_storage_to_order_schema(order: OrderModel) -> Order:
        return Order(
            id=order.id,
            account_id=order.account_id,
            brand_id=order.brand_id,
            channel_order_id=order.channel_order_id,
            customer=Customer(
                name=order.customer.name,
                phoneNumber=order.customer.phone
            ),
            delivery_address=Address(
                city=order.address.city,
                street=order.address.street,
                postalCode=order.address.postal_code
            ),
            pickup_time=order.pickup_time,
            items=[OrderItem(
                id=item.id,
                order_id=order.id,
                name=item.name,
                plu=item.plu,
                quantity=item.quantity
            ) for item in order.items],
            status_history=[OrderStatus(
                id=status.id,
                order_id=order.id,
                status=status.status,
                timestamp=status.timestamp,
                duration=status.duration or None
            ) for status in order.status_history],
            created_at=order.created_at,
            status=order.status_history[-1].status if order.status_history else None
        )

    async def get_order(self, order_id: int) -> Order | None:
        order = await OrderModel.get_or_none(id=order_id).prefetch_related(
            "items",
            "status_history"
        ).select_related(
            "customer",
            "address"
        )

        if not order:
            return None

        return self._order_storage_to_order_schema(order)

    async def create_order(self, order: OrderCreate) -> Order:
        async with in_transaction():
            db_order = await OrderModel.create(
                account_id=order.account_id,
                brand_id=order.brand_id,
                channel_order_id=order.channel_order_id,
                customer_id=order.customer_id,
                address_id=order.address_id,
                pickup_time=order.pickup_time,
            )

            for item in order.items:
                await OrderItemModel.create(
                    order=db_order,
                    name=item.name,
                    plu=item.plu,
                    quantity=item.quantity
                )

            await OrderStatusHistory.create(
                order=db_order,
                status=OrderStatusEnum.RECEIVED.value,
            )

            complete_order = await OrderModel.get(id=db_order.id).prefetch_related(
                "items",
                "status_history"
            ).select_related(
                "customer",
                "address"
            )

            return self._order_storage_to_order_schema(complete_order)

    @staticmethod
    async def update_order_status(order_id: int, new_status: OrderStatusEnum) -> OrderStatus:
        async with in_transaction():
            order = await OrderModel.get_or_none(id=order_id)
            if not order:
                raise ValueError("Order not found")

            new_status_entry = await OrderStatusHistory.create(
                order=order,
                status=new_status.value,
            )

            previous_status = await OrderStatusHistory.filter(
                order=order
            ).order_by("-timestamp").offset(1).first()

            if previous_status:
                duration = new_status_entry.timestamp - previous_status.timestamp
                previous_status.duration = int(duration.total_seconds())
                await previous_status.save()

            return OrderStatus(
                id=new_status_entry.id,
                order_id=order_id,
                status=new_status_entry.status,
                timestamp=new_status_entry.timestamp,
                duration=previous_status.duration if previous_status else None
            )
