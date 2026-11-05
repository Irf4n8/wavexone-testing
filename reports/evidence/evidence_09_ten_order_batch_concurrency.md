# Evidence Report: Copy Trading: Concurrency Batch (5 BUY + 5 SELL Orders Across 5 Followers) (❌ FAIL)

**Test Identifier:** `evidence_09_ten_order_batch_concurrency`  
**Objective:** Stress-test the fanout queue by placing 10 orders in rapid succession (5 BUY, 5 SELL). Verify all 5 followers replicate all 10 orders (50 total copied orders) with zero drops and bulk squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:01:21.358190` $\rightarrow$ `2026-11-05T17:03:01.389996` (100.03s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (0/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 Bulk Squareoff Closure** | `True` | `False` | ❌ FAIL |  |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.