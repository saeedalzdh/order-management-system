from fastapi import Depends

from app.api.v1.orders.schemas import Order, OrderCreate, OrderStatus, OrderStatusEnum
from app.domains.orders.repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository = Depends()):
        self.repository = repository

    async def get_order(self, order_id: int) -> Order | None:
        return await self.repository.get_order(order_id)

    async def create_order(self, order: OrderCreate) -> Order:
        return await self.repository.create_order(order)

    async def update_status(self, order_id: int, new_status: OrderStatusEnum) -> OrderStatus:
        return await self.repository.update_order_status(order_id, new_status)
