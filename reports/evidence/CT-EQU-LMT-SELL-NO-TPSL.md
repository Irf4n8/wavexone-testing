# Evidence Report: CT-EQU-LMT-SELL-NO-TPSL — Equity-Based Limit SELL WITHOUT TP/SL

- **Category:** Equity Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.93s
- **Timestamp:** 2026-11-06 14:31:35

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75248, "time": 0.042881011962890625}, "_duration_ms": 237.14, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=&target=&trigger=75946.71&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

