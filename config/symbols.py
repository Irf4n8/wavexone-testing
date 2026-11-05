"""
Symbol configurations and test order matrix definitions for WavexOne.
"""

TEST_SYMBOLS = {
    "C:EURUSD": {"name": "EURUSD", "min_lot": 0.01, "digits": 5, "type": "forex"},
    "C:GBPUSD": {"name": "GBPUSD", "min_lot": 0.01, "digits": 5, "type": "forex"},
    "C:USDJPY": {"name": "USDJPY", "min_lot": 0.01, "digits": 3, "type": "forex"},
    "C:XAUUSD": {"name": "XAUUSD", "min_lot": 0.01, "digits": 2, "type": "commodity"},
    "X:BTCUSD": {"name": "BTCUSD", "min_lot": 0.01, "digits": 2, "type": "crypto"},
}

# 10 Orders per module: 5 BUY, 5 SELL across 5 liquid symbols
ORDER_MATRIX_PLAN = [
    # Leg 1: Market BUYs
    {"id": 1, "symbol": "C:EURUSD", "side": "buy", "lot": 0.01, "type": "market"},
    {"id": 2, "symbol": "C:GBPUSD", "side": "buy", "lot": 0.01, "type": "market"},
    {"id": 3, "symbol": "C:USDJPY", "side": "buy", "lot": 0.01, "type": "market"},
    {"id": 4, "symbol": "C:XAUUSD", "side": "buy", "lot": 0.01, "type": "market"},
    {"id": 5, "symbol": "X:BTCUSD", "side": "buy", "lot": 0.01, "type": "market"},
    # Leg 2: Market SELLs
    {"id": 6, "symbol": "C:EURUSD", "side": "sell", "lot": 0.01, "type": "market"},
    {"id": 7, "symbol": "C:GBPUSD", "side": "sell", "lot": 0.01, "type": "market"},
    {"id": 8, "symbol": "C:USDJPY", "side": "sell", "lot": 0.01, "type": "market"},
    {"id": 9, "symbol": "C:XAUUSD", "side": "sell", "lot": 0.01, "type": "market"},
    {"id": 10, "symbol": "X:BTCUSD", "side": "sell", "lot": 0.01, "type": "market"},
]

