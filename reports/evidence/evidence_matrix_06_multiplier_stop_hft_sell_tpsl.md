# Evidence Report: Copy Trading Matrix: Multiplier Mode - Stop HFT SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_06_multiplier_stop_hft_sell_tpsl`  
**Objective:** Verify that placing 0.01 lot Stop HFT SELL (stop_hft_type=0) with explicit Trigger, TP, and SL replicates 0.03 lots to follower with matching parameters and clean cancellation.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:42.495345` $\rightarrow$ `2026-11-05T15:47:48.869976` (6.37s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.03 Lots Stop HFT SELL** | `0.03` | `0.03` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79956` | `79956` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79756` | `79756` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79956` | `79956` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79756` | `79756` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Stop HFT SELL with TP/SL
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=0&triggers=79856.00&sls=79956.00&targets=79756.00`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 57428,
    "time": 0.05874300003051758
  },
  "_duration_ms": 258.1,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=0.01&sls=79956.00&targets=79756.00&triggers=79856.00&symbol=X:BTCUSD&stop_hft_type=0&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_842"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.