# Evidence Report: CT-EQU-LMT-BUY-NO-TPSL — Equity-Based Limit BUY WITHOUT TP/SL

- **Category:** Equity Limit Orders
- **Status:** `PASS`
- **Execution Time:** 8.22s
- **Timestamp:** 2026-11-06 14:31:07

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75236, "time": 0.04153704643249512}, "_duration_ms": 286.41, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=&target=&trigger=75421.06&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

