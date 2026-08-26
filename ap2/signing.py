"""
Google AP2 CheckoutMandate signing (skeleton).
Spec: https://ap2-protocol.org/ + https://ucp.dev/documentation/ucp-and-ap2/

Real implementation should use google-agentic-commerce/AP2 Python SDK once
published to PyPI. This scaffold uses PyJWT with the merchant private key
to produce a detached JWT of the CheckoutObject hash.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any

try:
    import jwt  # PyJWT
except ImportError:  # scaffold, install with `uv pip install pyjwt cryptography`
    jwt = None  # type: ignore


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _checkout_object_hash(cart_state: dict[str, Any]) -> str:
    canonical = _canonical_json(
        {
            "id": cart_state["id"],
            "items": cart_state["items"],
            "totals": cart_state["totals"],
            "fulfillment_address": cart_state.get("fulfillment_address"),
        }
    )
    return hashlib.sha256(canonical).hexdigest()


def sign_checkout_mandate(cart_state: dict[str, Any]) -> str:
    """Return detached JWT signing the CheckoutObject hash (AP2 mandate)."""
    if jwt is None:
        return f"unsigned:{_checkout_object_hash(cart_state)}"
    key_path = os.environ.get("VEYRA_AP2_PRIVATE_KEY_PATH", "")
    if not key_path or not os.path.exists(key_path):
        return f"unsigned:{_checkout_object_hash(cart_state)}"
    with open(key_path, "rb") as f:
        private_key = f.read()
    payload = {
        "iss": os.environ.get("VEYRA_MERCHANT_ID", "veyra-scaffold"),
        "iat": int(time.time()),
        "checkout_hash": _checkout_object_hash(cart_state),
        "cart_totals": cart_state["totals"],
    }
    return jwt.encode(payload, private_key, algorithm="ES256")


def verify_payment_mandate(mandate_jwt: str, expected_hash: str, issuer_public_key: bytes) -> bool:
    """Verify PaymentMandate JWT from platform matches our CheckoutMandate hash."""
    if jwt is None:
        return False
    try:
        decoded = jwt.decode(mandate_jwt, issuer_public_key, algorithms=["ES256"])
    except jwt.InvalidTokenError:
        return False
    return decoded.get("checkout_hash") == expected_hash
