# Evidence Report: CT-MUL-STP-SELL-WITH-TPSL — Multiplier Stop HFT SELL WITH TP/SL

- **Category:** Multiplier Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.07s
- **Timestamp:** 2026-11-06 14:26:36

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT SELL (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75079, "time": 0.04220986366271973}, "_duration_ms": 235.73, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.50&sls=75503.63&targets=75203.63&triggers=75353.63&symbol=X:BTCUSD&stop_hft_type=0&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

