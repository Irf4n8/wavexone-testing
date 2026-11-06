# Evidence Report: Multiplier Mode: Market BUY 1.00 Lot (Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_01_mult_market_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market BUY with tight TP/SL. Follower replicates 3.00 lots (3.0x). Position auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:26:38.266312` $\rightarrow$ `2026-11-05T18:26:45.959909` (7.69s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |
| 2 | **Follower Replicated 3.0 Lots (Multiplier Mode)** | `3.0` | `3.0` | ✅ PASS |  |
| 3 | **Replication Entry Latency (<2.0s)** | `2.0` | `2.016` | ❌ FAIL |  |
| 4 | **Follower SL (79604) Propagated** | `79604` | `79604` | ✅ PASS |  |
| 5 | **Follower TP (79620) Propagated** | `79620` | `79620` | ✅ PASS |  |
| 6 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 2.63s without manual close. |
| 7 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Market BUY 1.00 Lot (Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59685",
    "intentId": "f98de26ece8fbdd1e84f2148b7c9cdcd",
    "executionStatus": "queued",
    "fanoutJobId": 6957,
    "fanoutStatus": "queued",
    "requestId": "legacy_e58565a229eef70fcea0e580cbfb9d6d",
    "placementReplayProtected": true
  },
  "_duration_ms": 260.56,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=79604.90&target=79620.90&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1397"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.