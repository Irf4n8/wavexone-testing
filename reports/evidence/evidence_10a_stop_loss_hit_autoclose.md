# Evidence Report: Copy Trading: Auto-Close on Stop Loss Hit (120s Timeout) (❌ FAIL)

**Test Identifier:** `evidence_10a_stop_loss_hit_autoclose`  
**Objective:** Place a BUY position with tight SL offset (12 points). Wait up to 120s for market tick to cross SL. Assert Master and all 5 followers auto-close.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:04:09.300488` $\rightarrow$ `2026-11-05T17:06:23.284397` (133.98s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (0/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **SL Auto-Close Hit** | `Triggered within 120s` | `Price did not move 12 points` | ❌ FAIL | Marked INCONCLUSIVE: test cannot force live staging market price ticks. |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.