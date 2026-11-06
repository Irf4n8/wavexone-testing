# Evidence Report: CT-MUL-MKT-SELL-WITH-TPSL — Multiplier Market SELL WITH TP/SL

- **Category:** Multiplier Market Orders
- **Status:** `PASS`
- **Execution Time:** 4.49s
- **Timestamp:** 2026-11-06 14:24:51

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | All 5 Followers Replicated (1.50 Lots) | `True` | `True` | ✅ PASS |
| 2 | ctf2 SL Propagated | `True` | `True` | ✅ PASS |
| 3 | ctf2 TP Propagated | `True` | `True` | ✅ PASS |
| 4 | ctf5 SL Propagated | `True` | `True` | ✅ PASS |
| 5 | ctf5 TP Propagated | `True` | `True` | ✅ PASS |
| 6 | ctf4 SL Propagated | `True` | `True` | ✅ PASS |
| 7 | ctf4 TP Propagated | `True` | `True` | ✅ PASS |
| 8 | ctf3 SL Propagated | `True` | `True` | ✅ PASS |
| 9 | ctf3 TP Propagated | `True` | `True` | ✅ PASS |
| 10 | ctf1 SL Propagated | `True` | `True` | ✅ PASS |
| 11 | ctf1 TP Propagated | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Market SELL
- **Action:** `POST /trade/placeorder.php`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order accepted for processing", "data": {"orderId": "75022", "intentId": "e6eb634b20bbf3b5807c68adbb2000c2", "executionStatus": "queued", "fanoutJobId": 9425, "fanoutStatus": "queued", "requestId": "legacy_c64eaac0e91c737a857ab5cb2c2c39f9", "placementReplayProtected": true}, "_duration_ms": 222.75, "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=0.50&sl=76434.07&target=74834.07&symbol=X:BTCUSD&token=[REDACTED]&clicked=yes&fingerprint=[REDACTED]"}`

