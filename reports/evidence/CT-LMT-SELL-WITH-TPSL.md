# Evidence Report: CT-LMT-SELL-WITH-TPSL — Limit SELL WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.44s
- **Timestamp:** 2026-11-06 14:20:17

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74945, "time": 0.04263710975646973}, "_duration_ms": 233.08, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=76015.11&target=75615.11&trigger=75815.11&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

