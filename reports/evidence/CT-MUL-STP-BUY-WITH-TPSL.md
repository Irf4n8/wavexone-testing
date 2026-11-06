# Evidence Report: CT-MUL-STP-BUY-WITH-TPSL — Multiplier Stop HFT BUY WITH TP/SL

- **Category:** Multiplier Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.23s
- **Timestamp:** 2026-11-06 14:26:09

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BUY (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75066, "time": 0.04458498954772949}, "_duration_ms": 233.3, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75714.74&targetb=76014.74&triggerb=75864.74&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

