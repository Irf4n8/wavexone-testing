# Evidence Report: Copy Trading Matrix: Balance Mode - Stop HFT SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_13_balance_stop_hft_sell_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives pending Stop HFT SELL scaled to balance ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:52.454888` $\rightarrow$ `2026-11-05T15:48:59.201513` (6.75s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Stop HFT SELL (0.01 lots)** | `0.01` | `0.01` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79966` | `79966` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79766` | `79766` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79966` | `79966` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79766` | `79766` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.