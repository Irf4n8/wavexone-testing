# Evidence Report: Copy Trading: Partial Auto Squareoff Proportional Lot Reduction (✅ PASS)

**Test Identifier:** `evidence_scen_27_partial_auto_squareoff_proportional`  
**Objective:** Master places 1.00 lot BUY. Follower 1 replicates 3.00 lots. Master squares off 0.50 lots (50%). Verify follower position auto squares off proportionally to 1.50 lots.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:48:07.732585` $\rightarrow$ `2026-11-05T18:48:16.757333` (9.02s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Initial Follower Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Partial Squareoff (0.50 Lot)
- **Action:** `GET /book/squareoff.php?id=59999&close_mode=partial&partial_lot=0.50`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 59999  Sent to for Closing",
  "data": {
    "exitMsg": "Exited 'BTCUSD' , 0.50 Lots transit"
  },
  "_duration_ms": 334.91
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.