# Evidence Report: Copy Trading: Unfollow Halts Replication & Re-Follow Restores Service (✅ PASS)

**Test Identifier:** `evidence_04_unfollow_refollow_lifecycle`  
**Objective:** Verify that unfollowing stops trade replication to that follower while peer followers continue copying, and re-following immediately resumes normal replication.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:00:03.766012` $\rightarrow$ `2026-11-05T17:00:26.522332` (22.76s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower 1 Did NOT Receive Order while Unfollowed** | `0` | `0` | ✅ PASS |  |
| 2 | **Peer ctf2 Received Order During F1 Unfollow** | `3.0` | `3.0` | ✅ PASS |  |
| 3 | **Peer ctf3 Received Order During F1 Unfollow** | `3.0` | `3.0` | ✅ PASS |  |
| 4 | **Peer ctf4 Received Order During F1 Unfollow** | `3.0` | `3.0` | ✅ PASS |  |
| 5 | **Peer ctf5 Received Order During F1 Unfollow** | `3.0` | `3.0` | ✅ PASS |  |
| 6 | **Follower 1 Re-established Replication (3.00 Lots)** | `3.0` | `3.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Follower 1 Unfollow Request
- **Action:** `GET /user/follow.php?follow=1060&type=unfollow`
```json
// Server Response:
{
  "status": "success",
  "message": "Successfully unfollowed to this user",
  "data": []
}
```

### Step 2: Follower 1 Re-follow Request
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

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.