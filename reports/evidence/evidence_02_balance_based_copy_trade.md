# Evidence Report: Copy Trading: Proportional Balance-Based Lot Sizing & Rounding Rule Audit (✅ PASS)

**Test Identifier:** `evidence_02_balance_based_copy_trade`  
**Objective:** Verify balance proportional lot sizing and evaluate boundary probe with raw follower lot in 0.1050 - 0.1099 to determine whether platform implements round (0.11) or floor (0.10).  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:59:38.949823` $\rightarrow$ `2026-11-05T16:59:51.834722` (12.88s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Probe 1 Balance Lot Tolerance (within 1 step: 0.01)** | `0.11` | `0.11` | ✅ PASS | Raw: 0.11012, Expected: 0.11, Actual: 0.11 |
| 2 | **Probe 2 Rounding Rule Detection from Platform Output** | `0.11 (round) or 0.10 (floor)` | `0.11` | ✅ PASS | Raw: 0.10792 -> Platform Lot: 0.11 -> Rule: round |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Update Copy Method to Balance
- **Action:** `GET /user/updateCopyTradingMethod.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Update Successfully",
  "data": []
}
```

### Step 2: Probe 2 Boundary Setup
- **Action:** `Selected probe lot so raw lot lands in 0.1050 - 0.1099`
- **Telemetry / Details:** `{"probe_master_lot": 0.98, "raw_lot": 0.10791573576429103, "round_val": 0.11, "floor_val": 0.1}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.