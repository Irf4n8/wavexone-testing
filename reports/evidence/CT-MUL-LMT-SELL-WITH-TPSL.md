# Evidence Report: CT-MUL-LMT-SELL-WITH-TPSL — Multiplier Limit SELL WITH TP/SL

- **Category:** Multiplier Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.63s
- **Timestamp:** 2026-11-06 14:25:42

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75051, "time": 0.04310488700866699}, "_duration_ms": 254.61, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=76083.08&target=75683.08&trigger=75883.08&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

