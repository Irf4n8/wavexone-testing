# Evidence Report: CT-BAL-LMT-SELL-NO-TPSL — Balance-Based Limit SELL WITHOUT TP/SL

- **Category:** Balance Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.85s
- **Timestamp:** 2026-11-06 14:28:27

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75151, "time": 0.044686079025268555}, "_duration_ms": 237.43, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=&target=&trigger=75852.69&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

