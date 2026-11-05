# Evidence Report: Copy Trading Matrix: Equity Mode - Pending Limit BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_17_equity_limit_buy_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives pending Limit BUY scaled to equity ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:35.545119` $\rightarrow$ `2026-11-05T15:49:42.315107` (6.77s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Limit BUY (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79155` | `79155` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79555` | `79555` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79155` | `79155` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79555` | `79555` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.