# Evidence Report: CT-MUL-STP-BUY-NO-TPSL — Multiplier Stop HFT BUY WITHOUT TP/SL

- **Category:** Multiplier Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.12s
- **Timestamp:** 2026-11-06 14:25:55

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75057, "time": 0.0419468879699707}, "_duration_ms": 235.94, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75884.31&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

