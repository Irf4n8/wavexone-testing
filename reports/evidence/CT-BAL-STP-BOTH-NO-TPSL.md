# Evidence Report: CT-BAL-STP-BOTH-NO-TPSL — Balance-Based Stop HFT BOTH WITHOUT TP/SL

- **Category:** Balance Stop HFT Orders
- **Status:** `PASS`
- **Execution Time:** 5.79s
- **Timestamp:** 2026-11-06 14:29:53

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Stop HFT BOTH Dual Legs (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Stop HFT BOTH
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": "75192,75193", "time": 0.03999805450439453}, "_duration_ms": 237.26, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.50&slb=&targetb=&triggerb=75818.35&lots=0.50&sls=&targets=&triggers=75318.35&symbol=X:BTCUSD&stop_hft_type=2&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

