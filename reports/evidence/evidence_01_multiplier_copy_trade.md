# Evidence Report: Copy Trading: Multiplier-Based Replication (1.00 Master Lot -> 3.00 Follower Lots) (✅ PASS)

**Test Identifier:** `evidence_01_multiplier_copy_trade`  
**Objective:** Verify that placing 1.00 lot X:BTCUSD on Master replicates 3.00 lots to all 5 followers with separate read verification polling via /book/orders.php and simultaneous clean squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:57:08.226895` $\rightarrow$ `2026-11-05T14:57:16.018648` (7.79s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (14/14 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Order Acceptance** | `success` | `success` | ✅ PASS |  |
| 2 | **Master Order Confirmed in Book** | `True` | `True` | ✅ PASS |  |
| 3 | **Follower ctf1 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1468.7ms |
| 4 | **Follower ctf2 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1670.62ms |
| 5 | **Follower ctf3 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 1873.63ms |
| 6 | **Follower ctf4 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 2810.04ms |
| 7 | **Follower ctf5 Replicated Lot** | `3.0` | `3.0` | ✅ PASS | Replication Latency: 3395.98ms |
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
- **Telemetry / Details:** `{"symbol": "X:BTCUSD", "last_price": 80269.63, "sl": "80169.63", "tp": "80369.63"}`

### Step 2: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "55696",
    "intentId": "9db0e42ae03fa901c10196595f7741ab",
    "executionStatus": "queued",
    "fanoutJobId": 6244,
    "fanoutStatus": "queued",
    "requestId": "legacy_7390ee9756c58b61fd1e0894250a81dd",
    "placementReplayProtected": true
  },
  "_duration_ms": 219.55,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=80169.63&target=80369.63&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_473"
}
```

### Step 3: Master Book Snapshot
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"order_id": "55696", "lot": "1", "entry_price": "0"}`

### Step 4: Follower ctf1 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf1", "copied_order_id": "55701", "lot": 3.0, "latency_ms": 1468.7}`

### Step 5: Follower ctf2 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf2", "copied_order_id": "55700", "lot": 3.0, "latency_ms": 1670.62}`

### Step 6: Follower ctf3 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf3", "copied_order_id": "55699", "lot": 3.0, "latency_ms": 1873.63}`

### Step 7: Follower ctf4 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf4", "copied_order_id": "55698", "lot": 3.0, "latency_ms": 2810.04}`

### Step 8: Follower ctf5 Replication
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"follower": "ctf5", "copied_order_id": "55697", "lot": 3.0, "latency_ms": 3395.98}`

### Step 9: Master Squareoff Request
- **Action:** `GET /book/squareoff.php?id=55696`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 55696  Sent to for Closing",
  "data": [],
  "_duration_ms": 264.74
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.