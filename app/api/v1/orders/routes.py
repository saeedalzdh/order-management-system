from fastapi import APIRouter

from app.api.v1.orders.handlers import create_order_handler, get_order_handler, update_order_status_handler
from app.api.v1.orders.schemas import Order, OrderStatus

router = APIRouter(tags=["Orders"], prefix="/orders")

router.add_api_route(
    path="/{order_id}",
    endpoint=get_order_handler,
    methods=["GET"],
    response_model=Order,
    status_code=200,
    responses={
        400: {"description": "Invalid order ID"},
        404: {"description": "Order not found"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/",
    endpoint=create_order_handler,
    methods=["POST"],
    response_model=Order,
    status_code=201,
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Server error"}
    }
)

router.add_api_route(
    path="/{order_id}/status",
    endpoint=update_order_status_handler,
    methods=["PUT"],
    response_model=OrderStatus,
    status_code=201,
    responses={
        400: {"description": "Invalid status or request format"},
        404: {"description": "Order not found"},
        500: {"description": "Server error"}
    }
)
