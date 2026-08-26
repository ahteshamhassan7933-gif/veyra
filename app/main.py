"""
Veyra — OpenAI Agentic Commerce Protocol endpoint scaffold.
Spec: https://developers.openai.com/commerce/specs/checkout

Five required endpoints:
  POST /checkout_sessions
  POST /checkout_sessions/{id}
  POST /checkout_sessions/{id}/complete
  POST /checkout_sessions/{id}/cancel
  GET  /checkout_sessions/{id}

All requests carry: Authorization, Signature, Timestamp, Idempotency-Key,
Request-Id, API-Version.
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from .signing import verify_openai_signature
from ..ap2.signing import sign_checkout_mandate

API_VERSION = "2025-09-12"
app = FastAPI(title="Veyra ACP", version="0.1.0")

# In-memory store for scaffold; swap for Postgres/D1 in prod.
SESSIONS: dict[str, dict[str, Any]] = {}


class Item(BaseModel):
    id: str
    quantity: int = Field(ge=1)


class Address(BaseModel):
    name: str | None = None
    line_one: str
    line_two: str | None = None
    city: str
    state: str | None = None
    country: str
    postal_code: str


class Buyer(BaseModel):
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None


class CheckoutCreateRequest(BaseModel):
    buyer: Buyer | None = None
    items: list[Item]
    fulfillment_address: Address | None = None


class CheckoutUpdateRequest(BaseModel):
    buyer: Buyer | None = None
    items: list[Item] | None = None
    fulfillment_address: Address | None = None


class CheckoutCompleteRequest(BaseModel):
    buyer: Buyer
    payment_data: dict[str, Any]


async def _authenticate(request: Request, authorization: str | None, signature: str | None, timestamp: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    api_key = authorization.removeprefix("Bearer ")
    body = await request.body()
    if not verify_openai_signature(api_key, body, signature, timestamp):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad signature")


def _cart_state(session_id: str) -> dict[str, Any]:
    s = SESSIONS[session_id]
    subtotal = sum(i["quantity"] * 1000 for i in s["items"])  # placeholder pricing
    return {
        "id": session_id,
        "status": s["status"],
        "buyer": s.get("buyer"),
        "items": s["items"],
        "fulfillment_address": s.get("fulfillment_address"),
        "totals": {"subtotal": subtotal, "shipping": 0, "tax": 0, "total": subtotal, "currency": "USD"},
        "messages": [],
        "errors": [],
    }


@app.post("/checkout_sessions", status_code=201)
async def create_session(
    payload: CheckoutCreateRequest,
    request: Request,
    authorization: str | None = Header(None),
    signature: str | None = Header(None, alias="Signature"),
    timestamp: str | None = Header(None, alias="Timestamp"),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    await _authenticate(request, authorization, signature, timestamp)
    sid = f"cs_{uuid.uuid4().hex}"
    SESSIONS[sid] = {
        "status": "in_progress",
        "items": [i.model_dump() for i in payload.items],
        "buyer": payload.buyer.model_dump() if payload.buyer else None,
        "fulfillment_address": payload.fulfillment_address.model_dump() if payload.fulfillment_address else None,
        "created": time.time(),
    }
    return _cart_state(sid)


@app.post("/checkout_sessions/{session_id}")
async def update_session(
    session_id: str,
    payload: CheckoutUpdateRequest,
    request: Request,
    authorization: str | None = Header(None),
    signature: str | None = Header(None, alias="Signature"),
    timestamp: str | None = Header(None, alias="Timestamp"),
) -> dict[str, Any]:
    await _authenticate(request, authorization, signature, timestamp)
    if session_id not in SESSIONS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    s = SESSIONS[session_id]
    if payload.items is not None:
        s["items"] = [i.model_dump() for i in payload.items]
    if payload.buyer is not None:
        s["buyer"] = payload.buyer.model_dump()
    if payload.fulfillment_address is not None:
        s["fulfillment_address"] = payload.fulfillment_address.model_dump()
    return _cart_state(session_id)


@app.get("/checkout_sessions/{session_id}")
async def get_session(
    session_id: str,
    request: Request,
    authorization: str | None = Header(None),
    signature: str | None = Header(None, alias="Signature"),
    timestamp: str | None = Header(None, alias="Timestamp"),
) -> dict[str, Any]:
    await _authenticate(request, authorization, signature, timestamp)
    if session_id not in SESSIONS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return _cart_state(session_id)


@app.post("/checkout_sessions/{session_id}/complete")
async def complete_session(
    session_id: str,
    payload: CheckoutCompleteRequest,
    request: Request,
    authorization: str | None = Header(None),
    signature: str | None = Header(None, alias="Signature"),
    timestamp: str | None = Header(None, alias="Timestamp"),
) -> dict[str, Any]:
    await _authenticate(request, authorization, signature, timestamp)
    if session_id not in SESSIONS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    s = SESSIONS[session_id]
    s["status"] = "completed"
    s["order_id"] = f"ord_{uuid.uuid4().hex}"
    state = _cart_state(session_id)
    state["ap2_mandate_signature"] = sign_checkout_mandate(state)
    return state


@app.post("/checkout_sessions/{session_id}/cancel")
async def cancel_session(
    session_id: str,
    request: Request,
    authorization: str | None = Header(None),
    signature: str | None = Header(None, alias="Signature"),
    timestamp: str | None = Header(None, alias="Timestamp"),
) -> dict[str, Any]:
    await _authenticate(request, authorization, signature, timestamp)
    if session_id not in SESSIONS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    SESSIONS[session_id]["status"] = "canceled"
    return _cart_state(session_id)
