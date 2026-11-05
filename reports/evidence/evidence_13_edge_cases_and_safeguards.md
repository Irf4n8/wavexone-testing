# Evidence Report: Copy Trading: Edge Cases, Partial Close & Platform Resilience Audit (❌ FAIL)

**Test Identifier:** `evidence_13_edge_cases_and_safeguards`  
**Objective:** Verify real UI partial close endpoint (close_mode=partial&partial_lot=0.50), follower early close autonomy, extreme multiplier margin exhaustion, pause probe, invalid inputs rejection, and outside-hours symbol behavior.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:52:57.464757` $\rightarrow$ `2026-11-05T16:53:23.960694` (26.5s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (7/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 Zero Ghost/Duplicate Positions** | `1` | `1` | ✅ PASS |  |
| 2 | **Follower ctf2 Zero Ghost/Duplicate Positions** | `1` | `1` | ✅ PASS |  |
| 3 | **Follower ctf3 Zero Ghost/Duplicate Positions** | `1` | `1` | ✅ PASS |  |
| 4 | **Follower ctf4 Zero Ghost/Duplicate Positions** | `1` | `1` | ✅ PASS |  |
| 5 | **Follower ctf5 Zero Ghost/Duplicate Positions** | `1` | `1` | ✅ PASS |  |
| 6 | **Master Lot Reduced to 0.50** | `0.5` | `0.5` | ✅ PASS |  |
| 7 | **Follower Proportional Partial Close (3.00 -> 1.50)** | `1.5` | `1.5` | ✅ PASS | Observed follower lot: 1.5. Tagged UNVERIFIED vs spec. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Real UI Partial Close Request
- **Action:** `GET /book/squareoff.php?close_mode=partial&partial_lot=0.50`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 58382  Sent to for Closing",
  "data": {
    "exitMsg": "Exited 'BTCUSD' , 0.50 Lots transit"
  },
  "_duration_ms": 243.59
}
```

### Step 2: Follower 1 Early Close
- **Action:** `GET /book/squareoff.php?id=58393`
```json
// Server Response:
{
  "status": "fail",
  "message": "This order is no longer available to close. Please refresh your positions.",
  "data": [],
  "_duration_ms": 191.15
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.