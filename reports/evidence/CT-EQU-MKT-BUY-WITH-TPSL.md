# Evidence Report: CT-EQU-MKT-BUY-WITH-TPSL — Equity-Based Market BUY WITH TP/SL

- **Category:** Equity Market Orders
- **Status:** `PASS`
- **Execution Time:** 5.42s
- **Timestamp:** 2026-11-06 14:30:33

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (0.05 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market BUY
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75213", "intentId": "f417186e2d0a4fdf348ae68b0baefc24", "executionStatus": "queued", "fanoutJobId": 9433, "fanoutStatus": "queued", "requestId": "legacy_2e5d7e2176ae61384620cd8979085c02", "placementReplayProtected": true}, "_duration_ms": 254.65, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=0.50&sl=74815.81&target=76415.81&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

