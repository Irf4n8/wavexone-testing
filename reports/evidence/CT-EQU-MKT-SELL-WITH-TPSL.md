# Evidence Report: CT-EQU-MKT-SELL-WITH-TPSL — Equity-Based Market SELL WITH TP/SL

- **Category:** Equity Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.98s
- **Timestamp:** 2026-11-06 14:30:55

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75225", "intentId": "949c66d28c698659ef864b3f530f3913", "executionStatus": "queued", "fanoutJobId": 9435, "fanoutStatus": "queued", "requestId": "legacy_96b0571d45a9a17fae1ffc7483fadb6b", "placementReplayProtected": true}, "_duration_ms": 221.44, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=76435.34&target=74835.34&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

