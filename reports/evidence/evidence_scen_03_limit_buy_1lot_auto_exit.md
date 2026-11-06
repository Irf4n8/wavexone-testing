# Evidence Report: Copy Trading: Limit BUY 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_03_limit_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit BUY with trigger 1.5 pts below CMP. Follower replicates 3.00 lots pending. When filled, auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:33:38.907245` $\rightarrow$ `2026-11-05T17:33:55.761936` (16.85s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Pending Limit BUY** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (80138.31) Replicated** | `80138.31` | `80138.31` | ✅ PASS |  |
| 3 | **Limit BUY Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 8.7s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Limit BUY Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=limit`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59105,
    "time": 1.3782470226287842
  },
  "_duration_ms": 1564.57,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=1.00&sl=80130.31&target=80146.31&trigger=80138.31&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1337"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.