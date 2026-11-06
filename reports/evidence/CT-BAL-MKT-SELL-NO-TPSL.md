# Evidence Report: CT-BAL-MKT-SELL-NO-TPSL — Balance-Based Market SELL WITHOUT TP/SL

- **Category:** Balance Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.87s
- **Timestamp:** 2026-11-06 14:27:38

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75116", "intentId": "cd8f2b3c337a93ce8b9201f35b1f8acb", "executionStatus": "queued", "fanoutJobId": 9429, "fanoutStatus": "queued", "requestId": "legacy_035ecf0bf0b8ab678010ed00bc4179bf", "placementReplayProtected": true}, "_duration_ms": 290.4, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

