"""Smoke tests for ACP endpoints (no signature verification — merchant secret injected)."""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ["VEYRA_MERCHANT_SECRET_test_key"] = "test_secret"

# Monkeypatch signature verification for smoke tests
from app import signing as _sig  # noqa: E402


def _always_valid(*_args, **_kwargs) -> bool:
    return True


_sig.verify_openai_signature = _always_valid  # type: ignore

from app.main import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


HEADERS = {
    "Authorization": "Bearer test_key",
    "Signature": "sig",
    "Timestamp": "2026-08-26T00:00:00Z",
    "Idempotency-Key": "test_idem_1",
    "Request-Id": "test_req_1",
    "Content-Type": "application/json",
    "API-Version": "2025-09-12",
}


def test_full_checkout_lifecycle(client: TestClient) -> None:
    r = client.post(
        "/checkout_sessions",
        headers=HEADERS,
        json={"items": [{"id": "sku_1", "quantity": 2}]},
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]

    r = client.post(
        f"/checkout_sessions/{sid}",
        headers=HEADERS,
        json={"items": [{"id": "sku_1", "quantity": 3}]},
    )
    assert r.status_code == 200
    assert r.json()["items"][0]["quantity"] == 3

    r = client.get(f"/checkout_sessions/{sid}", headers=HEADERS)
    assert r.status_code == 200

    r = client.post(
        f"/checkout_sessions/{sid}/complete",
        headers=HEADERS,
        json={
            "buyer": {"first_name": "Ali", "email": "ali@example.com"},
            "payment_data": {"token": "delegated_pm_123"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "completed"
    assert body["ap2_mandate_signature"].startswith("unsigned:") or "." in body["ap2_mandate_signature"]


def test_cancel(client: TestClient) -> None:
    r = client.post("/checkout_sessions", headers=HEADERS, json={"items": [{"id": "x", "quantity": 1}]})
    sid = r.json()["id"]
    r = client.post(f"/checkout_sessions/{sid}/cancel", headers=HEADERS)
    assert r.json()["status"] == "canceled"
