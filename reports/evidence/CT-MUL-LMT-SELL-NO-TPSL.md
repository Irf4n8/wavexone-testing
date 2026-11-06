# Evidence Report: CT-MUL-LMT-SELL-NO-TPSL — Multiplier Limit SELL WITHOUT TP/SL

- **Category:** Multiplier Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.51s
- **Timestamp:** 2026-11-06 14:25:28

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75045, "time": 0.038017988204956055}, "_duration_ms": 250.32, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=&target=&trigger=75857.57&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

