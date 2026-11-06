# Evidence Report: CT-MUL-MKT-SELL-NO-TPSL — Multiplier Market SELL WITHOUT TP/SL

- **Category:** Multiplier Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.51s
- **Timestamp:** 2026-11-06 14:24:41

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (1.50 Lots) | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75016", "intentId": "d9ec835a245fadd9956242767a6062bb", "executionStatus": "queued", "fanoutJobId": 9424, "fanoutStatus": "queued", "requestId": "legacy_97b1492b0b492819822ce49aa4f60289", "placementReplayProtected": true}, "_duration_ms": 217.53, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

