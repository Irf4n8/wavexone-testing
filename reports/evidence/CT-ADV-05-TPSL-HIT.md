# Evidence Report: CT-ADV-05-TPSL-HIT — Real-Market TP/SL Hit & Automated Follower Fanout Closure

- **Category:** Risk & Auto Square-Off
- **Status:** `PASS`
- **Execution Time:** 10.31s
- **Timestamp:** 2026-11-06 17:36:28

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master Order Hit TP/SL & Auto-Closed | `True` | `True` | ✅ PASS |
| 2 | ctf1 Automatically Closed via Fanout | `0` | `0` | ✅ PASS |
| 3 | ctf2 Automatically Closed via Fanout | `0` | `0` | ✅ PASS |
| 4 | ctf3 Automatically Closed via Fanout | `0` | `0` | ✅ PASS |
| 5 | ctf4 Automatically Closed via Fanout | `0` | `0` | ✅ PASS |
| 6 | ctf5 Automatically Closed via Fanout | `0` | `0` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Live Price Probed
- **Action:** `Probe execution price`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"cmp": 76093.39, "sl": "76091.39", "tp": "76095.39"}`

