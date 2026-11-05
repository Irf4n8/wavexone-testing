# Evidence Report: Copy Trading Matrix: Equity Mode - Pending Limit SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_18_equity_limit_sell_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives pending Limit SELL scaled to equity ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:44.780461` $\rightarrow$ `2026-11-05T15:49:51.564384` (6.78s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Limit SELL (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `81543` | `81543` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `81143` | `81143` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `81543` | `81543` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `81143` | `81143` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.