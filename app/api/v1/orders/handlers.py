from fastapi import Depends, HTTPException, Path

from app.api.v1.orders.schemas import Order, OrderCreate, OrderStatus, OrderStatusUpdate
from app.domains.orders.service import OrderService


async def get_order_handler(
    order_id: int = Path(...),
    service: OrderService = Depends()
) -> Order:
    try:
        order = await service.get_order(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")

async def create_order_handler(
    order: OrderCreate,
    service: OrderService = Depends()
) -> Order:
    try:
        return await service.create_order(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

async def update_order_status_handler(
    order_id: int = Path(...),
    status_update: OrderStatusUpdate | None = None,
    service: OrderService = Depends()
) -> OrderStatus:
    try:
        if status_update is None:
            raise HTTPException(status_code=400, detail="Status update is required")
        return await service.update_status(order_id, status_update.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")
