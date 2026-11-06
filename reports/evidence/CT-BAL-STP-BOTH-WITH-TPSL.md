# Evidence Report: CT-BAL-STP-BOTH-WITH-TPSL — Balance-Based Stop HFT BOTH WITH TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.72s
- **Timestamp:** 2026-11-06 14:30:07

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75205,75206", "time": 0.0444788932800293}, "_duration_ms": 243.24, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75678.72&targetb=75978.72&triggerb=75828.72&lots=0.50&sls=75478.72&targets=75178.72&triggers=75328.72&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

