# Evidence Report: CT-MUL-LMT-BUY-NO-TPSL — Multiplier Limit BUY WITHOUT TP/SL

- **Category:** Multiplier Limit Orders
- **Status:** `PASS`
- **Execution Time:** 7.67s
- **Timestamp:** 2026-11-06 14:25:02

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Followers Replicated Limit BUY (1.50 Lots) | `5` | `5` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Limit BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order Placed Successfully", "data": {"orderId": 75033, "time": 0.04695487022399902}, "_duration_ms": 244.47, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.50&sl=&target=&trigger=75356.25&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

