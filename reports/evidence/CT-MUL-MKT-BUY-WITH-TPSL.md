# Evidence Report: CT-MUL-MKT-BUY-WITH-TPSL — Multiplier Market BUY WITH TP/SL

- **Category:** Multiplier Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.34s
- **Timestamp:** 2026-11-06 14:24:31

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (1.50 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75010", "intentId": "86ba989366616ee92f8c36b87e8cbcb6", "executionStatus": "queued", "fanoutJobId": 9423, "fanoutStatus": "queued", "requestId": "legacy_66230674ae395780a41a271d0a90ff97", "placementReplayProtected": true}, "_duration_ms": 220.22, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=74831.71&target=76431.71&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

