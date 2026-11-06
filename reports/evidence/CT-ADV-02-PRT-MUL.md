# Evidence Report: CT-ADV-02-PRT-MUL — Partial Close Proportional Reduction (Multiplier Mode: 0.50 -> 0.30 => Follower 1.50 -> 0.90)

- **Category:** Trade Management
- **Status:** `PASS`
- **Execution Time:** 11.74s
- **Timestamp:** 2026-11-06 17:35:33

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Initial Replicated Lots == 1.50 across all 5 followers | `1.5` | `1.5` | ✅ PASS |
| 2 | Master Remaining Lot == 0.30 | `0.3` | `0.3` | ✅ PASS |
| 3 | ctf1 Proportional Remaining Lot == 0.90 | `0.9` | `0.9` | ✅ PASS |
| 4 | ctf2 Proportional Remaining Lot == 0.90 | `0.9` | `0.9` | ✅ PASS |
| 5 | ctf3 Proportional Remaining Lot == 0.90 | `0.9` | `0.9` | ✅ PASS |
| 6 | ctf4 Proportional Remaining Lot == 0.90 | `0.9` | `0.9` | ✅ PASS |
| 7 | ctf5 Proportional Remaining Lot == 0.90 | `0.9` | `0.9` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Master Partial Close 0.20 Lots
- **Action:** `GET /book/squareoff.php?id=77712&close_mode=partial&partial_lot=0.20`
- **Endpoint:** `` () | Latency: 0.0ms
- **Details:** `{"status": "success", "message": "Order ID - 77712  Sent to for Closing", "data": {"exitMsg": "Exited 'BTCUSD' , 0.20 Lots transit"}, "_duration_ms": 258.35}`

