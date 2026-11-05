# Evidence Report: Copy Trading Matrix: Equity Mode - Stop HFT BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_19_equity_stop_hft_buy_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives pending Stop HFT BUY scaled to equity ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:49:54.005530` $\rightarrow$ `2026-11-05T15:50:00.782216` (6.78s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Stop HFT BUY (0.01 lots)** | `0.01` | `0.01` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80741` | `80741` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80941` | `80941` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80741` | `80741` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80941` | `80941` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.