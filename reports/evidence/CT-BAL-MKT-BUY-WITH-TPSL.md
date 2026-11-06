# Evidence Report: CT-BAL-MKT-BUY-WITH-TPSL — Balance-Based Market BUY WITH TP/SL

- **Category:** Balance Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.58s
- **Timestamp:** 2026-11-06 14:27:28

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75110", "intentId": "d97788898d59c3f305954bf0b25db410", "executionStatus": "queued", "fanoutJobId": 9428, "fanoutStatus": "queued", "requestId": "legacy_fcb07a28c35c4bde998339bcf8eea328", "placementReplayProtected": true}, "_duration_ms": 220.41, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=74808.92&target=76408.92&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

