from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "orders": {
            "models": ["app.domains.orders.models", "app.domains.analytics.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

TORTOISE_ORM_TEST = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "orders": {
            "models": ["app.domains.orders.models"],
            "default_connection": "default",
        }
    },
}

def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False, # to avoid generating schemas on every startup
        add_exception_handlers=True,
    )
