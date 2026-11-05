# Evidence Report: Copy Trading Matrix: Equity Mode - Market SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_16_equity_market_sell_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives lot size proportional to live equity ratio on Market SELL with matching TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:23.725999` $\rightarrow$ `2026-11-05T15:49:33.036277` (9.31s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled to Equity Ratio SELL (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80849` | `80849` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79849` | `79849` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80849` | `80849` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79849` | `79849` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.