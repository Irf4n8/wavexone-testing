# Evidence Report: CT-EQU-STP-BOTH-NO-TPSL — Equity-Based Stop HFT BOTH WITHOUT TP/SL

- **Category:** Equity Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.53s
- **Timestamp:** 2026-11-06 14:32:59

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75289,75290", "time": 0.05303692817687988}, "_duration_ms": 293.98, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75968.58&lots=0.50&sls=&targets=&triggers=75468.58&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

