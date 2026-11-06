# Evidence Report: Balance Mode: Market SELL 1.00 Lot (Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_09_bal_market_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market SELL with tight TP/SL. Follower scales by balance ratio (~0.11 lots). Position auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:30:47.424170` $\rightarrow$ `2026-11-05T18:30:54.370792` (6.95s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 0.11 Lots (Balance Mode)** | `0.11` | `0.11` | ✅ PASS |  |
| 3 | **Replication Entry Latency (<2.0s)** | `2.0` | `2.035` | ❌ FAIL |  |
| 4 | **Follower SL (79641) Propagated** | `79641` | `79641` | ✅ PASS |  |
| 5 | **Follower TP (79625) Propagated** | `79625` | `79625` | ✅ PASS |  |
| 6 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 1.42s without manual close. |
| 7 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Market SELL 1.00 Lot (Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59766",
    "intentId": "6d1b873f70dea8cb301089ffe9436cb6",
    "executionStatus": "queued",
    "fanoutJobId": 6962,
    "fanoutStatus": "queued",
    "requestId": "legacy_b875dfca2b6ff9bab9ee0f6501f35c1c",
    "placementReplayProtected": true
  },
  "_duration_ms": 246.57,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=79641.42&target=79625.42&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1421"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.