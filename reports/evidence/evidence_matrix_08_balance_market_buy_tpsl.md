# Evidence Report: Copy Trading Matrix: Balance Mode - Market BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_08_balance_market_buy_tpsl`  
**Objective:** Verify that under Balance mode, Follower receives lot size proportional to live balance ratio on Market BUY with matching TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:48:02.630399` $\rightarrow$ `2026-11-05T15:48:11.287370` (8.66s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled to Balance Ratio (0.11 lots)** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79845` | `79845` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80845` | `80845` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79845` | `79845` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80845` | `80845` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.