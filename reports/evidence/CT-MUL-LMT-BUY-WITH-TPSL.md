# Evidence Report: CT-MUL-LMT-BUY-WITH-TPSL — Multiplier Limit BUY WITH TP/SL

- **Category:** Multiplier Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.7s
- **Timestamp:** 2026-11-06 14:25:15

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75039, "time": 0.040329933166503906}, "_duration_ms": 233.52, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=75162.72&target=75562.72&trigger=75362.72&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

