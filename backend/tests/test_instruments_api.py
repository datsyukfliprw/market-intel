from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


def create_instrument(
    client: TestClient,
    symbol: str = "AAPL",
    **kwargs: object,
) -> dict[str, Any]:
    payload = {
        "symbol": symbol,
        "name": kwargs.get("name", "Apple Inc."),
        "exchange": kwargs.get("exchange", "NASDAQ"),
        "asset_type": kwargs.get("asset_type", "stock"),
        "sector": kwargs.get("sector", "Technology"),
        "industry": kwargs.get("industry", "Consumer Electronics"),
        "currency": kwargs.get("currency", "USD"),
    }

    response = client.post("/instruments", json=payload)

    assert response.status_code == 201

    body: dict[str, Any] = response.json()

    return body


def test_create_instrument(
    client: TestClient,
) -> None:
    body = create_instrument(client)

    assert body["symbol"] == "AAPL"
    assert body["name"] == "Apple Inc."
    assert body["exchange"] == "NASDAQ"
    assert body["asset_type"] == "stock"
    assert body["currency"] == "USD"
    assert body["is_active"] is True
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_normalize_symbol_to_uppercase(
    client: TestClient,
) -> None:
    body = create_instrument(client, symbol="aapl")

    assert body["symbol"] == "AAPL"


def test_normalize_currency_to_uppercase(
    client: TestClient,
) -> None:
    body = create_instrument(client, symbol="MSFT", currency="usd")

    assert body["currency"] == "USD"


def test_reject_empty_symbol(
    client: TestClient,
) -> None:
    response = client.post(
        "/instruments",
        json={
            "symbol": "",
            "asset_type": "stock",
        },
    )

    assert response.status_code == 422


def test_reject_invalid_currency_length(
    client: TestClient,
) -> None:
    response = client.post(
        "/instruments",
        json={
            "symbol": "TSLA",
            "asset_type": "stock",
            "currency": "US",
        },
    )

    assert response.status_code == 422


def test_rejects_duplicate_symbol(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="AAPL")

    response = client.post(
        "/instruments",
        json={
            "symbol": "aapl",
            "asset_type": "stock",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Instrument with this symbol already exists",
    }


def test_list_instruments(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="AAPL")
    create_instrument(client, symbol="MSFT")

    response = client.get("/instruments")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["symbol"] == "AAPL"
    assert body[1]["symbol"] == "MSFT"


def test_active_instruments_appear_before_inactive(
    client: TestClient,
) -> None:
    inactive = create_instrument(
        client,
        symbol="AA",
        name="Inactive Co",
    )

    create_instrument(
        client,
        symbol="ZZ",
        name="Active Co",
    )

    response = client.patch(
        f"/instruments/{inactive['id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200

    response = client.get("/instruments")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["symbol"] == "ZZ"
    assert body[1]["symbol"] == "AA"
    assert body[0]["is_active"] is True
    assert body[1]["is_active"] is False


def test_get_instrument_by_id(
    client: TestClient,
) -> None:
    created = create_instrument(client)

    response = client.get(f"/instruments/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_instrument_by_lowercase_symbol(
    client: TestClient,
) -> None:
    created = create_instrument(client, symbol="NVDA")

    response = client.get("/instruments/by-symbol/nvda")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["symbol"] == "NVDA"


def test_get_instrument_missing_id_returns_404(
    client: TestClient,
) -> None:
    response = client.get(f"/instruments/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Instrument not found",
    }


def test_get_instrument_missing_symbol_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/instruments/by-symbol/NOPE")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Instrument not found",
    }


def test_update_instrument_metadata(
    client: TestClient,
) -> None:
    created = create_instrument(client, symbol="AMD")

    response = client.patch(
        f"/instruments/{created['id']}",
        json={
            "name": "Advanced Micro Devices, Inc.",
            "sector": "Semiconductors",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Advanced Micro Devices, Inc."
    assert body["sector"] == "Semiconductors"
    assert body["symbol"] == "AMD"


def test_deactivate_instrument(
    client: TestClient,
) -> None:
    created = create_instrument(client, symbol="INTC")

    response = client.patch(
        f"/instruments/{created['id']}",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_patch_cannot_change_symbol(
    client: TestClient,
) -> None:
    created = create_instrument(client, symbol="META")

    response = client.patch(
        f"/instruments/{created['id']}",
        json={
            "symbol": "FB",
            "name": "Meta Platforms, Inc.",
        },
    )

    assert response.status_code == 422

    response = client.get(f"/instruments/{created['id']}")

    assert response.status_code == 200

    body = response.json()

    assert body["symbol"] == "META"
    assert body["name"] == "Apple Inc."


def test_search_by_partial_symbol(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="AAPL")
    create_instrument(client, symbol="MSFT")

    response = client.get("/instruments?query=AAP")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["symbol"] == "AAPL"


def test_search_by_partial_company_name(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="TSLA", name="Tesla, Inc.")

    response = client.get("/instruments?query=Tes")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["symbol"] == "TSLA"


def test_search_is_case_insensitive(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="GOOGL", name="Alphabet Inc.")

    response = client.get("/instruments?query=alphabet")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["symbol"] == "GOOGL"


def test_limit_and_offset_work(
    client: TestClient,
) -> None:
    create_instrument(client, symbol="A")
    create_instrument(client, symbol="B")
    create_instrument(client, symbol="C")

    response = client.get("/instruments?limit=2&offset=1")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["symbol"] == "B"
    assert body[1]["symbol"] == "C"


def test_invalid_limit_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/instruments?limit=0")

    assert response.status_code == 422

    response = client.get("/instruments?limit=201")

    assert response.status_code == 422
