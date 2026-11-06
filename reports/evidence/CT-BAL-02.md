# Evidence Report: CT-BAL-02 — Proportional Balance-Based Market SELL Copying (0.50 Master Lot -> Dynamic Balance Ratio Sizing)

- **Category:** Balance-Based Copy Trading
- **Status:** `PASS`
- **Execution Time:** 6.37s
- **Timestamp:** 2026-11-06 13:01:08

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Pre-Flight Zero Open Orders | `True` | `True` | ✅ PASS |
| 2 | All Followers Switched to Balance Mode | `True` | `True` | ✅ PASS |
| 3 | ctf1 Balance Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 4 | ctf2 Balance Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 5 | ctf3 Balance Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 6 | ctf4 Balance Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 7 | ctf5 Balance Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 8 | Master Order Found in Book | `True` | `True` | ✅ PASS |
| 9 | Master Lot Size is 0.50 | `0.5` | `0.5` | ✅ PASS |
| 10 | Master Fill Price Valid | `True` | `True` | ✅ PASS |
| 11 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |
| 12 | Replicated Count == 5 | `5` | `5` | ✅ PASS |
| 13 | ctf2 Direction is SELL | `SELL` | `SELL` | ✅ PASS |
| 14 | ctf2 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 15 | ctf2 Replication Latency <= 2.5s | `<= 2500ms` | `192.96ms` | ✅ PASS |
| 16 | ctf2 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `8.9 pts` | ✅ PASS |
| 17 | ctf5 Direction is SELL | `SELL` | `SELL` | ✅ PASS |
| 18 | ctf5 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 19 | ctf5 Replication Latency <= 2.5s | `<= 2500ms` | `192.96ms` | ✅ PASS |
| 20 | ctf5 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `8.9 pts` | ✅ PASS |
| 21 | ctf1 Direction is SELL | `SELL` | `SELL` | ✅ PASS |
| 22 | ctf1 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 23 | ctf1 Replication Latency <= 2.5s | `<= 2500ms` | `192.96ms` | ✅ PASS |
| 24 | ctf1 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `8.9 pts` | ✅ PASS |
| 25 | ctf4 Direction is SELL | `SELL` | `SELL` | ✅ PASS |
| 26 | ctf4 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 27 | ctf4 Replication Latency <= 2.5s | `<= 2500ms` | `192.96ms` | ✅ PASS |
| 28 | ctf4 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `8.9 pts` | ✅ PASS |
| 29 | ctf3 Direction is SELL | `SELL` | `SELL` | ✅ PASS |
| 30 | ctf3 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 31 | ctf3 Replication Latency <= 2.5s | `<= 2500ms` | `208.36ms` | ✅ PASS |
| 32 | ctf3 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `8.9 pts` | ✅ PASS |
| 33 | All Positions Cleanly Liquidated | `True` | `True` | ✅ PASS |
| 34 | ctf1 Closure Latency <= 3.5s | `<= 3500ms` | `905.84ms` | ✅ PASS |
| 35 | ctmaster Closure Latency <= 3.5s | `<= 3500ms` | `905.84ms` | ✅ PASS |
| 36 | ctf4 Closure Latency <= 3.5s | `<= 3500ms` | `934.02ms` | ✅ PASS |
| 37 | ctf5 Closure Latency <= 3.5s | `<= 3500ms` | `934.02ms` | ✅ PASS |
| 38 | ctf2 Closure Latency <= 3.5s | `<= 3500ms` | `934.02ms` | ✅ PASS |
| 39 | ctf3 Closure Latency <= 3.5s | `<= 3500ms` | `938.66ms` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Pre-Flight Order Book Verification
- **Action:** `Check 0 open orders`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms

### Step 2: Switch Followers to Balance Mode
- **Action:** `GET /user/updateCopyTradingMethod.php?method=balance`
- **Endpoint:** `https://stage.wavexone.com/user/updateCopyTradingMethod.php` () | Latency: 0.0ms

### Step 3: Capture Balances & Compute Expected Lots
- **Action:** `GET /book/balance.php`
- **Endpoint:** `https://stage.wavexone.com/book/balance.php` () | Latency: 0.0ms
- **Details:** `{"master_balance": 111221385.09, "expected_lots": {"ctf1": 0.05, "ctf2": 0.05, "ctf3": 0.05, "ctf4": 0.05, "ctf5": 0.05}}`

### Step 4: Master Place Market SELL 0.50 Lot
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `https://stage.wavexone.com/trade/placeorder.php` (POST) | Latency: 414.27ms

### Step 5: Poll Follower Order Books for Dynamic Balance SELL Replication
- **Action:** `Concurrent separate read polling /book/orders.php`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 209.82ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf2": {"order_id": "74678", "symbol": "X:BTCUSD", "side": "SELL", "lot": 0.05, "open_price": 75216.0, "sl": "---", "target": null, "latency_ms": 192.96, "raw_order": {"id": "74678", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:31:12", "trigger": "0", "type": "market", "lot": "0.05", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75216", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf5": {"order_id": "74675", "symbol": "X:BTCUSD", "side": "SELL", "lot": 0.05, "open_price": 75216.0, "sl": "---", "target": null, "latency_ms": 192.96, "raw_order": {"id": "74675", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:31:12", "trigger": "0", "type": "market", "lot": "0.05", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75216", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74679", "symbol": "X:BTCUSD", "side": "SELL", "lot": 0.05, "open_price": 75216.0, "sl": "---", "target": null, "latency_ms": 192.96, "raw_order": {"id": "74679", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:31:12", "trigger": "0", "type": "market", "lot": "0.05", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75216", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74676", "symbol": "X:BTCUSD", "side": "SELL", "lot": 0.05, "open_price": 75216.0, "sl": "---", "target": null, "latency_ms": 192.96, "raw_order": {"id": "74676", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:31:12", "trigger": "0", "type": "market", "lot": "0.05", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75216", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74677", "symbol": "X:BTCUSD", "side": "SELL", "lot": 0.05, "open_price": 75216.0, "sl": "---", "target": null, "latency_ms": 208.36, "raw_order": {"id": "74677", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:31:12", "trigger": "0", "type": "market", "lot": "0.05", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75216", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.21}`

### Step 6: Master Square-Off Position
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` (GET) | Latency: 0.0ms
- **Details:** `{"master_order_id": "74674", "response": {"status": "success", "message": "Order ID - 74674  Sent to for Closing", "data": [], "_duration_ms": 234.41}}`

### Step 7: Verify Clean Full Liquidation
- **Action:** `Poll /book/orders.php across all 6 accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctf1": 905.84, "ctmaster": 905.84, "ctf4": 934.02, "ctf5": 934.02, "ctf2": 934.02, "ctf3": 938.66}, "unclosed_accounts": [], "total_wait_sec": 0.94}`

