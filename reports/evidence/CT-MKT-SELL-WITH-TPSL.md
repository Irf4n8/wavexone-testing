# Evidence Report: CT-MKT-SELL-WITH-TPSL — Market SELL WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.75s
- **Timestamp:** 2026-11-06 14:19:37

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
| 8 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |
| 12 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 13 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "74916", "intentId": "56ac0172ae1d81affe1da0a5566f968e", "executionStatus": "queued", "fanoutJobId": 9420, "fanoutStatus": "queued", "requestId": "legacy_337171fadc5686881125cf92761c33b5", "placementReplayProtected": true}, "_duration_ms": 219.11, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=76371.69&target=74771.69&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

