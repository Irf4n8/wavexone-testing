# Evidence Report: CT-BAL-LMT-BUY-WITH-TPSL — Balance-Based Limit BUY WITH TP/SL

- **Category:** Balance Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.99s
- **Timestamp:** 2026-11-06 14:28:13

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75145, "time": 0.0386199951171875}, "_duration_ms": 261.09, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=75151.10&target=75551.10&trigger=75351.10&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

