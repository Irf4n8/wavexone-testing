# Evidence Report: Copy Trading Matrix: Multiplier Mode - Pending Limit BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_03_multiplier_limit_buy_tpsl`  
**Objective:** Verify that placing 1.00 lot Limit BUY with explicit Trigger, TP, and SL replicates 3.00 lots to follower with matching parameters and clean cancellation.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:15.792573` $\rightarrow$ `2026-11-05T15:47:22.336359` (6.54s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Limit BUY** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79137` | `79137` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79537` | `79537` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79137` | `79137` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79537` | `79537` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Limit BUY with TP/SL
- **Action:** `POST /trade/placeorder.php?type=limit&trigger=79337.56&sl=79137.56&target=79537.56`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 57410,
    "time": 0.0749819278717041
  },
  "_duration_ms": 287.05,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=1.00&sl=79137.56&target=79537.56&trigger=79337.56&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_833"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.