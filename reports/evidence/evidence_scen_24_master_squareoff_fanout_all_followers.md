# Evidence Report: Copy Trading: Master Squareoff Triggers Simultaneous Auto Squareoff Across All 5 Followers (✅ PASS)

**Test Identifier:** `evidence_scen_24_master_squareoff_fanout_all_followers`  
**Objective:** Master places 1.00 whole lot Market BUY. All 5 followers replicate 3.00 lots. Master calls /book/squareoff.php. Engine automatically fans out squareoff to all 5 followers simultaneously.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:44:44.396212` $\rightarrow$ `2026-11-05T18:44:52.398086` (8.0s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (7/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **All 5 Followers Replicated 3.00 Lots** | `5` | `5` | ✅ PASS |  |
| 2 | **Follower ctf1 Auto Squared Off via Fanout** | `True` | `True` | ✅ PASS |  |
| 3 | **Follower ctf2 Auto Squared Off via Fanout** | `True` | `True` | ✅ PASS |  |
| 4 | **Follower ctf3 Auto Squared Off via Fanout** | `True` | `True` | ✅ PASS |  |
| 5 | **Follower ctf4 Auto Squared Off via Fanout** | `True` | `True` | ✅ PASS |  |
| 6 | **Follower ctf5 Auto Squared Off via Fanout** | `True` | `True` | ✅ PASS |  |
| 7 | **Fanout Squareoff Latency (<3.0s)** | `3.0` | `2.933` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master 1.00 Lot Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59981",
    "intentId": "1622db6b0dbbc3a0de2d719044998af2",
    "executionStatus": "queued",
    "fanoutJobId": 6984,
    "fanoutStatus": "queued",
    "requestId": "legacy_f6500102030c249546246528c32e0807",
    "placementReplayProtected": true
  },
  "_duration_ms": 216.56,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1490"
}
```

### Step 2: Master Squareoff Request
- **Action:** `GET /book/squareoff.php?id=59981`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 59981  Sent to for Closing",
  "data": [],
  "_duration_ms": 229.43
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.