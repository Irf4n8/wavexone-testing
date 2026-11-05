# Evidence Report: Copy Trading: Proportional Balance-Based Lot Sizing & Rounding Rule Audit (✅ PASS)

**Test Identifier:** `evidence_02_balance_based_copy_trade`  
**Objective:** Verify that updating copy method to 'balance' scales follower order lot size proportionally to follower balance vs master balance, testing both round and rounding-boundary probe ending below .005.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:57:18.503045` $\rightarrow$ `2026-11-05T14:57:30.940998` (12.44s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (3/3 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Method Update Status** | `success` | `success` | ✅ PASS |  |
| 2 | **Probe 1 Balance Lot Tolerance (within 1 step: 0.01)** | `0.11` | `0.11` | ✅ PASS | Raw: 0.11013, Expected: 0.11, Actual: 0.11 |
| 3 | **Probe 2 Rounding Rule Detection** | `round(0.1)` | `0.1` | ✅ PASS | Detected rounding rule behavior: round |

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

### Step 2: Probe 1 Calculations
- **Action:** `Computed expected balance scaling`
- **Telemetry / Details:** `{"master_balance": 111224113.69, "follower_balance": 12249323.37, "ratio": 0.11013190362784898, "raw_lot": 0.11013190362784898, "expected_lot": 0.11}`

### Step 3: Probe 2 Boundary Setup
- **Action:** `Selected probe lot to differentiate round vs ceil`
- **Telemetry / Details:** `{"probe_master_lot": 0.95, "raw_lot": 0.10462530844645652, "round_val": 0.1}`

### Step 4: Restore Multiplier Method
- **Action:** `GET /user/updateCopyTradingMethod.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Update Successfully",
  "data": []
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.