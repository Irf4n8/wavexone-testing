# Evidence Report: Copy Trading Matrix: Balance Mode - Stop HFT BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_12_balance_stop_hft_buy_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives pending Stop HFT BUY scaled to balance ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:43.232498` $\rightarrow$ `2026-11-05T15:48:50.032785` (6.8s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Stop HFT BUY (0.01 lots)** | `0.01` | `0.01` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80753` | `80753` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80953` | `80953` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80753` | `80753` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80953` | `80953` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.