# Evidence Report: CT-EQU-LMT-SELL-WITH-TPSL — Equity-Based Limit SELL WITH TP/SL

- **Category:** Equity Limit Orders
- **Status:** `PASS`
- **Execution Time:** 8.25s
- **Timestamp:** 2026-11-06 14:31:49

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit SELL (0.05 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75254, "time": 0.04474997520446777}, "_duration_ms": 242.3, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=0.50&sl=76139.79&target=75739.79&trigger=75939.79&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

