# Evidence Report: CT-EQU-STP-BOTH-WITH-TPSL — Equity-Based Stop HFT BOTH WITH TP/SL

- **Category:** Equity Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.65s
- **Timestamp:** 2026-11-06 14:33:14

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75301,75302", "time": 0.0483701229095459}, "_duration_ms": 249.96, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75892.62&targetb=76192.62&triggerb=76042.62&lots=0.50&sls=75692.62&targets=75392.62&triggers=75542.62&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

