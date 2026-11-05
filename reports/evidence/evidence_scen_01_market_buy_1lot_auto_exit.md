# Evidence Report: Copy Trading: Market BUY 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_01_market_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market BUY with tight 5.0 pt TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:14:48.356619` $\rightarrow$ `2026-11-05T17:14:54.636805` (6.28s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 3.00 Lots (3.0x Multiplier)** | `3.0` | `3.0` | ✅ PASS |  |
| 3 | **Follower SL (80268.81) Propagated** | `80268.81` | `80268.81` | ✅ PASS |  |
| 4 | **Follower TP (80278.81) Propagated** | `80278.81` | `80278.81` | ✅ PASS |  |
| 5 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 1.37s without manual close. |
| 6 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Market BUY Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "58709",
    "intentId": "7c70ba15d1226777ac90c9922b3d6f95",
    "executionStatus": "queued",
    "fanoutJobId": 6783,
    "fanoutStatus": "queued",
    "requestId": "legacy_36bc599230203cdd7304c48984b05f79",
    "placementReplayProtected": true
  },
  "_duration_ms": 229.61,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=80268.81&target=80278.81&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1223"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.