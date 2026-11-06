# Evidence Report: CT-STP-SELL-WITH-TPSL — Stop HFT SELL WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.08s
- **Timestamp:** 2026-11-06 14:21:01

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74970, "time": 0.04164385795593262}, "_duration_ms": 226.53, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=75504.47&targets=75204.47&triggers=75354.47&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

