# Evidence Report: CT-EQU-MKT-SELL-NO-TPSL — Equity-Based Market SELL WITHOUT TP/SL

- **Category:** Equity Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.89s
- **Timestamp:** 2026-11-06 14:30:44

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75219", "intentId": "22d0c13e2f514d6c20c3057fd2054235", "executionStatus": "queued", "fanoutJobId": 9434, "fanoutStatus": "queued", "requestId": "legacy_6c9c156a1c97ca150395b8cc717d90ec", "placementReplayProtected": true}, "_duration_ms": 222.75, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

