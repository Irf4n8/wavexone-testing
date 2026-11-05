# Evidence Report: Copy Trading Matrix: Balance Mode - Pending Limit BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_10_balance_limit_buy_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives pending Limit BUY scaled to balance ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:24.725978` $\rightarrow$ `2026-11-05T15:48:31.488450` (6.76s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Limit BUY (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79135` | `79135` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79535` | `79535` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79135` | `79135` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79535` | `79535` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.