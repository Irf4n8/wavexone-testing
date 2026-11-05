# Evidence Report: Copy Trading: Stop HFT BUY 1.00 Lot with Trigger, TP/SL & Automatic Exit (❌ FAIL)

**Test Identifier:** `evidence_scen_05_stop_hft_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BUY (type=1) with trigger 5.0 pts above CMP. Follower replicates 3.00 lots. Triggers into fill, then auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:16:27.033433` $\rightarrow$ `2026-11-05T17:17:31.754602` (64.72s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Pending Stop BUY** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (80287.59) Replicated** | `80287.59` | `80287.59` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Stop HFT BUY Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=1`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 58747,
    "time": 0.0648508071899414
  },
  "_duration_ms": 279.14,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=80277.59&targetb=80292.59&triggerb=80287.59&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1236"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.