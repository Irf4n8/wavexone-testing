# Evidence Report: CT-MUL-STP-BOTH-WITH-TPSL — Multiplier Stop HFT BOTH WITH TP/SL

- **Category:** Multiplier Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.34s
- **Timestamp:** 2026-11-06 14:27:03

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75102,75103", "time": 0.04450082778930664}, "_duration_ms": 231.48, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=75710.96&targetb=76010.96&triggerb=75860.96&lots=0.50&sls=75510.96&targets=75210.96&triggers=75360.96&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

