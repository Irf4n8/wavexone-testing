# Evidence Report: Copy Trading Matrix: Equity Mode - Stop HFT BOTH with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_21_equity_stop_hft_both_tpsl`  
**Objective:** Verify that under Equity mode, Stop HFT BOTH creates dual pending orders on master and replicates dual equity-scaled orders with matching Trigger, TP, and SL to follower.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:50:12.466579` $\rightarrow$ `2026-11-05T15:50:23.716747` (11.25s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated Dual Stop Orders with TP/SL (Equity Mode)** | `2` | `2` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.