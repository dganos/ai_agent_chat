import json
import os
import threading
import time
from queue import Queue, Empty
from typing import Any, Callable, Dict, Generator, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GAMMA_BASE_URL = "https://gamma-api.polymarket.com"
DEFAULT_CLOB_WS_URL = os.getenv("POLYMARKET_CLOB_WS_URL", "wss://clob.polymarket.com/ws")


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


def fetch_historical_data(market_id: str, limit: int = 500) -> Dict[str, Any]:
    """Attempt to fetch historical trade data for a market.

    Tries a couple of likely endpoints; gracefully degrades if unavailable.
    """
    candidate_paths = [
        f"/markets/{market_id}/trades",
        f"/markets/{market_id}/history",
        f"/markets/{market_id}",
    ]
    last_error: Optional[str] = None
    for path in candidate_paths:
        url = f"{GAMMA_BASE_URL}{path}"
        try:
            resp = _request_with_backoff("GET", url, params={"limit": limit})
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            continue
    return {"status": "unavailable", "message": last_error or "No endpoint available"}


def stream_clob_prices(
    market_id: Optional[str] = None,
    ws_url: Optional[str] = None,
    max_messages: Optional[int] = None,
    connect_timeout_s: int = 10,
) -> Generator[Dict[str, Any], None, None]:
    """Yield messages from the Polymarket CLOB websocket.

    This is a best-effort generic stream. Message formats may change; consumers
    should defensively handle fields.
    """
    try:
        from websocket import WebSocketApp  # type: ignore
    except Exception as import_exc:  # noqa: BLE001
        yield {"error": f"websocket-client not installed: {import_exc}"}
        return

    effective_url = ws_url or DEFAULT_CLOB_WS_URL

    messages_queue: Queue[str] = Queue()
    connected_event = threading.Event()
    stop_event = threading.Event()

    def on_open(_ws):  # noqa: ANN001
        connected_event.set()
        # Attempt a generic subscription if market_id provided (schema may vary)
        if market_id:
            try:
                subscribe_payload = json.dumps({"type": "subscribe", "marketId": market_id})
                _ws.send(subscribe_payload)
            except Exception:
                pass

    def on_message(_ws, message: str):  # noqa: ANN001
        messages_queue.put(message)

    def on_error(_ws, error):  # noqa: ANN001
        messages_queue.put(json.dumps({"error": str(error)}))

    def on_close(_ws, _code, _reason):  # noqa: ANN001
        stop_event.set()

    ws_app = WebSocketApp(
        effective_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    thread = threading.Thread(target=lambda: ws_app.run_forever(ping_interval=20, ping_timeout=10))
    thread.daemon = True
    thread.start()

    # Wait for connection
    connected_event.wait(timeout=connect_timeout_s)

    yielded = 0
    try:
        while not stop_event.is_set():
            try:
                raw = messages_queue.get(timeout=1)
            except Empty:
                continue
            try:
                data = json.loads(raw)
            except Exception:
                data = {"raw": raw}
            yielded += 1
            yield data
            if max_messages and yielded >= max_messages:
                break
    finally:
        try:
            ws_app.close()
        except Exception:
            pass


def calculate_arbitrage_opportunity(
    yes_price_a: float,
    yes_price_b: float,
    fee_rate: float = 0.02,
) -> Dict[str, Any]:
    """Compute simple arbitrage spread for YES prices across two markets.

    Returns positive spread when actionable after fees.
    """
    spread = abs(yes_price_a - yes_price_b)
    actionable = spread > fee_rate
    better_market = "A" if yes_price_a < yes_price_b else "B"
    return {
        "spread": spread,
        "actionable": actionable,
        "buy_on": better_market,
        "sell_on": "B" if better_market == "A" else "A",
    }


def position_size_simple(bankroll_usdc: float, risk_fraction: float, price: float) -> float:
    """Position size as units given bankroll and risk fraction."""
    risk_fraction = max(0.0, min(risk_fraction, 1.0))
    budget = bankroll_usdc * risk_fraction
    if price <= 0:
        return 0.0
    return round(budget / price, 6)


def apply_stop_loss(current_price: float, entry_price: float, threshold: float = 0.1) -> bool:
    """Return True when current drawdown exceeds threshold."""
    if entry_price <= 0:
        return False
    drawdown = (entry_price - current_price) / entry_price
    return drawdown >= max(0.0, threshold)
