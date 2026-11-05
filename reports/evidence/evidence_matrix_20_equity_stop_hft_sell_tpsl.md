# Evidence Report: Copy Trading Matrix: Equity Mode - Stop HFT SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_20_equity_stop_hft_sell_tpsl`  
**Objective:** Verify that under Equity mode, Follower receives pending Stop HFT SELL scaled to equity ratio with matching Trigger, TP, and SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:50:03.218314` $\rightarrow$ `2026-11-05T15:50:10.029690` (6.81s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Scaled Stop HFT SELL (0.01 lots)** | `0.01` | `0.01` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79933` | `79933` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79733` | `79733` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79933` | `79933` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79733` | `79733` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.