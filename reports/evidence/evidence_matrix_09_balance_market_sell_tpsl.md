# Evidence Report: Copy Trading Matrix: Balance Mode - Market SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_09_balance_market_sell_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives lot size proportional to live balance ratio on Market SELL with matching TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:13.720800` $\rightarrow$ `2026-11-05T15:48:22.243770` (8.52s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled to Balance Ratio SELL (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80842` | `80842` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79842` | `79842` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80842` | `80842` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79842` | `79842` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.