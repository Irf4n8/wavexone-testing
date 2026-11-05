# Evidence Report: Copy Trading: Pending Order Auto-Cancellation via Master Only (✅ PASS)

**Test Identifier:** `evidence_11_limit_and_stop_hft_replication`  
**Objective:** Cancel ONLY the master pending limit order. Assert follower pending copy disappears on its own within 10s. Log failure as suspected engine bug.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:52:39.444620` $\rightarrow$ `2026-11-05T16:52:43.747318` (4.3s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Pending Order Auto-Cancelled on Master Cancel** | `True` | `True` | ✅ PASS | If False: logged as FAIL (suspected engine bug, pending dev confirmation). |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Cancel Limit Request
- **Action:** `GET /book/cancel.php?id=58375`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 58375  cancelled",
  "data": [],
  "_duration_ms": 205.13
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.