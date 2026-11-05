# Evidence Report: Copy Trading: Market SELL 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_02_market_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market SELL with tight 5.0 pt TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:14:55.854091` $\rightarrow$ `2026-11-05T17:15:03.262907` (7.41s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 3.00 Lots (3.0x Multiplier)** | `3.0` | `3.0` | ✅ PASS |  |
| 3 | **Follower SL (80274.45) Propagated** | `80274.45` | `80274.45` | ✅ PASS |  |
| 4 | **Follower TP (80264.45) Propagated** | `80264.45` | `80264.45` | ✅ PASS |  |
| 5 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 2.57s without manual close. |
| 6 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Market SELL Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "58715",
    "intentId": "34655e38876f7f79735b43c26ac6093b",
    "executionStatus": "queued",
    "fanoutJobId": 6784,
    "fanoutStatus": "queued",
    "requestId": "legacy_f5e2256f0ded10ad3dd59b6d4b9841e6",
    "placementReplayProtected": true
  },
  "_duration_ms": 233.87,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=80274.45&target=80264.45&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1226"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.