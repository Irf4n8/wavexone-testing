# Evidence Report: Copy Trading: Market BUY 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_01_market_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market BUY with tight TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:33:03.432864` $\rightarrow$ `2026-11-05T17:33:13.181097` (9.75s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 3.00 Lots (3.0x Multiplier)** | `3.0` | `3.0` | ✅ PASS |  |
| 3 | **Follower SL (80141.45) Propagated** | `80141.45` | `80141.45` | ✅ PASS |  |
| 4 | **Follower TP (80157.45) Propagated** | `80157.45` | `80157.45` | ✅ PASS |  |
| 5 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 4.96s without manual close. |
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
    "orderId": "59092",
    "intentId": "ede96e4955022535ac9c6852f8523c31",
    "executionStatus": "queued",
    "fanoutJobId": 6870,
    "fanoutStatus": "queued",
    "requestId": "legacy_1c6439b448d750a11fe4411b419033d8",
    "placementReplayProtected": true
  },
  "_duration_ms": 229.01,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=80141.45&target=80157.45&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1330"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.