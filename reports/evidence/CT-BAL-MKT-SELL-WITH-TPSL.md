# Evidence Report: CT-BAL-MKT-SELL-WITH-TPSL — Balance-Based Market SELL WITH TP/SL

- **Category:** Balance Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.69s
- **Timestamp:** 2026-11-06 14:27:49

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75128", "intentId": "e0a6b2aab1a90bc632d1a5a5740977cd", "executionStatus": "queued", "fanoutJobId": 9431, "fanoutStatus": "queued", "requestId": "legacy_b7965e89215d4934306f9132139eceaa", "placementReplayProtected": true}, "_duration_ms": 232.89, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=76413.74&target=74813.74&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

