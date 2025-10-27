import os
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GAMMA_BASE_URL = "https://gamma-api.polymarket.com"


def _request_with_backoff(method: str, url: str, **kwargs) -> requests.Response:
    """HTTP request with simple exponential backoff and capped retries."""
    max_attempts = kwargs.pop("max_attempts", 4)
    backoff = kwargs.pop("backoff", 0.75)
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.request(method, url, timeout=kwargs.pop("timeout", 15), **kwargs)
            if 200 <= response.status_code < 300:
                return response
            # Retry on 5xx and 429
            if response.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"Transient error {response.status_code}")
            response.raise_for_status()
            return response
        except Exception as exc:  # noqa: BLE001
            if attempt == max_attempts:
                raise
            sleep_s = backoff * (2 ** (attempt - 1))
            time.sleep(sleep_s)
    raise RuntimeError("Unreachable")


def fetch_markets(query: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Fetch markets from Polymarket Gamma API.

    Args:
        query: Optional text to filter markets.
        limit: Max number of markets to return.
    Returns:
        Parsed JSON dict from Gamma.
    """
    params: Dict[str, Any] = {"limit": max(1, min(limit, 100))}
    if query:
        params["query"] = query
    url = f"{GAMMA_BASE_URL}/markets"
    resp = _request_with_backoff("GET", url, params=params)
    return resp.json()


def place_order(
    market_id: str,
    side: str,
    price: float,
    size: float,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Mocked order placement. In MVP we do not submit real orders.

    Args:
        market_id: Market identifier.
        side: "buy" or "sell".
        price: Price as decimal (0-1).
        size: Quantity to trade.
        dry_run: If True, only simulate and return stub.
    Returns:
        Dict with details and a mocked order id.
    """
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")

    if dry_run:
        return {
            "status": "dry_run",
            "message": "Order simulated; no live trade executed.",
            "market_id": market_id,
            "side": side,
            "price": price,
            "size": size,
            "order_id": f"dry_{int(time.time()*1000)}",
        }

    # Safety rail: live mode not enabled in MVP
    raise RuntimeError(
        "Live trading is disabled in MVP. Enable only after audit and confirmation."
    )
