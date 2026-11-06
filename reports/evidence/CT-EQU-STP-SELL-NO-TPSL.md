# Evidence Report: CT-EQU-STP-SELL-NO-TPSL — Equity-Based Stop HFT SELL WITHOUT TP/SL

- **Category:** Equity Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.53s
- **Timestamp:** 2026-11-06 14:32:31

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75272, "time": 0.05045580863952637}, "_duration_ms": 249.98, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=&targets=&triggers=75459.35&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

