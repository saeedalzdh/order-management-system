from fastapi import APIRouter

from app.api.v1.analytics.routes import router as analytics_router
from app.api.v1.orders.routes import router as orders_router

router = APIRouter(prefix="/api/v1")

router.include_router(orders_router)
router.include_router(analytics_router)
