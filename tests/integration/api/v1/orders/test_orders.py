from collections.abc import AsyncGenerator

import pytest
from app.domains.orders.models import Address, Customer, Order, OrderItem, OrderStatusHistory
from httpx import AsyncClient
from pytest_asyncio import fixture as async_fixture


@async_fixture
async def customer() -> Customer:
    existing = await Customer.all().count()
    if existing > 0:
        pytest.fail("Existing customers found. Database not clean!")
    return await Customer.create(name="Test Customer", phone="1234567890")

@async_fixture
async def address() -> Address:
    existing = await Address.all().count()
    if existing > 0:
        pytest.fail("Existing addresses found. Database not clean!")
    return await Address.create(city="Test City", street="Test St", postal_code="12345")

@async_fixture(autouse=True)
async def cleanup_db() -> AsyncGenerator[None, None]:
    """Automatically cleanup database after each test."""
    yield
    await Customer.all().delete()
    await Address.all().delete()
    await Order.all().delete()
    await OrderItem.all().delete()
    await OrderStatusHistory.all().delete()

@pytest.mark.asyncio
async def test_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.text == "OK"


@pytest.mark.asyncio
async def test_create_order(client: AsyncClient, customer: Customer, address: Address) -> None:
    order_data = {
        "channel_order_id": "test123",
        "account_id": "acct123",
        "brand_id": "brand123",
        "pickup_time": "2023-10-01T12:00:00",
        "customer_id": customer.id,
        "address_id": address.id,
        "items": [
            {
                "name": "Item 1",
                "plu": "PLU123",
                "quantity": 2
            }
        ]
    }

    response = await client.post("/api/v1/orders/", json=order_data)

    assert response.status_code == 201
    data = response.json()
    assert data["channel_order_id"] == "test123"
    assert data["customer"]["name"] == customer.name
    assert data["delivery_address"]["city"] == address.city
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_get_order(client: AsyncClient, customer: Customer, address: Address) -> None:
    order = await Order.create(
        channel_order_id="test123",
        account_id="acct123",
        brand_id="brand123",
        pickup_time="2023-10-01T12:00:00",
        customer=customer,
        address=address
    )

    response = await client.get(f"/api/v1/orders/{order.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order.id
    assert data["channel_order_id"] == "test123"


@pytest.mark.asyncio
async def test_update_order_status(client: AsyncClient, customer: Customer, address: Address) -> None:
    order = await Order.create(
        channel_order_id="test123",
        account_id="acct123",
        brand_id="brand123",
        pickup_time="2023-10-01T12:00:00",
        customer=customer,
        address=address
    )

    status_data = {"status": 2}
    response = await client.put(f"/api/v1/orders/{order.id}/status", json=status_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == 2

    status_history = await order.status_history.all()
    assert len(status_history) == 1
    assert status_history[0].status == 2
