# Evidence Report: CT-BAL-LMT-SELL-WITH-TPSL — Balance-Based Limit SELL WITH TP/SL

- **Category:** Balance Limit Orders
- **Status:** `PASS`
- **Execution Time:** 8.1s
- **Timestamp:** 2026-11-06 14:28:41

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75157, "time": 0.047165870666503906}, "_duration_ms": 254.66, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=76049.58&target=75649.58&trigger=75849.58&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

