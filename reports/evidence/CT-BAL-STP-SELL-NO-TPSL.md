# Evidence Report: CT-BAL-STP-SELL-NO-TPSL — Balance-Based Stop HFT SELL WITHOUT TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.69s
- **Timestamp:** 2026-11-06 14:29:24

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75175, "time": 0.04235196113586426}, "_duration_ms": 292.8, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=&targets=&triggers=75333.40&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

