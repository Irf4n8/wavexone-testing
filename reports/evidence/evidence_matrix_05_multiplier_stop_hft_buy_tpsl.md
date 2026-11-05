# Evidence Report: Copy Trading Matrix: Multiplier Mode - Stop HFT BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_05_multiplier_stop_hft_buy_tpsl`  
**Objective:** Verify that placing 0.01 lot Stop HFT BUY (stop_hft_type=1) with explicit Trigger, TP, and SL replicates 0.03 lots to follower with matching parameters and clean cancellation.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:33.674646` $\rightarrow$ `2026-11-05T15:47:40.068387` (6.39s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.03 Lots Stop HFT BUY** | `0.03` | `0.03` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80766` | `80766` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80966` | `80966` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80766` | `80766` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80966` | `80966` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Stop HFT BUY with TP/SL
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=1&triggerb=80866.84&slb=80766.84&targetb=80966.84`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 57422,
    "time": 0.06981492042541504
  },
  "_duration_ms": 277.33,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.01&slb=80766.84&targetb=80966.84&triggerb=80866.84&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_839"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.