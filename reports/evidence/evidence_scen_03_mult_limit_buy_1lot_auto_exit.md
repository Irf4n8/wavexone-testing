# Evidence Report: Multiplier Mode: Limit BUY 1.00 Lot (Pending & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_03_mult_limit_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit BUY with trigger 1.5 pts below CMP. Follower replicates 3.00 lots. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:27:09.951652` $\rightarrow$ `2026-11-05T18:27:22.170796` (12.22s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.0 Lots Pending Limit BUY** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (79574.83) Replicated** | `79574.83` | `79574.83` | ✅ PASS |  |
| 3 | **Limit BUY Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 1.42s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Limit BUY 1.00 Lot (Pending & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59711,
    "time": 0.07927107810974121
  },
  "_duration_ms": 298.84,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=1.00&sl=79566.83&target=79582.83&trigger=79574.83&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1402"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.