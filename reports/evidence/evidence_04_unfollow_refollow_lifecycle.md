# Evidence Report: Copy Trading: Unfollow and Re-Follow Lifecycle Verification (✅ PASS)

**Test Identifier:** `evidence_04_unfollow_refollow_lifecycle`  
**Objective:** Verify that unfollowing a master immediately halts trade replication while active peers continue copying, and re-following the master immediately restores real-time trade copying.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:45:56.038516` $\rightarrow$ `2026-11-05T13:46:14.177442` (18.14s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (8/8 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Unfollow Status** | `success` | `success` | ✅ PASS |  |
| 2 | **Unfollowed Follower Receives 0 Trades** | `0` | `0` | ✅ PASS | Replication halted for ctf1 while unfollowed |
| 3 | **Active Peer ctf2 Copied Trade** | `True` | `True` | ✅ PASS |  |
| 4 | **Active Peer ctf3 Copied Trade** | `True` | `True` | ✅ PASS |  |
| 5 | **Active Peer ctf4 Copied Trade** | `True` | `True` | ✅ PASS |  |
| 6 | **Active Peer ctf5 Copied Trade** | `True` | `True` | ✅ PASS |  |
| 7 | **Re-Follow Status** | `success` | `success` | ✅ PASS |  |
| 8 | **Follower Resumed Copying After Re-Follow** | `True` | `True` | ✅ PASS | Replicated Order ID: 53950 |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Unfollow Master Request
- **Action:** `GET /user/follow.php?follow=1060&type=unfollow`
```json
// Server Response:
{
  "status": "success",
  "message": "Successfully unfollowed to this user",
  "data": []
}
```

### Step 2: Master Order Placement (Trade 1)
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53940",
    "intentId": "33183cdd8879e58eebafbf6c0daf8505",
    "executionStatus": "queued",
    "fanoutJobId": 6009,
    "fanoutStatus": "queued",
    "requestId": "legacy_b2a27756960e1c21ae5640b24fee4a5a",
    "placementReplayProtected": true
  },
  "_duration_ms": 268.41,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_220"
}
```

### Step 3: Re-Follow Master Request
- **Action:** `GET /user/follow.php?follow=1060&type=follow&method=multiplier&value=3.0`
```json
// Server Response:
{
  "status": "success",
  "message": "Successfully followed this user. Master profit share: 10.00%",
  "data": {
    "profit_share": 10
  }
}
```

### Step 4: Master Order Placement (Trade 2)
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53945",
    "intentId": "cda218daa8868f0590081270967a3a0b",
    "executionStatus": "queued",
    "fanoutJobId": 6010,
    "fanoutStatus": "queued",
    "requestId": "legacy_6478c1613c98bcddce89787be7c048cf",
    "placementReplayProtected": true
  },
  "_duration_ms": 258.88,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_222"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.