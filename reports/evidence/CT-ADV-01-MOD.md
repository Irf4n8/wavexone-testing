# Evidence Report: CT-ADV-01-MOD — Mid-Trade Order Modification Fanout (Live SL/TP Update)

- **Category:** Trade Management
- **Status:** `PASS`
- **Execution Time:** 11.87s
- **Timestamp:** 2026-11-06 17:35:17

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Initial SL/TP Replicated on All Followers | `True` | `True` | ✅ PASS |
| 2 | ctf1 Updated SL Propagated (75692.92) | `75692.92` | `75692.92` | ✅ PASS |
| 3 | ctf1 Updated TP Propagated (77692.92) | `77692.92` | `77692.92` | ✅ PASS |
| 4 | ctf2 Updated SL Propagated (75692.92) | `75692.92` | `75692.92` | ✅ PASS |
| 5 | ctf2 Updated TP Propagated (77692.92) | `77692.92` | `77692.92` | ✅ PASS |
| 6 | ctf3 Updated SL Propagated (75692.92) | `75692.92` | `75692.92` | ✅ PASS |
| 7 | ctf3 Updated TP Propagated (77692.92) | `77692.92` | `77692.92` | ✅ PASS |
| 8 | ctf4 Updated SL Propagated (75692.92) | `75692.92` | `75692.92` | ✅ PASS |
| 9 | ctf4 Updated TP Propagated (77692.92) | `77692.92` | `77692.92` | ✅ PASS |
| 10 | ctf5 Updated SL Propagated (75692.92) | `75692.92` | `75692.92` | ✅ PASS |
| 11 | ctf5 Updated TP Propagated (77692.92) | `77692.92` | `77692.92` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Placed 0.50 BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"order_id": "77694", "sl": "75092.92", "tp": "77092.92"}`

### Step 2: Master Modified StopLoss
- **Action:** `GET /book/modify.php?id=77694&name=StopLoss&val=75692.92`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Stop Loss for ID - 77694  Updated to 75692.92", "data": [], "_duration_ms": 328.27}`

### Step 3: Master Modified Target
- **Action:** `GET /book/modify.php?id=77694&name=Target&val=77692.92`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Target for ID - 77694  Updated to 77692.92", "data": [], "_duration_ms": 307.65}`

