# Evidence Report: CT-STP-BOTH-NO-TPSL — Stop HFT BOTH WITHOUT TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.13s
- **Timestamp:** 2026-11-06 14:21:12

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH (Dual Legs) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "74981,74982", "time": 0.04567885398864746}, "_duration_ms": 241.59, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75834.50&lots=0.50&sls=&targets=&triggers=75334.50&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

