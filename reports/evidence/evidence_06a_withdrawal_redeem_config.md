# Evidence Report: Portal & Wallet: Dynamic 80% Withdrawal Cap with Open Orders (✅ PASS)

**Test Identifier:** `evidence_06a_withdrawal_redeem_config`  
**Objective:** Verify apiRedeemConfig dynamically caps withdrawable ratio to 0.8 when orders are open and restores to 1.0 upon closure.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:00:42.712334` $\rightarrow$ `2026-11-05T17:00:52.070705` (9.36s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (4/4 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Clean State Withdrawable Ratio == 1.0** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Active State open_orders Count >= 1** | `>= 1` | `1` | ✅ PASS |  |
| 3 | **Active State Withdrawable Ratio Capped to 0.8** | `0.8` | `0.8` | ✅ PASS |  |
| 4 | **Restored Withdrawable Ratio == 1.0** | `1.0` | `1.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.