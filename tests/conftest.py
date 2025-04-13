from collections.abc import AsyncGenerator

import pytest_asyncio
from app.core.database import TORTOISE_ORM_TEST
from app.main import app as _app
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise


async def app() -> FastAPI:
    return _app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_tests() -> AsyncGenerator[None, None]:
    await Tortoise.init(config=TORTOISE_ORM_TEST)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    fastapi_app: FastAPI = await app()

    transport = ASGITransport(app=fastapi_app)

    async with AsyncClient(
            transport=transport,
            base_url="http://testserver"
    ) as client:
        yield client
