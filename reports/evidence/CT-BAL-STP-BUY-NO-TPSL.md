# Evidence Report: CT-BAL-STP-BUY-NO-TPSL — Balance-Based Stop HFT BUY WITHOUT TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.67s
- **Timestamp:** 2026-11-06 14:28:55

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75163, "time": 0.03634500503540039}, "_duration_ms": 270.68, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75835.15&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

