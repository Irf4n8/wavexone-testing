# Evidence Report: CT-BAL-STP-BUY-WITH-TPSL — Balance-Based Stop HFT BUY WITH TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.96s
- **Timestamp:** 2026-11-06 14:29:09

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75169, "time": 0.03963589668273926}, "_duration_ms": 269.63, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75683.22&targetb=75983.22&triggerb=75833.22&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

