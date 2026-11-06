# Evidence Report: Multiplier Mode: Limit SELL 1.00 Lot (Pending & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_04_mult_limit_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit SELL with trigger 1.5 pts above CMP. Follower replicates 3.00 lots. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:27:28.370616` $\rightarrow$ `2026-11-05T18:27:40.392515` (12.02s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.0 Lots Pending Limit SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (79567.08) Replicated** | `79567.08` | `79567.08` | ✅ PASS |  |
| 3 | **Limit SELL Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 6.28s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Limit SELL 1.00 Lot (Pending & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59723,
    "time": 0.08333086967468262
  },
  "_duration_ms": 296.56,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=1.00&sl=79575.08&target=79559.08&trigger=79567.08&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1404"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.