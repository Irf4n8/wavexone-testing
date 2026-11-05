# Evidence Report: Copy Trading Matrix: Multiplier Mode - Pending Limit SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_04_multiplier_limit_sell_tpsl`  
**Objective:** Verify that placing 1.00 lot Limit SELL with explicit Trigger, TP, and SL replicates 3.00 lots to follower with matching parameters and clean cancellation.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:24.797208` $\rightarrow$ `2026-11-05T15:47:31.241938` (6.44s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Limit SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `81553` | `81553` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `81153` | `81153` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `81553` | `81553` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `81153` | `81153` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Limit SELL with TP/SL
- **Action:** `POST /trade/placeorder.php?type=limit&trigger=81353.56&sl=81553.56&target=81153.56`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 57416,
    "time": 0.06988906860351562
  },
  "_duration_ms": 282.43,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=1.00&sl=81553.56&target=81153.56&trigger=81353.56&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_836"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.