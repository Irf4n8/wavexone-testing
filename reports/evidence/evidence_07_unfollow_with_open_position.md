# Evidence Report: Copy Trading: Unfollow Master with Active Open Position (⚠️ UNVERIFIED vs spec)

**Test Identifier:** `evidence_07_unfollow_with_open_position`  
**Objective:** Investigate and record platform behavior when a follower unfollows master while trade is active. Records whether position stays open or auto-closes, and whether master squareoff closes or orphans it. Tagged UNVERIFIED vs spec.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:58:37.310725` $\rightarrow$ `2026-11-05T14:58:46.240817` (8.93s)  
**Overall Verification Status:** **⚠️ UNVERIFIED vs spec**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Recorded Behavior Upon Unfollow (Tagged UNVERIFIED)** | `RECORDED` | `STAYED_OPEN` | ✅ PASS | Follower position STAYED_OPEN when unfollow executed |
| 2 | **Recorded Behavior Upon Master Close (Tagged UNVERIFIED)** | `RECORDED` | `CLOSED_WITH_MASTER` | ✅ PASS | Follower position CLOSED_WITH_MASTER after master squareoff |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Positions Opened
- **Action:** `Active orders verified before unfollow`
- **Telemetry / Details:** `{"master_oid": "55804", "f1_oid": "55815"}`

### Step 2: Follower Unfollows with Open Trade
- **Action:** `GET /user/follow.php?type=unfollow`
```json
// Server Response:
{
  "status": "success",
  "message": "Successfully unfollowed to this user",
  "data": []
}
```

### Step 3: Observed Behavior Upon Unfollow
- **Action:** `Follower trade status: STAYED_OPEN`
- **Telemetry / Details:** `{"behavior_on_unfollow": "STAYED_OPEN", "f1_orders": [{"id": "55815", "symbol": "X:BTCUSD", "formated_symbol": "BTCUSD", "pair": "xxx", "time": "2026-11-05 09:28:38", "trigger": "0", "type": "market", "lot": "3", "bs": "BUY", "sl": "---", "tp": "---", "avg": "80258.4", "t_swap": "0.00", "commission": "0.00", "status": "open", "partiallot": "---", "follower_placement": null, "provider_symbol": "X:BTCUSD", "display_symbol": "X:BTCUSD"}]}`

### Step 4: Observed Behavior Upon Master Squareoff
- **Action:** `Follower trade status after master close: CLOSED_WITH_MASTER`
- **Telemetry / Details:** `{"behavior_after_master_close": "CLOSED_WITH_MASTER", "f1_orders": []}`

### Step 5: Re-Follow Master
- **Action:** `Restored follower connection`
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