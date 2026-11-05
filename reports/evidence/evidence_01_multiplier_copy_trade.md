# Evidence Report: Copy Trading: Multiplier-Based Replication (1.00 Master Lot -> 3.00 Follower Lots) (✅ PASS)

**Test Identifier:** `evidence_01_multiplier_copy_trade`  
**Objective:** Verify that placing 1.00 lot X:BTCUSD on Master replicates 3.00 lots to all 5 followers with separate read verification polling via /book/orders.php and simultaneous clean squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:59:28.978096` $\rightarrow$ `2026-11-05T16:59:36.177957` (7.2s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (13/13 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Order Status** | `success` | `success` | ✅ PASS |  |
| 2 | **Master Order Found in Book** | `True` | `True` | ✅ PASS |  |
| 3 | **Follower ctf1 Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 0.884s |
| 4 | **Follower ctf2 Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1.083s |
| 5 | **Follower ctf3 Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1.284s |
| 6 | **Follower ctf4 Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1.466s |
| 7 | **Follower ctf5 Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 2.327s |
| 8 | **Master Order Squareoff Closure** | `True` | `True` | ✅ PASS |  |
| 9 | **Follower ctf1 Simultaneous Squareoff** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf2 Simultaneous Squareoff** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf3 Simultaneous Squareoff** | `True` | `True` | ✅ PASS |  |
| 12 | **Follower ctf4 Simultaneous Squareoff** | `True` | `True` | ✅ PASS |  |
| 13 | **Follower ctf5 Simultaneous Squareoff** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "58410",
    "intentId": "305ff0517ad9d9665c6b81d1271fe35f",
    "executionStatus": "queued",
    "fanoutJobId": 6732,
    "fanoutStatus": "queued",
    "requestId": "legacy_8f41ffef650fd3e870bf3bb2b3a2b689",
    "placementReplayProtected": true
  },
  "_duration_ms": 255.82,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1100"
}
```

### Step 2: Master Order Snapshot
- **Action:** `GET /book/orders.php`
```json
// Server Response:
{
  "id": "58410",
  "symbol": "X:BTCUSD",
  "formated_symbol": "BTCUSD",
  "pair": "xxx",
  "time": "2026-11-05 11:29:30",
  "trigger": "0",
  "type": "market",
  "lot": "1",
  "bs": "BUY",
  "sl": "---",
  "tp": "---",
  "avg": "0",
  "t_swap": "0.00",
  "commission": null,
  "status": "pending",
  "partiallot": "---",
  "follower_placement": null,
  "provider_symbol": "X:BTCUSD",
  "display_symbol": "X:BTCUSD"
}
```

### Step 3: Replication Latencies
- **Action:** `Measured per-follower latency`
- **Telemetry / Details:** `{"ctf1": 0.884, "ctf2": 1.083, "ctf3": 1.284, "ctf4": 1.466, "ctf5": 2.327}`

### Step 4: Master Squareoff Request
- **Action:** `GET /book/squareoff.php?id=58410`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 58410  Sent to for Closing",
  "data": [],
  "_duration_ms": 273.1
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.