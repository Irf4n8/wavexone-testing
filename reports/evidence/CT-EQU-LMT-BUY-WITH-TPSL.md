# Evidence Report: CT-EQU-LMT-BUY-WITH-TPSL — Equity-Based Limit BUY WITH TP/SL

- **Category:** Equity Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.91s
- **Timestamp:** 2026-11-06 14:31:21

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75242, "time": 0.04217100143432617}, "_duration_ms": 243.99, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=75244.44&target=75644.44&trigger=75444.44&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

