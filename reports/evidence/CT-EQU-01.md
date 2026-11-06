# Evidence Report: CT-EQU-01 — Proportional Equity-Based Copy Trading (0.50 Master Lot -> Dynamic Equity Ratio Sizing)

- **Category:** Equity-Based Copy Trading
- **Status:** `PASS`
- **Execution Time:** 7.18s
- **Timestamp:** 2026-11-06 13:00:54

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Pre-Flight Zero Open Orders | `True` | `True` | ✅ PASS |
| 2 | All Followers Switched to Equity Mode | `True` | `True` | ✅ PASS |
| 3 | ctf1 Equity Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 4 | ctf2 Equity Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 5 | ctf3 Equity Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 6 | ctf4 Equity Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 7 | ctf5 Equity Ratio Lot Calculation | `0.05` | `0.05` | ✅ PASS |
| 8 | Master Order Found in Book | `True` | `True` | ✅ PASS |
| 9 | Master Lot Size is 0.50 | `0.5` | `0.5` | ✅ PASS |
| 10 | Master Fill Price Valid | `True` | `True` | ✅ PASS |
| 11 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |
| 12 | Replicated Count == 5 | `5` | `5` | ✅ PASS |
| 13 | ctf5 Direction is BUY | `BUY` | `BUY` | ✅ PASS |
| 14 | ctf5 Equity Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 15 | ctf5 Replication Latency <= 2.5s | `<= 2500ms` | `185.06ms` | ✅ PASS |
| 16 | ctf5 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.7 pts` | ✅ PASS |
| 17 | ctf1 Direction is BUY | `BUY` | `BUY` | ✅ PASS |
| 18 | ctf1 Equity Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 19 | ctf1 Replication Latency <= 2.5s | `<= 2500ms` | `185.06ms` | ✅ PASS |
| 20 | ctf1 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.7 pts` | ✅ PASS |
| 21 | ctf4 Direction is BUY | `BUY` | `BUY` | ✅ PASS |
| 22 | ctf4 Equity Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 23 | ctf4 Replication Latency <= 2.5s | `<= 2500ms` | `185.06ms` | ✅ PASS |
| 24 | ctf4 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.7 pts` | ✅ PASS |
| 25 | ctf2 Direction is BUY | `BUY` | `BUY` | ✅ PASS |
| 26 | ctf2 Equity Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 27 | ctf2 Replication Latency <= 2.5s | `<= 2500ms` | `185.06ms` | ✅ PASS |
| 28 | ctf2 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.7 pts` | ✅ PASS |
| 29 | ctf3 Direction is BUY | `BUY` | `BUY` | ✅ PASS |
| 30 | ctf3 Equity Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 31 | ctf3 Replication Latency <= 2.5s | `<= 2500ms` | `202.25ms` | ✅ PASS |
| 32 | ctf3 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.7 pts` | ✅ PASS |
| 33 | All Positions Cleanly Liquidated | `True` | `True` | ✅ PASS |
| 34 | ctf1 Closure Latency <= 3.5s | `<= 3500ms` | `906.92ms` | ✅ PASS |
| 35 | ctf2 Closure Latency <= 3.5s | `<= 3500ms` | `906.92ms` | ✅ PASS |
| 36 | ctmaster Closure Latency <= 3.5s | `<= 3500ms` | `906.92ms` | ✅ PASS |
| 37 | ctf5 Closure Latency <= 3.5s | `<= 3500ms` | `922.72ms` | ✅ PASS |
| 38 | ctf4 Closure Latency <= 3.5s | `<= 3500ms` | `922.72ms` | ✅ PASS |
| 39 | ctf3 Closure Latency <= 3.5s | `<= 3500ms` | `938.57ms` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Pre-Flight Order Book Verification
- **Action:** `Check 0 open orders`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms

### Step 2: Switch Followers to Equity Mode
- **Action:** `GET /user/updateCopyTradingMethod.php?method=equity`
- **Endpoint:** `https://stage.wavexone.com/user/updateCopyTradingMethod.php` () | Latency: 0.0ms

### Step 3: Capture Equities & Compute Expected Lots
- **Action:** `GET /book/balance.php`
- **Endpoint:** `https://stage.wavexone.com/book/balance.php` () | Latency: 0.0ms
- **Details:** `{"master_equity": 111221391.1, "expected_lots": {"ctf1": 0.05, "ctf2": 0.05, "ctf3": 0.05, "ctf4": 0.05, "ctf5": 0.05}}`

### Step 4: Master Place Market BUY 0.50 Lot
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `https://stage.wavexone.com/trade/placeorder.php` (POST) | Latency: 408.57ms

### Step 5: Poll Follower Order Books for Dynamic Equity Replication
- **Action:** `Concurrent separate read polling /book/orders.php`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 215.8ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf5": {"order_id": "74669", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75232.7, "sl": "---", "target": null, "latency_ms": 185.06, "raw_order": {"id": "74669", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:59", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75232.7", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74673", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75232.7, "sl": "---", "target": null, "latency_ms": 185.06, "raw_order": {"id": "74673", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:59", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75232.7", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74670", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75232.7, "sl": "---", "target": null, "latency_ms": 185.06, "raw_order": {"id": "74670", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:59", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75232.7", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf2": {"order_id": "74672", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75232.7, "sl": "---", "target": null, "latency_ms": 185.06, "raw_order": {"id": "74672", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:59", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75232.7", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74671", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75232.7, "sl": "---", "target": null, "latency_ms": 202.25, "raw_order": {"id": "74671", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:59", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75232.7", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.22}`

### Step 6: Master Square-Off Position
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` (GET) | Latency: 0.0ms
- **Details:** `{"master_order_id": "74668", "response": {"status": "success", "message": "Order ID - 74668  Sent to for Closing", "data": [], "_duration_ms": 234.63}}`

### Step 7: Verify Clean Full Liquidation
- **Action:** `Poll /book/orders.php across all 6 accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctf1": 906.92, "ctf2": 906.92, "ctmaster": 906.92, "ctf5": 922.72, "ctf4": 922.72, "ctf3": 938.57}, "unclosed_accounts": [], "total_wait_sec": 0.94}`

