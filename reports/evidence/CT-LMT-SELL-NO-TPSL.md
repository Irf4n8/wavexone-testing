# Evidence Report: CT-LMT-SELL-NO-TPSL — Limit SELL WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.48s
- **Timestamp:** 2026-11-06 14:20:06

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74939, "time": 0.0450129508972168}, "_duration_ms": 237.78, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=&target=&trigger=75842.26&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

