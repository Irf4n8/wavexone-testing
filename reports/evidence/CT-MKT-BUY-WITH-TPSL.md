# Evidence Report: CT-MKT-BUY-WITH-TPSL — Market BUY WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.77s
- **Timestamp:** 2026-11-06 14:19:21

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master SL Configured | `True` | `True` | ✅ PASS |
| 2 | Master TP Configured | `True` | `True` | ✅ PASS |
| 3 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |
| 4 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 12 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 13 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "74904", "intentId": "fb15c7fddfba521183ca8d1382ba84b4", "executionStatus": "queued", "fanoutJobId": 9418, "fanoutStatus": "queued", "requestId": "legacy_6ccb7b8fab850cf240071105c552b17b", "placementReplayProtected": true}, "_duration_ms": 216.0, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=74773.49&target=76373.49&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

