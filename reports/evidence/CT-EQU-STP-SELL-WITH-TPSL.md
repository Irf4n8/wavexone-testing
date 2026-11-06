# Evidence Report: CT-EQU-STP-SELL-WITH-TPSL — Equity-Based Stop HFT SELL WITH TP/SL

- **Category:** Equity Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.67s
- **Timestamp:** 2026-11-06 14:32:45

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75278, "time": 0.040925025939941406}, "_duration_ms": 327.51, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=75623.22&targets=75323.22&triggers=75473.22&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

