import json
from typing import Any, Dict

import pytest

from polymarket.api_helpers import (
    compute_mid_price,
    detect_simple_arbitrage,
    simple_moving_average,
)


def test_compute_mid_price():
    assert compute_mid_price({"best_bid": 0.4, "best_ask": 0.6}) == 0.5
    assert compute_mid_price({"best_bid": 0.0, "best_ask": 0.6}) is None
    assert compute_mid_price({}) is None


def test_detect_simple_arbitrage():
    # No arb when spread below threshold
    assert detect_simple_arbitrage(0.50, 0.505, max_rel_spread=0.02) is None
    # Arb when above threshold
    arb = detect_simple_arbitrage(0.6, 0.55, max_rel_spread=0.05)
    assert arb is not None
    assert "spread" in arb and "relative" in arb and "direction" in arb


def test_simple_moving_average():
    sma = simple_moving_average([1, 2, 3, 4, 5, 6], window=3)
    assert sma[:2] == [None, None]
    assert sma[2] == pytest.approx(2.0)
    assert sma[-1] == pytest.approx(5.0)
