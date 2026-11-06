# Evidence Report: CT-MUL-01 — Multiplier 3.0x Proportional Replication (0.50 Master Lot -> 1.50 Follower Lots)

- **Category:** Multiplier Copy Trading
- **Status:** `PASS`
- **Execution Time:** 5.26s
- **Timestamp:** 2026-11-06 13:00:27

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Pre-Flight Zero Open Orders | `True` | `True` | ✅ PASS |
| 2 | Master Order Found in Book | `True` | `True` | ✅ PASS |
| 3 | Master Lot Size is 0.50 | `0.5` | `0.5` | ✅ PASS |
| 4 | Master Fill Price Valid | `True` | `True` | ✅ PASS |
| 5 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |
| 6 | Replicated Count == 5 | `5` | `5` | ✅ PASS |
| 7 | ctf2 Lot Size == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 8 | ctf2 Replication Latency <= 2.5s | `<= 2500ms` | `210.44ms` | ✅ PASS |
| 9 | ctf2 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `2.5 pts` | ✅ PASS |
| 10 | ctf1 Lot Size == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 11 | ctf1 Replication Latency <= 2.5s | `<= 2500ms` | `210.44ms` | ✅ PASS |
| 12 | ctf1 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `2.5 pts` | ✅ PASS |
| 13 | ctf5 Lot Size == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 14 | ctf5 Replication Latency <= 2.5s | `<= 2500ms` | `210.44ms` | ✅ PASS |
| 15 | ctf5 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `5.5 pts` | ✅ PASS |
| 16 | ctf4 Lot Size == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 17 | ctf4 Replication Latency <= 2.5s | `<= 2500ms` | `210.44ms` | ✅ PASS |
| 18 | ctf4 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `5.5 pts` | ✅ PASS |
| 19 | ctf3 Lot Size == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 20 | ctf3 Replication Latency <= 2.5s | `<= 2500ms` | `223.94ms` | ✅ PASS |
| 21 | ctf3 Price Spread Markup Buffer Valid | `<= 12.0 pts` | `2.5 pts` | ✅ PASS |
| 22 | All Positions Cleanly Liquidated | `True` | `True` | ✅ PASS |
| 23 | ctf5 Closure Latency <= 3.5s | `<= 3500ms` | `918.69ms` | ✅ PASS |
| 24 | ctf4 Closure Latency <= 3.5s | `<= 3500ms` | `918.69ms` | ✅ PASS |
| 25 | ctmaster Closure Latency <= 3.5s | `<= 3500ms` | `929.79ms` | ✅ PASS |
| 26 | ctf2 Closure Latency <= 3.5s | `<= 3500ms` | `929.79ms` | ✅ PASS |
| 27 | ctf3 Closure Latency <= 3.5s | `<= 3500ms` | `940.17ms` | ✅ PASS |
| 28 | ctf1 Closure Latency <= 3.5s | `<= 3500ms` | `1628.56ms` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Pre-Flight Order Book Verification
- **Action:** `Check 0 open orders`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms

### Step 2: Master Place Market BUY 0.50 Lot
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `https://stage.wavexone.com/trade/placeorder.php` (POST) | Latency: 420.31ms

### Step 3: Poll Follower Order Books for 1.50 Lot Replication
- **Action:** `Concurrent separate read polling /book/orders.php`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 225.0ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf2": {"order_id": "74660", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75268.2, "sl": "---", "target": null, "latency_ms": 210.44, "raw_order": {"id": "74660", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:30", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75268.2", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74661", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75268.2, "sl": "---", "target": null, "latency_ms": 210.44, "raw_order": {"id": "74661", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:30", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75268.2", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf5": {"order_id": "74657", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75271.2, "sl": "---", "target": null, "latency_ms": 210.44, "raw_order": {"id": "74657", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:30", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75271.2", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74658", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75271.2, "sl": "---", "target": null, "latency_ms": 210.44, "raw_order": {"id": "74658", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:30", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75271.2", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74659", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75268.2, "sl": "---", "target": null, "latency_ms": 223.94, "raw_order": {"id": "74659", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:30:30", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75268.2", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.22}`

### Step 4: Master Square-Off Position
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` (GET) | Latency: 0.0ms
- **Details:** `{"master_order_id": "74656", "response": {"status": "success", "message": "Order ID - 74656  Sent to for Closing", "data": [], "_duration_ms": 237.91}}`

### Step 5: Verify Clean Full Liquidation
- **Action:** `Poll /book/orders.php across all 6 accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` (GET) | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctf5": 918.69, "ctf4": 918.69, "ctmaster": 929.79, "ctf2": 929.79, "ctf3": 940.17, "ctf1": 1628.56}, "unclosed_accounts": [], "total_wait_sec": 1.63}`

