# Evidence Report: Copy Trading: Auto Squareoff on Stop Loss Hit (SELL) Across All 5 Followers (✅ PASS)

**Test Identifier:** `evidence_scen_26_auto_squareoff_sl_hit_sell_all_followers`  
**Objective:** Master places 1.00 whole lot Market SELL with tight Stop Loss offset (10 pts above CMP). When market ticks up to SL, broker engine triggers auto squareoff on Master and all 5 followers auto square off synchronously.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:46:31.512983` $\rightarrow$ `2026-11-05T18:48:04.105833` (92.59s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (11/11 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 SL (79588) Propagated** | `79588` | `79588` | ✅ PASS |  |
| 2 | **Follower ctf2 SL (79588) Propagated** | `79588` | `79588` | ✅ PASS |  |
| 3 | **Follower ctf3 SL (79588) Propagated** | `79588` | `79588` | ✅ PASS |  |
| 4 | **Follower ctf4 SL (79588) Propagated** | `79588` | `79588` | ✅ PASS |  |
| 5 | **Follower ctf5 SL (79588) Propagated** | `79588` | `79588` | ✅ PASS |  |
| 6 | **Master Auto Squareoff on SELL SL Hit** | `True` | `True` | ✅ PASS | Closed in 80.03s |
| 7 | **Follower ctf1 Auto Squared Off on Master SELL SL Hit** | `True` | `True` | ✅ PASS |  |
| 8 | **Follower ctf2 Auto Squared Off on Master SELL SL Hit** | `True` | `True` | ✅ PASS |  |
| 9 | **Follower ctf3 Auto Squared Off on Master SELL SL Hit** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf4 Auto Squared Off on Master SELL SL Hit** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf5 Auto Squared Off on Master SELL SL Hit** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master 1.00 Lot SELL with SL
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59993",
    "intentId": "0eab81d7054cfa35ec875b1dc468c0fe",
    "executionStatus": "queued",
    "fanoutJobId": 6986,
    "fanoutStatus": "queued",
    "requestId": "legacy_b46cbb50284eec9168b5892ad81c61f1",
    "placementReplayProtected": true
  },
  "_duration_ms": 224.58,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=79588.61&target=79078.61&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1496"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.