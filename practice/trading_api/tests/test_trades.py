import pytest

# ─── CREATE TESTS ───────────────────────────────────────

@pytest.mark.asyncio
async def test_create_trade_success(client):
    response = await client.post("/trades/", json={
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["quantity"] == 10
    assert data["price"] == 150.0
    assert data["status"] == "pending"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_trade_invalid_symbol(client):
    response = await client.post("/trades/", json={
        "symbol": "AAPL123",
        "quantity": 10,
        "price": 150.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_trade_negative_quantity(client):
    response = await client.post("/trades/", json={
        "symbol": "AAPL",
        "quantity": -5,
        "price": 150.0
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_trade_zero_price(client):
    response = await client.post("/trades/", json={
        "symbol": "AAPL",
        "quantity": 10,
        "price": 0
    })
    assert response.status_code == 422

# ─── GET TESTS ───────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_trades_empty(client):
    response = await client.get("/trades/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_all_trades(client):
    await client.post("/trades/", json={
        "symbol": "AAPL", "quantity": 10, "price": 150.0
    })
    await client.post("/trades/", json={
        "symbol": "GOOG", "quantity": 5, "price": 200.0
    })
    response = await client.get("/trades/")
    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_get_trade_by_id(client):
    create = await client.post("/trades/", json={
        "symbol": "AAPL", "quantity": 10, "price": 150.0
    })
    trade_id = create.json()["id"]
    response = await client.get(f"/trades/{trade_id}")
    assert response.status_code == 200
    assert response.json()["id"] == trade_id

@pytest.mark.asyncio
async def test_get_trade_not_found(client):
    response = await client.get("/trades/999")
    assert response.status_code == 404

# ─── FILTER + PAGINATION TESTS ───────────────────────────────────────

@pytest.mark.asyncio
async def test_filter_by_symbol(client):
    await client.post("/trades/", json={
        "symbol": "AAPL", "quantity": 10, "price": 150.0
    })
    await client.post("/trades/", json={
        "symbol": "GOOG", "quantity": 5, "price": 200.0
    })
    symbol="AAPL"
    response = await client.get(f"/trades/symbol/{symbol}")
    assert response.status_code == 200
    data = response.json()
    assert all(t["symbol"] == "AAPL" for t in data)



@pytest.mark.asyncio
async def test_pagination_hard_cap(client):
    response = await client.get("/trades/?limit=200")
    assert response.status_code == 200   # should not error
    # limit silently capped at 100

# ─── CANCEL TESTS ───────────────────────────────────────

@pytest.mark.asyncio
async def test_cancel_trade(client):
    create = await client.post("/trades/", json={
        "symbol": "AAPL", "quantity": 10, "price": 150.0
    })
    trade_id = create.json()["id"]
    response = await client.patch(f"/trades/{trade_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

@pytest.mark.asyncio
async def test_cancel_already_cancelled(client):
    create = await client.post("/trades/", json={
        "symbol": "AAPL", "quantity": 10, "price": 150.0
    })
    trade_id = create.json()["id"]
    await client.patch(f"/trades/{trade_id}/cancel")
    response = await client.patch(f"/trades/{trade_id}/cancel")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cancel_nonexistent_trade(client):
    response = await client.patch("/trades/999/cancel")
    assert response.status_code == 404

# ─── AUTH TESTS ───────────────────────────────────────
from httpx import AsyncClient, ASGITransport
from apis.trading_api.app.main import app as fastapi_app

@pytest.mark.asyncio
async def test_missing_api_key():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test"
        # no X-API-Key header
    ) as no_auth_client:
        response = await no_auth_client.get("/trades/")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_wrong_api_key():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        headers={"X-API-Key": "wrong-key"}
    ) as bad_client:
        response = await bad_client.get("/trades/")
        assert response.status_code == 403