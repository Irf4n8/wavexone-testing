# Evidence Report: CT-BAL-STP-SELL-WITH-TPSL — Balance-Based Stop HFT SELL WITH TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.58s
- **Timestamp:** 2026-11-06 14:29:39

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75181, "time": 0.0395660400390625}, "_duration_ms": 266.61, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=75481.36&targets=75181.36&triggers=75331.36&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

