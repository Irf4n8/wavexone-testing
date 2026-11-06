# Evidence Report: CT-LMT-BUY-WITH-TPSL — Limit BUY WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.47s
- **Timestamp:** 2026-11-06 14:19:56

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74933, "time": 0.04392504692077637}, "_duration_ms": 236.92, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=75144.31&target=75544.31&trigger=75344.31&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

