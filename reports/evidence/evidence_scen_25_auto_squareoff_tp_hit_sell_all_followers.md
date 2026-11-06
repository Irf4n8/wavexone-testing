# Evidence Report: Copy Trading: Auto Squareoff on Take Profit Hit (SELL) Across All 5 Followers (✅ PASS)

**Test Identifier:** `evidence_scen_25_auto_squareoff_tp_hit_sell_all_followers`  
**Objective:** Master places 1.00 whole lot Market SELL with tight Take Profit offset (10 pts below CMP). When market ticks down to TP, broker engine triggers auto squareoff on Master and all 5 followers auto square off synchronously.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:45:18.850275` $\rightarrow$ `2026-11-05T18:46:27.858661` (69.01s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (11/11 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 TP (79596) Propagated** | `79596` | `79596` | ✅ PASS |  |
| 2 | **Follower ctf2 TP (79596) Propagated** | `79596` | `79596` | ✅ PASS |  |
| 3 | **Follower ctf3 TP (79596) Propagated** | `79596` | `79596` | ✅ PASS |  |
| 4 | **Follower ctf4 TP (79596) Propagated** | `79596` | `79596` | ✅ PASS |  |
| 5 | **Follower ctf5 TP (79596) Propagated** | `79596` | `79596` | ✅ PASS |  |
| 6 | **Master Auto Squareoff on SELL TP Hit** | `True` | `True` | ✅ PASS | Closed in 61.07s |
| 7 | **Follower ctf1 Auto Squared Off on Master SELL TP Hit** | `True` | `True` | ✅ PASS |  |
| 8 | **Follower ctf2 Auto Squared Off on Master SELL TP Hit** | `True` | `True` | ✅ PASS |  |
| 9 | **Follower ctf3 Auto Squared Off on Master SELL TP Hit** | `True` | `True` | ✅ PASS |  |
| 10 | **Follower ctf4 Auto Squared Off on Master SELL TP Hit** | `True` | `True` | ✅ PASS |  |
| 11 | **Follower ctf5 Auto Squared Off on Master SELL TP Hit** | `True` | `True` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master 1.00 Lot SELL with TP
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59987",
    "intentId": "42d0d738926a9ba3008f443735a4f40b",
    "executionStatus": "queued",
    "fanoutJobId": 6985,
    "fanoutStatus": "queued",
    "requestId": "legacy_7b380e2a66c13713d1a6eb0f0f651412",
    "placementReplayProtected": true
  },
  "_duration_ms": 245.55,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=80106.71&target=79596.71&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1494"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.