# Evidence Report: Copy Trading Matrix: Multiplier Mode - Stop HFT BOTH with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_07_multiplier_stop_hft_both_tpsl`  
**Objective:** Verify that placing Stop HFT BOTH creates dual pending orders on master and replicates dual 3.0x orders with matching Trigger, TP, and SL to follower.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:51.277892` $\rightarrow$ `2026-11-05T15:48:00.169131` (8.89s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated Dual Stop Orders with TP/SL** | `2` | `2` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Stop HFT BOTH with TP/SL
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=2`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": "57439,57440",
    "time": 0.06980395317077637
  },
  "_duration_ms": 284.87,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=0.01&slb=80756.54&targetb=80956.54&triggerb=80856.54&lots=0.01&sls=79956.54&targets=79756.54&triggers=79856.54&symbol=X:BTCUSD&stop_hft_type=2&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_845"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.