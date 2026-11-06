# Evidence Report: Balance Mode: Limit SELL 1.00 Lot (Pending & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_11_bal_limit_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit SELL with trigger 1.5 pts above CMP. Follower replicates balance-scaled pending lot. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:31:14.758738` $\rightarrow$ `2026-11-05T18:31:23.125561` (8.37s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.11 Lots Pending Limit SELL** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Follower Trigger (79650.85) Replicated** | `79650.85` | `79650.85` | ✅ PASS |  |
| 3 | **Limit SELL Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 0.21s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Limit SELL 1.00 Lot (Pending & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59783,
    "time": 0.053926944732666016
  },
  "_duration_ms": 272.33,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=1.00&sl=79658.85&target=79642.85&trigger=79650.85&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1425"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.