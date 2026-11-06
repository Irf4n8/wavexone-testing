# Evidence Report: Balance Mode: Stop HFT SELL 1.00 Lot (Trigger & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_13_bal_stop_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT SELL (type=0) with trigger 4.0 pts below CMP. Follower replicates balance-scaled pending lot. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:31:48.027177` $\rightarrow$ `2026-11-05T18:32:33.389739` (45.36s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.11 Lots Pending Stop SELL** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Follower Trigger (79587.95) Replicated** | `79587.95` | `79587.95` | ✅ PASS |  |
| 3 | **Stop SELL Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 0.2s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Stop HFT SELL 1.00 Lot (Trigger & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59795,
    "time": 0.07700800895690918
  },
  "_duration_ms": 294.89,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=1.00&sls=79595.95&targets=79579.95&triggers=79587.95&symbol=X:BTCUSD&stop_hft_type=0&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1431"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.