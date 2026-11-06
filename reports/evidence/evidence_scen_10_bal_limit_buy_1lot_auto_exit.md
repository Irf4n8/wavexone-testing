# Evidence Report: Balance Mode: Limit BUY 1.00 Lot (Pending & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_10_bal_limit_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit BUY with trigger 1.5 pts below CMP. Follower replicates balance-scaled pending lot. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:31:00.603374` $\rightarrow$ `2026-11-05T18:31:08.512835` (7.91s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 0.11 Lots Pending Limit BUY** | `0.11` | `0.11` | ✅ PASS |  |
| 2 | **Follower Trigger (79646.81) Replicated** | `79646.81` | `79646.81` | ✅ PASS |  |
| 3 | **Limit BUY Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 0.2s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Limit BUY 1.00 Lot (Pending & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59777,
    "time": 0.06359505653381348
  },
  "_duration_ms": 275.57,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=1.00&sl=79638.81&target=79654.81&trigger=79646.81&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1423"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.