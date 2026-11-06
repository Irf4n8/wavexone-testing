# Evidence Report: CT-MUL-STP-BOTH-NO-TPSL — Multiplier Stop HFT BOTH WITHOUT TP/SL

- **Category:** Multiplier Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.12s
- **Timestamp:** 2026-11-06 14:26:50

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75090,75091", "time": 0.04519486427307129}, "_duration_ms": 249.31, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75859.12&lots=0.50&sls=&targets=&triggers=75359.12&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

