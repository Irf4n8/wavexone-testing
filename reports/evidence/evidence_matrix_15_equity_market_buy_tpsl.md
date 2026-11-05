# Evidence Report: Copy Trading Matrix: Equity Mode - Market BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_15_equity_market_buy_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives lot size proportional to live equity ratio on Market BUY with matching TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:13.152780` $\rightarrow$ `2026-11-05T15:49:21.302139` (8.15s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled to Equity Ratio BUY (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79850` | `79850` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80850` | `80850` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79850` | `79850` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80850` | `80850` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.