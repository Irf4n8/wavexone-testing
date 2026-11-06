# Evidence Report: CT-LMT-BUY-NO-TPSL — Limit BUY WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.52s
- **Timestamp:** 2026-11-06 14:19:45

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74927, "time": 0.04168581962585449}, "_duration_ms": 234.86, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=&target=&trigger=75319.27&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

