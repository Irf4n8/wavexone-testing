# Evidence Report: Balance Mode: Market BUY 1.00 Lot (Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_08_bal_market_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market BUY with tight TP/SL. Follower scales by balance ratio (~0.11 lots). Position auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:30:32.898733` $\rightarrow$ `2026-11-05T18:30:41.230464` (8.33s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (7/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 0.11 Lots (Balance Mode)** | `0.11` | `0.11` | ✅ PASS |  |
| 3 | **Replication Entry Latency (<2.0s)** | `2.0` | `1.989` | ✅ PASS |  |
| 4 | **Follower SL (79626) Propagated** | `79626` | `79626` | ✅ PASS |  |
| 5 | **Follower TP (79642) Propagated** | `79642` | `79642` | ✅ PASS |  |
| 6 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 1.41s without manual close. |
| 7 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Market BUY 1.00 Lot (Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59760",
    "intentId": "0f6ddeeaeb9aa5dfcc93e46f5bbbc958",
    "executionStatus": "queued",
    "fanoutJobId": 6961,
    "fanoutStatus": "queued",
    "requestId": "legacy_313aa2f4fb46ec305f37cba294d94a2c",
    "placementReplayProtected": true
  },
  "_duration_ms": 242.99,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=79626.97&target=79642.97&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1419"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.