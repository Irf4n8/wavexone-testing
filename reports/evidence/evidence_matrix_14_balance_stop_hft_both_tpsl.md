# Evidence Report: Copy Trading Matrix: Balance Mode - Stop HFT BOTH with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_14_balance_stop_hft_both_tpsl`  
**Objective:** Verify that under Balance mode, Stop HFT BOTH creates dual pending orders on master and replicates dual balance-scaled orders with matching TP/SL to follower.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:01.619298` $\rightarrow$ `2026-11-05T15:49:10.727405` (9.11s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated Dual Stop Orders with TP/SL (Balance Mode)** | `2` | `2` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.