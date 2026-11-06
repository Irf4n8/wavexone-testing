# Evidence Report: CT-MKT-BUY-NO-TPSL — Market BUY WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.47s
- **Timestamp:** 2026-11-06 14:19:12

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master SL Empty (Without TP/SL) | `True` | `True` | ✅ PASS |
| 2 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "74898", "intentId": "ed6f97c30b2400032d19213a4a728936", "executionStatus": "queued", "fanoutJobId": 9417, "fanoutStatus": "queued", "requestId": "legacy_53db44698629fc746c389535ea604c84", "placementReplayProtected": true}, "_duration_ms": 218.74, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

