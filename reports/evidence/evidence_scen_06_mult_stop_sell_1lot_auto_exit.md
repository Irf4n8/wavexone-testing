# Evidence Report: Multiplier Mode: Stop HFT SELL 1.00 Lot (Trigger & Auto-Exit) (❌ FAIL)

**Test Identifier:** `evidence_scen_06_mult_stop_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT SELL (type=0) with trigger 4.0 pts below CMP. Follower replicates 3.00 lots. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:28:37.927522` $\rightarrow$ `2026-11-05T18:29:50.374807` (72.45s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.0 Lots Pending Stop SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (79531.36) Replicated** | `79531.36` | `79531.36` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Stop HFT SELL 1.00 Lot (Trigger & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59735,
    "time": 0.06646084785461426
  },
  "_duration_ms": 285.68,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=1.00&sls=79539.36&targets=79523.36&triggers=79531.36&symbol=X:BTCUSD&stop_hft_type=0&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1412"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.