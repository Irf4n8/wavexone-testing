# Evidence Report: CT-EQU-STP-BUY-WITH-TPSL — Equity-Based Stop HFT BUY WITH TP/SL

- **Category:** Equity Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.53s
- **Timestamp:** 2026-11-06 14:32:17

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75266, "time": 0.03876495361328125}, "_duration_ms": 242.44, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75795.12&targetb=76095.12&triggerb=75945.12&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

