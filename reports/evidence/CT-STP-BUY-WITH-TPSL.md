# Evidence Report: CT-STP-BUY-WITH-TPSL — Stop HFT BUY WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.19s
- **Timestamp:** 2026-11-06 14:20:39

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 74958, "time": 0.03997397422790527}, "_duration_ms": 232.77, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75690.88&targetb=75990.88&triggerb=75840.88&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

