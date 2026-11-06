# Evidence Report: CT-BAL-MKT-BUY-NO-TPSL — Balance-Based Market BUY WITHOUT TP/SL

- **Category:** Balance Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.81s
- **Timestamp:** 2026-11-06 14:27:17

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75104", "intentId": "6126ec6a1cccb119c4792b1111d28466", "executionStatus": "queued", "fanoutJobId": 9427, "fanoutStatus": "queued", "requestId": "legacy_e621014b72d2f783fa0fb9438a3e97ef", "placementReplayProtected": true}, "_duration_ms": 326.47, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

