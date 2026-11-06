# Evidence Report: CT-STATEFUL-01 — Copy Trading Finite State Machine (FSM) Lifecycle & Invariant Validation

- **Category:** Stateful Automation
- **Status:** `PASS`
- **Execution Time:** 15.86s
- **Timestamp:** 2026-11-06 13:08:52

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | State 0: Zero Open Positions | `True` | `True` | ✅ PASS |
| 2 | State 1: Heterogeneous Config Persisted | `True` | `True` | ✅ PASS |
| 3 | State 2: All 5 Heterogeneous Followers Replicated | `True` | `True` | ✅ PASS |
| 4 | State 2: ctf2 (mode) lot == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 5 | State 2: ctf5 (mode) lot == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 6 | State 2: ctf3 (mode) lot == 0.05 | `0.05` | `0.05` | ✅ PASS |
| 7 | State 2: ctf4 (mode) lot == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 8 | State 2: ctf1 (mode) lot == 1.50 | `1.5` | `1.5` | ✅ PASS |
| 9 | State 2 Invariant: Total Ecosystem Open Orders == 6 | `6` | `6` | ✅ PASS |
| 10 | State 3: ctf1 Order Closed in Own Book | `True` | `True` | ✅ PASS |
| 11 | State 3 Invariant: Master Order Remains Active | `True` | `True` | ✅ PASS |
| 12 | State 3 Invariant: Peer ctf2 Remains Active | `True` | `True` | ✅ PASS |
| 13 | State 3 Invariant: Peer ctf3 Remains Active | `True` | `True` | ✅ PASS |
| 14 | State 3 Invariant: Peer ctf4 Remains Active | `True` | `True` | ✅ PASS |
| 15 | State 3 Invariant: Peer ctf5 Remains Active | `True` | `True` | ✅ PASS |
| 16 | State 4: Unfollow API Succeeded | `success` | `success` | ✅ PASS |
| 17 | State 5 Invariant: All Positions Cleanly Liquidated | `True` | `True` | ✅ PASS |
| 18 | State 6 Invariant: All 5 Followers Replicated SELL 1.50 Lots | `True` | `True` | ✅ PASS |
| 19 | State 7 Invariant: Final Clean Slate Verified | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: STATE_0: Assert Clean Slate
- **Action:** `Query /book/orders.php across all 6 accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms
- **Details:** `{"status": "clean", "pre_existing_orders": {}}`

### Step 2: STATE_1: Heterogeneous Mode Assignment
- **Action:** `Set ctf1=3x, ctf2=bal, ctf3=eq, ctf4=3x, ctf5=bal`
- **Endpoint:** `https://stage.wavexone.com/user/updateCopyTradingMethod.php` () | Latency: 0.0ms
- **Details:** `{"expected_lots": {"ctf1": 1.5, "ctf2": 0.05, "ctf3": 0.05, "ctf4": 1.5, "ctf5": 0.05}}`

### Step 3: STATE_2: Master Place Market BUY 0.50 Lot
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `https://stage.wavexone.com/trade/placeorder.php` (POST) | Latency: 0.0ms

### Step 4: STATE_2: Multi-Mode Replications Captured
- **Action:** `Poll /book/orders.php`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf2": {"order_id": "74697", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75338.5, "sl": "---", "target": null, "latency_ms": 189.54, "raw_order": {"id": "74697", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:38:56", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75338.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf5": {"order_id": "74699", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75338.5, "sl": "---", "target": null, "latency_ms": 194.32, "raw_order": {"id": "74699", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:38:56", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75338.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74696", "symbol": "X:BTCUSD", "side": "BUY", "lot": 0.05, "open_price": 75338.5, "sl": "---", "target": null, "latency_ms": 216.78, "raw_order": {"id": "74696", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:38:56", "trigger": "0", "type": "market", "lot": "0.05", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75338.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74695", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75340.1, "sl": "---", "target": null, "latency_ms": 216.78, "raw_order": {"id": "74695", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:38:56", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75340.1", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74698", "symbol": "X:BTCUSD", "side": "BUY", "lot": 1.5, "open_price": 75340.1, "sl": "---", "target": null, "latency_ms": 217.84, "raw_order": {"id": "74698", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:38:56", "trigger": "0", "type": "market", "lot": "1.5", "bs": "BUY", "sl": "---", "tp": "---", "avg": "75340.1", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.22}`

### Step 5: STATE_3: Follower ctf1 Manual Close
- **Action:** `GET /book/squareoff.php (Follower Peer Exit)`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` () | Latency: 0.0ms
- **Details:** `{"order_id": "74698", "response": {"status": "success", "message": "Order ID - 74698  Sent to for Closing", "data": [], "_duration_ms": 211.37}}`

### Step 6: STATE_4: ctf5 Unfollows Master While Trade Open
- **Action:** `GET /user/follow.php?type=unfollow`
- **Endpoint:** `https://stage.wavexone.com/user/follow.php` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Successfully unfollowed to this user", "data": []}`

### Step 7: STATE_5: Master Square-Off (Fanout Trigger)
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` () | Latency: 0.0ms
- **Details:** `{"master_order_id": "74694", "response": {"status": "success", "message": "Order ID - 74694  Sent to for Closing", "data": [], "_duration_ms": 238.7}}`

### Step 8: STATE_5: Fanout Closure Verification
- **Action:** `Poll /book/orders.php across all accounts`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctf5": 189.2, "ctf1": 215.32, "ctf2": 880.45, "ctf3": 896.21, "ctf4": 896.21, "ctmaster": 896.21}, "unclosed_accounts": [], "total_wait_sec": 0.91}`

### Step 9: STATE_6: ctf5 Re-Follows Master
- **Action:** `GET /user/follow.php?type=follow`
- **Endpoint:** `https://stage.wavexone.com/user/follow.php` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Successfully followed this user. Master profit share: 10.00%", "data": {"profit_share": 10}}`

### Step 10: STATE_6: SELL Replication After Re-Follow
- **Action:** `Poll /book/orders.php for SELL 1.50 lots`
- **Endpoint:** `https://stage.wavexone.com/book/orders.php` () | Latency: 0.0ms
- **Details:** `{"all_replicated": true, "replicated_count": 5, "expected_count": 5, "replicated_orders": {"ctf2": {"order_id": "74703", "symbol": "X:BTCUSD", "side": "SELL", "lot": 1.5, "open_price": 75315.5, "sl": "---", "target": null, "latency_ms": 216.16, "raw_order": {"id": "74703", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:39:05", "trigger": "0", "type": "market", "lot": "1.5", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75315.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf5": {"order_id": "74705", "symbol": "X:BTCUSD", "side": "SELL", "lot": 1.5, "open_price": 75315.5, "sl": "---", "target": null, "latency_ms": 216.16, "raw_order": {"id": "74705", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:39:05", "trigger": "0", "type": "market", "lot": "1.5", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75315.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf3": {"order_id": "74702", "symbol": "X:BTCUSD", "side": "SELL", "lot": 1.5, "open_price": 75315.5, "sl": "---", "target": null, "latency_ms": 240.07, "raw_order": {"id": "74702", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:39:05", "trigger": "0", "type": "market", "lot": "1.5", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75315.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf1": {"order_id": "74704", "symbol": "X:BTCUSD", "side": "SELL", "lot": 1.5, "open_price": 75315.5, "sl": "---", "target": null, "latency_ms": 243.29, "raw_order": {"id": "74704", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:39:05", "trigger": "0", "type": "market", "lot": "1.5", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75315.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}, "ctf4": {"order_id": "74701", "symbol": "X:BTCUSD", "side": "SELL", "lot": 1.5, "open_price": 75315.5, "sl": "---", "target": null, "latency_ms": 243.29, "raw_order": {"id": "74701", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-06 07:39:05", "trigger": "0", "type": "market", "lot": "1.5", "bs": "SELL", "sl": "---", "tp": "---", "avg": "75315.5", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}}}, "missing_followers": [], "total_wait_sec": 0.24}`

### Step 11: STATE_7: Final Master Square-Off
- **Action:** `GET /book/squareoff.php`
- **Endpoint:** `https://stage.wavexone.com/book/squareoff.php` () | Latency: 0.0ms
- **Details:** `{"all_closed": true, "closed_latencies_ms": {"ctf2": 908.09, "ctf3": 925.87, "ctmaster": 925.87, "ctf4": 925.87, "ctf5": 1635.66, "ctf1": 1663.69}, "unclosed_accounts": [], "total_wait_sec": 1.66}`

### Step 12: FSM Traversal Complete
- **Action:** `State History Recorded`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"traversed_states": ["STATE_0_IDLE_CLEAN_SLATE", "STATE_1_HETEROGENEOUS_CONFIGURATION", "STATE_2_MASTER_BUY_OPEN", "STATE_3_PEER_ISOLATION_EXIT", "STATE_4_UNFOLLOW_IN_FLIGHT", "STATE_5_MASTER_SQUAREOFF_FANOUT", "STATE_6_RE_FOLLOW_AND_SELL_OPEN", "STATE_7_FINAL_SQUAREOFF_AND_BASELINE"], "final_state": "STATE_7_FINAL_SQUAREOFF_AND_BASELINE"}`

