# Evidence Report: CT-EQU-MKT-BUY-NO-TPSL — Equity-Based Market BUY WITHOUT TP/SL

- **Category:** Equity Market Orders
- **Status:** `PASS`
- **Execution Time:** 5.03s
- **Timestamp:** 2026-11-06 14:30:22

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75207", "intentId": "551a4dc71a3d5b9b246b21d6c6f07bf5", "executionStatus": "queued", "fanoutJobId": 9432, "fanoutStatus": "queued", "requestId": "legacy_e45a398bbecba1e5a3a34eb0e3232411", "placementReplayProtected": true}, "_duration_ms": 221.53, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

