# Evidence Report: CT-STP-BOTH-WITH-TPSL — Stop HFT BOTH WITH TP/SL (0.50 Master -> 1.50 Follower)

- **Category:** Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.14s
- **Timestamp:** 2026-11-06 14:21:23

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH (Dual Legs) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "74994,74995", "time": 0.042562007904052734}, "_duration_ms": 238.94, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75715.95&targetb=76015.95&triggerb=75865.95&lots=0.50&sls=75515.95&targets=75215.95&triggers=75365.95&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

