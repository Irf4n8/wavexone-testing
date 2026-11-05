# Evidence Report: Copy Trading: Auto-Close on Take Profit Hit (120s Timeout) (✅ PASS)

**Test Identifier:** `evidence_10b_take_profit_hit_autoclose`  
**Objective:** Place a BUY position with tight TP offset (12 points). Wait up to 120s for market tick to cross TP. Assert Master and all 5 followers auto-close.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:52:23.748677` $\rightarrow$ `2026-11-05T16:52:36.980862` (13.23s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Order Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |
| 2 | **Follower ctf1 Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |
| 3 | **Follower ctf2 Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |
| 4 | **Follower ctf3 Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |
| 5 | **Follower ctf4 Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |
| 6 | **Follower ctf5 Auto-Closed on TP Hit** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.