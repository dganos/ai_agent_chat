import os
import time
from typing import Any, Dict, Optional, Callable, List

import requests
from dotenv import load_dotenv

try:
    # Optional dependency for real-time market data
    import websocket  # type: ignore
except Exception:  # noqa: BLE001
    websocket = None  # type: ignore

load_dotenv()

GAMMA_BASE_URL = "https://gamma-api.polymarket.com"
ARBITRAGE_MAX_REL_SPREAD_DEFAULT = 0.02


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


def compute_mid_price(orderbook: Dict[str, Any]) -> Optional[float]:
    """Compute mid price from orderbook snapshot that contains best bid/ask."""
    try:
        best_bid = float(orderbook.get("best_bid", 0))
        best_ask = float(orderbook.get("best_ask", 0))
        if best_bid <= 0 or best_ask <= 0:
            return None
        return (best_bid + best_ask) / 2.0
    except Exception:  # noqa: BLE001
        return None


def detect_simple_arbitrage(
    market_a_price: float,
    market_b_price: float,
    max_rel_spread: float = ARBITRAGE_MAX_REL_SPREAD_DEFAULT,
) -> Optional[Dict[str, Any]]:
    """Detect basic arbitrage opportunity given two prices.

    Returns dict describing the opportunity or None.
    """
    if market_a_price <= 0 or market_b_price <= 0:
        return None
    spread = abs(market_a_price - market_b_price)
    rel = spread / max(market_a_price, market_b_price)
    if rel >= max_rel_spread:
        return {"spread": spread, "relative": rel, "direction": "A>B" if market_a_price > market_b_price else "B>A"}
    return None


# --- ML/Data scaffolding (lightweight, optional) ---
def simple_moving_average(series: List[float], window: int = 5) -> List[Optional[float]]:
    """Compute a simple moving average for a numeric series.

    Returns list aligned with input, with None for indices where window is incomplete.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    result: List[Optional[float]] = []
    total = 0.0
    for i, val in enumerate(series):
        total += val
        if i >= window:
            total -= series[i - window]
        if i + 1 >= window:
            result.append(total / window)
        else:
            result.append(None)
    return result


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


def subscribe_orderbook_ws(
    market_id: str,
    on_message: Callable[[Dict[str, Any]], None],
    on_error: Optional[Callable[[str], None]] = None,
    on_close: Optional[Callable[[], None]] = None,
):
    """Subscribe to Polymarket CLOB WebSocket for a single market orderbook updates.

    This is a minimal helper that relies on the `websocket-client` package if available.
    """
    if websocket is None:
        raise RuntimeError(
            "websocket-client is not installed. Please add it to requirements to use WS."
        )

    ws_url = "wss://clob.polymarket.com/ws"

    def _on_open(ws):  # type: ignore[no-redef]
        # Subscribe message format may vary; this uses a common schema
        sub_msg = {"type": "subscribe", "channel": "orderbook", "market": market_id}
        ws.send(__import__("json").dumps(sub_msg))

    def _on_message(ws, message):  # type: ignore[no-redef]
        try:
            data = __import__("json").loads(message)
            on_message(data)
        except Exception as exc:  # noqa: BLE001
            if on_error:
                on_error(f"Failed to parse message: {exc}")

    def _on_error(ws, error):  # type: ignore[no-redef]
        if on_error:
            on_error(str(error))

    def _on_close(ws, *args):  # type: ignore[no-redef]
        if on_close:
            on_close()

    ws_app = websocket.WebSocketApp(  # type: ignore[attr-defined]
        ws_url,
        on_open=_on_open,
        on_message=_on_message,
        on_error=_on_error,
        on_close=_on_close,
    )

    # Run forever in the calling thread; user can manage threading
    ws_app.run_forever(ping_interval=20, ping_timeout=10)
