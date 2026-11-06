# Evidence Report: CT-STP-BUY-NO-TPSL — Stop HFT BUY WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.12s
- **Timestamp:** 2026-11-06 14:20:28

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74952, "time": 0.04553103446960449}, "_duration_ms": 253.86, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75806.46&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

