# Evidence Report: CT-MUL-MKT-BUY-NO-TPSL — Multiplier Market BUY WITHOUT TP/SL

- **Category:** Multiplier Market Orders
- **Status:** `PASS`
- **Execution Time:** 6.46s
- **Timestamp:** 2026-11-06 14:24:19

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (1.50 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75002", "intentId": "154b606dd81f66c9f2727b00828538ac", "executionStatus": "queued", "fanoutJobId": 9421, "fanoutStatus": "queued", "requestId": "legacy_d47330242cb5895381a3b6a8f3357f59", "placementReplayProtected": true}, "_duration_ms": 228.01, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

