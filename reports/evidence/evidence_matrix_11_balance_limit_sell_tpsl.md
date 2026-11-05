# Evidence Report: Copy Trading Matrix: Balance Mode - Pending Limit SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_11_balance_limit_sell_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives pending Limit SELL scaled to balance ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:33.920764` $\rightarrow$ `2026-11-05T15:48:40.783473` (6.86s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Limit SELL (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `81546` | `81546` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `81146` | `81146` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `81546` | `81546` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `81146` | `81146` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.