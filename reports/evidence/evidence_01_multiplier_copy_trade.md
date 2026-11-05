# Evidence Report: Copy Trading: Multiplier-Based Replication (1.00 Master Lot -> 3.00 Follower Lots) (✅ PASS)

**Test Identifier:** `evidence_01_multiplier_copy_trade`  
**Objective:** Verify that placing 1.00 lot X:BTCUSD on Master replicates 3.00 lots to all 5 followers with separate read verification polling via /book/orders.php and simultaneous clean squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:45:35.298379` $\rightarrow$ `2026-11-05T13:45:42.270435` (6.97s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (14/14 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Order Acceptance** | `success` | `success` | ✅ PASS |  |
| 2 | **Master Order Confirmed in Book** | `True` | `True` | ✅ PASS |  |
| 3 | **Follower ctf1 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1700.46ms |
| 4 | **Follower ctf2 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 2558.24ms |
| 5 | **Follower ctf3 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 2757.89ms |
| 6 | **Follower ctf4 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 2954.38ms |
| 7 | **Follower ctf5 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 3149.88ms |
| 8 | **Master Squareoff Response** | `success` | `success` | ✅ PASS |  |
| 9 | **Master Position Closure Verified** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf1 Order Closure** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf2 Order Closure** | `True` | `True` | ✅ PASS |  |
| 12 | **Follower ctf3 Order Closure** | `True` | `True` | ✅ PASS |  |
| 13 | **Follower ctf4 Order Closure** | `True` | `True` | ✅ PASS |  |
| 14 | **Follower ctf5 Order Closure** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Market Probe
- **Action:** `Fetched live engine price`
- **Telemetry / Details:** `{"symbol": "X:BTCUSD", "last_price": 80450.32, "sl": "80400.32", "tp": "80500.32"}`

### Step 2: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53922",
    "intentId": "04bcad750b05bd62c2e8aae5f6fad98d",
    "executionStatus": "queued",
    "fanoutJobId": 6006,
    "fanoutStatus": "queued",
    "requestId": "legacy_6ca57761c5511cf8bec813a7be9f6f7f",
    "placementReplayProtected": true
  },
  "_duration_ms": 279.27,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=80400.32&target=80500.32&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_214"
}
```

### Step 3: Master Book Snapshot
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"order_id": "53922", "lot": "1", "entry_price": "80451.6"}`

### Step 4: Follower ctf1 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf1", "copied_order_id": "53927", "lot": 3.0, "latency_ms": 1700.46}`

### Step 5: Follower ctf2 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf2", "copied_order_id": "53926", "lot": 3.0, "latency_ms": 2558.24}`

### Step 6: Follower ctf3 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf3", "copied_order_id": "53925", "lot": 3.0, "latency_ms": 2757.89}`

### Step 7: Follower ctf4 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf4", "copied_order_id": "53924", "lot": 3.0, "latency_ms": 2954.38}`

### Step 8: Follower ctf5 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf5", "copied_order_id": "53923", "lot": 3.0, "latency_ms": 3149.88}`

### Step 9: Master Squareoff Request
- **Action:** `GET /book/squareoff.php?id=53922`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 53922  Sent to for Closing",
  "data": [],
  "_duration_ms": 264.29
}
```

### Step 10: Follower ctf1 Closure Verified
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf1", "closed_order_id": "53927", "status": "closed"}`

### Step 11: Follower ctf2 Closure Verified
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf2", "closed_order_id": "53926", "status": "closed"}`

### Step 12: Follower ctf3 Closure Verified
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf3", "closed_order_id": "53925", "status": "closed"}`

### Step 13: Follower ctf4 Closure Verified
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf4", "closed_order_id": "53924", "status": "closed"}`

### Step 14: Follower ctf5 Closure Verified
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf5", "closed_order_id": "53923", "status": "closed"}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.