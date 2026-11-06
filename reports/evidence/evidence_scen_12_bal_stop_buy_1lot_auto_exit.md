# Evidence Report: Balance Mode: Stop HFT BUY 1.00 Lot (Trigger & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_12_bal_stop_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BUY (type=1) with trigger 4.0 pts above CMP. Follower replicates balance-scaled pending lot. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:31:29.295865` $\rightarrow$ `2026-11-05T18:31:41.859440` (12.56s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.11 Lots Pending Stop BUY** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Follower Trigger (79636.63) Replicated** | `79636.63` | `79636.63` | ✅ PASS |  |
| 3 | **Stop BUY Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 1.41s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Stop HFT BUY 1.00 Lot (Trigger & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59789,
    "time": 0.060463905334472656
  },
  "_duration_ms": 270.23,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=79628.63&targetb=79644.63&triggerb=79636.63&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1427"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.