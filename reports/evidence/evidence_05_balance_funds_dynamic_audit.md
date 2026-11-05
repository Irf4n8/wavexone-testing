# Evidence Report: Copy Trading: Dynamic Margin Audit & Leverage Compliance (✅ PASS)

**Test Identifier:** `evidence_05_balance_funds_dynamic_audit`  
**Objective:** Verify expected margin = (lot * price / leverage) within 2% tolerance, follower margin = 3x master margin (+-2%), and 100% margin release post-squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:58:07.186080` $\rightarrow$ `2026-11-05T14:58:18.799951` (11.61s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Margin Formula Match (2% tolerance)** | `$160.49 +- 2%` | `$160.50 (err: 0.01%)` | ✅ PASS | Formula: lot * price / leverage |
| 2 | **Follower Margin Formula Match (2% tolerance)** | `$481.48 +- 2%` | `$481.50 (err: 0.00%)` | ✅ PASS | Formula: (lot*3) * price / leverage |
| 3 | **Follower Margin is 3x Master Margin (2% tolerance)** | `3.0 +- 2%` | `3.000 (err: 0.00%)` | ✅ PASS |  |
| 4 | **Master Margin Fully Released (Residual <= 1.0)** | `0.0` | `0.0` | ✅ PASS | Fund restored back to balance |
| 5 | **Follower Margin Fully Released (Residual <= 1.0)** | `0.0` | `0.0` | ✅ PASS | Fund restored back to balance |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Dynamic Margin Expectation
- **Action:** `Computed mathematical margin requirement`
- **Telemetry / Details:** `{"price": 80247.4, "leverage": 500, "expected_master_margin": 160.49, "expected_follower_margin": 481.48}`

### Step 2: In-Trade Margin Observation
- **Action:** `GET /book/balance.php`
- **Telemetry / Details:** `{"observed_master_margin": 160.5, "observed_follower_margin": 481.5}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.