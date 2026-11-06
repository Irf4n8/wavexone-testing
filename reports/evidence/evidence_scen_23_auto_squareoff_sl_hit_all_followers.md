# Evidence Report: Copy Trading: Auto Squareoff on Stop Loss Hit Across All 5 Followers (✅ PASS)

**Test Identifier:** `evidence_scen_23_auto_squareoff_sl_hit_all_followers`  
**Objective:** Master places 1.00 whole lot Market BUY with tight Stop Loss offset (10 pts). When market ticks and hits SL, brokerage engine triggers auto squareoff on Master and all 5 followers auto square off synchronously.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:44:30.396221` $\rightarrow$ `2026-11-05T18:44:40.768785` (10.37s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (11/11 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 SL (79567) Propagated** | `79567` | `79567` | ✅ PASS |  |
| 2 | **Follower ctf2 SL (79567) Propagated** | `79567` | `79567` | ✅ PASS |  |
| 3 | **Follower ctf3 SL (79567) Propagated** | `79567` | `79567` | ✅ PASS |  |
| 4 | **Follower ctf4 SL (79567) Propagated** | `79567` | `79567` | ✅ PASS |  |
| 5 | **Follower ctf5 SL (79567) Propagated** | `79567` | `79567` | ✅ PASS |  |
| 6 | **Master Auto Squareoff on SL Hit** | `True` | `True` | ✅ PASS | Closed in 2.55s |
| 7 | **Follower ctf1 Auto Squared Off on Master SL Hit** | `True` | `True` | ✅ PASS |  |
| 8 | **Follower ctf2 Auto Squared Off on Master SL Hit** | `True` | `True` | ✅ PASS |  |
| 9 | **Follower ctf3 Auto Squared Off on Master SL Hit** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf4 Auto Squared Off on Master SL Hit** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf5 Auto Squared Off on Master SL Hit** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master 1.00 Lot Placement with SL
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59975",
    "intentId": "f1de8e66bb08e487f8ebd634fd70f236",
    "executionStatus": "queued",
    "fanoutJobId": 6983,
    "fanoutStatus": "queued",
    "requestId": "legacy_a6c111301bdb6f6c2f6820ede04cd155",
    "placementReplayProtected": true
  },
  "_duration_ms": 229.7,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=79567.30&target=80077.30&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1489"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.