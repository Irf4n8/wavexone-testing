# Evidence Report: Copy Trading: Auto Squareoff on Take Profit Hit Across All 5 Followers (✅ PASS)

**Test Identifier:** `evidence_scen_22_auto_squareoff_tp_hit_all_followers`  
**Objective:** Master places 1.00 whole lot Market BUY with tight Take Profit offset (10 pts). When market ticks and hits TP, brokerage engine triggers auto squareoff on Master and all 5 followers auto square off synchronously.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:44:01.683847` $\rightarrow$ `2026-11-05T18:44:26.751649` (25.07s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (11/11 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 TP (79574) Propagated** | `79574` | `79574` | ✅ PASS |  |
| 2 | **Follower ctf2 TP (79574) Propagated** | `79574` | `79574` | ✅ PASS |  |
| 3 | **Follower ctf3 TP (79574) Propagated** | `79574` | `79574` | ✅ PASS |  |
| 4 | **Follower ctf4 TP (79574) Propagated** | `79574` | `79574` | ✅ PASS |  |
| 5 | **Follower ctf5 TP (79574) Propagated** | `79574` | `79574` | ✅ PASS |  |
| 6 | **Master Auto Squareoff on TP Hit** | `True` | `True` | ✅ PASS | Closed in 16.86s |
| 7 | **Follower ctf1 Auto Squared Off on Master TP Hit** | `True` | `True` | ✅ PASS |  |
| 8 | **Follower ctf2 Auto Squared Off on Master TP Hit** | `True` | `True` | ✅ PASS |  |
| 9 | **Follower ctf3 Auto Squared Off on Master TP Hit** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf4 Auto Squared Off on Master TP Hit** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf5 Auto Squared Off on Master TP Hit** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master 1.00 Lot Placement with TP
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59969",
    "intentId": "25296bda3ee59b0aa455c25195802af9",
    "executionStatus": "queued",
    "fanoutJobId": 6982,
    "fanoutStatus": "queued",
    "requestId": "legacy_f2113d72dcf1741ebe997c9bf849558f",
    "placementReplayProtected": true
  },
  "_duration_ms": 229.31,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=79064.25&target=79574.25&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1487"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.