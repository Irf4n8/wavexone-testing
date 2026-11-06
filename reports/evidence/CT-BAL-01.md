# Evidence Report: CT-BAL-01 — Proportional Balance-Based Copy Trading (0.50 Master Lot -> Dynamic Balance Ratio Sizing)

- **Category:** Balance-Based Copy Trading
- **Status:** `PASS`
- **Execution Time:** 7.04s
- **Timestamp:** 2026-11-06 13:00:39

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
| 13 | ctf2 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 14 | ctf2 Replication Latency <= 2.5s | `<= 2500ms` | `202.03ms` | ✅ PASS |
| 15 | ctf2 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `1.0 pts` | ✅ PASS |
| 16 | ctf1 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 17 | ctf1 Replication Latency <= 2.5s | `<= 2500ms` | `202.03ms` | ✅ PASS |
| 18 | ctf1 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.2 pts` | ✅ PASS |
| 19 | ctf4 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 20 | ctf4 Replication Latency <= 2.5s | `<= 2500ms` | `203.26ms` | ✅ PASS |
| 21 | ctf4 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.2 pts` | ✅ PASS |
| 22 | ctf5 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 23 | ctf5 Replication Latency <= 2.5s | `<= 2500ms` | `203.26ms` | ✅ PASS |
| 24 | ctf5 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `1.0 pts` | ✅ PASS |
| 25 | ctf3 Balance Mode Lot Size == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 26 | ctf3 Replication Latency <= 2.5s | `<= 2500ms` | `218.62ms` | ✅ PASS |
| 27 | ctf3 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `0.2 pts` | ✅ PASS |
| 28 | All Positions Cleanly Liquidated | `True` | `True` | ✅ PASS |
| 29 | ctmaster Closure Latency <= 3.5s | `<= 3500ms` | `923.33ms` | ✅ PASS |
| 30 | ctf5 Closure Latency <= 3.5s | `<= 3500ms` | `924.35ms` | ✅ PASS |
| 31 | ctf4 Closure Latency <= 3.5s | `<= 3500ms` | `924.35ms` | ✅ PASS |
| 32 | ctf1 Closure Latency <= 3.5s | `<= 3500ms` | `924.35ms` | ✅ PASS |
| 33 | ctf2 Closure Latency <= 3.5s | `<= 3500ms` | `924.35ms` | ✅ PASS |
| 34 | ctf3 Closure Latency <= 3.5s | `<= 3500ms` | `948.51ms` | ✅ PASS |

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
- **Details:** `{"master_balance": 111221391.58, "expected_lots": {"ctf1": 0.05, "ctf2": 0.05, "ctf3": 0.05, "ctf4": 0.05, "ctf5": 0.05}}`

### Step 4: Master Place Market BUY 0.50 Lot
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `https://stage.wavexone.com/trade/placeorder.php` (POST) | Latency: 412.1ms

### Step 5: Poll Follower Order Books for Dynamic Balance Replication
- **Action:** `Concurrent separate read polling /book/orders.php`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 219.76ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf2": {"order_id": "74666", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75207.1, "sl": "---", "target": null, "latency_ms": 202.03, "raw_order": {"id": "74666", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:44", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75207.1", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74667", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75206.3, "sl": "---", "target": null, "latency_ms": 202.03, "raw_order": {"id": "74667", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:44", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75206.3", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74664", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75206.3, "sl": "---", "target": null, "latency_ms": 203.26, "raw_order": {"id": "74664", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:44", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75206.3", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf5": {"order_id": "74663", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75207.1, "sl": "---", "target": null, "latency_ms": 203.26, "raw_order": {"id": "74663", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:44", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75207.1", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74665", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75206.3, "sl": "---", "target": null, "latency_ms": 218.62, "raw_order": {"id": "74665", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:44", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75206.3", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.22}`

### Step 6: Master Square-Off Position
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` (GET) | Latency: 0.0ms
- **Details:** `{"master_order_id": "74662", "response": {"status": "success", "message": "Order ID - 74662  Sent to for Closing", "data": [], "_duration_ms": 230.72}}`

### Step 7: Verify Clean Full Liquidation
- **Action:** `Poll /book/orders.php across all 6 accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctmaster": 923.33, "ctf5": 924.35, "ctf4": 924.35, "ctf1": 924.35, "ctf2": 924.35, "ctf3": 948.51}, "unclosed_accounts": [], "total_wait_sec": 0.95}`

