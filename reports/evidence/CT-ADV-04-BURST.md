# Evidence Report: CT-ADV-04-BURST — Rapid-Fire Scalping Burst Concurrency Test (4 Fast Orders)

- **Category:** Stress & Concurrency
- **Status:** `PASS`
- **Execution Time:** 15.76s
- **Timestamp:** 2026-11-06 17:36:09

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master Has 4 Open Positions | `4` | `4` | ✅ PASS |
| 2 | ctf1 Replicated All 4 Burst Orders | `4` | `4` | ✅ PASS |
| 3 | ctf2 Replicated All 4 Burst Orders | `4` | `4` | ✅ PASS |
| 4 | ctf3 Replicated All 4 Burst Orders | `4` | `4` | ✅ PASS |
| 5 | ctf4 Replicated All 4 Burst Orders | `4` | `4` | ✅ PASS |
| 6 | ctf5 Replicated All 4 Burst Orders | `4` | `4` | ✅ PASS |
| 7 | Mass Square-Off Clean Slate Verified | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Fired 4 Rapid Orders
- **Action:** `POST /trade/placeorder.php x4`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"burst_duration_sec": 3.09}`

