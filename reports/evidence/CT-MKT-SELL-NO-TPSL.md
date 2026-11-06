# Evidence Report: CT-MKT-SELL-NO-TPSL — Market SELL WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.38s
- **Timestamp:** 2026-11-06 14:19:29

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master SL Empty (Without TP/SL) | `True` | `True` | ✅ PASS |
| 2 | All 5 Followers Replicated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "74910", "intentId": "e6783496c448a91c2a85de74388819fa", "executionStatus": "queued", "fanoutJobId": 9419, "fanoutStatus": "queued", "requestId": "legacy_5044abee5f74b8289cf563d066208a7d", "placementReplayProtected": true}, "_duration_ms": 235.44, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=&target=&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

