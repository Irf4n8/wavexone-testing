# Evidence Report: Copy Trading: Short/SELL Order Replication (1.00 Master Lot -> 3.00 Follower Lots) (✅ PASS)

**Test Identifier:** `evidence_08_sell_orders_replication`  
**Objective:** Verify that placing 1.00 lot SELL order replicates as SELL with 3.00 lots across all 5 followers, records replication latencies, and verifies clean simultaneous squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:58:48.562849` $\rightarrow$ `2026-11-05T14:58:55.848215` (7.29s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master SELL Order in Book** | `SELL` | `SELL` | ✅ PASS |  |
| 2 | **Follower ctf1 Replicated SELL Lot & Side** | `SELL 3.0` | `SELL 3.0` | ✅ PASS | Latency: 1477.29ms |
| 3 | **Follower ctf2 Replicated SELL Lot & Side** | `SELL 3.0` | `SELL 3.0` | ✅ PASS | Latency: 2372.71ms |
| 4 | **Follower ctf3 Replicated SELL Lot & Side** | `SELL 3.0` | `SELL 3.0` | ✅ PASS | Latency: 2569.87ms |
| 5 | **Follower ctf4 Replicated SELL Lot & Side** | `SELL 3.0` | `SELL 3.0` | ✅ PASS | Latency: 2769.59ms |
| 6 | **Follower ctf5 Replicated SELL Lot & Side** | `SELL 3.0` | `SELL 3.0` | ✅ PASS | Latency: 2972.5ms |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master SELL Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "55822",
    "intentId": "2180de25ef6666d66cc26a7cfd082f5b",
    "executionStatus": "queued",
    "fanoutJobId": 6253,
    "fanoutStatus": "queued",
    "requestId": "legacy_b5a2dc65ba54f2cd18f653fdb055fa62",
    "placementReplayProtected": true
  },
  "_duration_ms": 222.03,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=80365.68&target=80165.68&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_492"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.