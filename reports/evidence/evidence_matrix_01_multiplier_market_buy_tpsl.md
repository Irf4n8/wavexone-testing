# Evidence Report: Copy Trading Matrix: Multiplier Mode - Market BUY with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_01_multiplier_market_buy_tpsl`  
**Objective:** Verify that placing 1.00 lot Market BUY with explicit TP and SL replicates 3.00 lots to follower with identical TP/SL and clean squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:46:52.561678` $\rightarrow$ `2026-11-05T15:47:01.597439` (9.04s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `79835` | `79835` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `80835` | `80835` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `79835` | `79835` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `80835` | `80835` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Market BUY with TP/SL
- **Action:** `POST /trade/placeorder.php?type=market&bs=buy&sl=79835.52&target=80835.52`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "57393",
    "intentId": "5c96df46f34e601c818169469ca572d8",
    "executionStatus": "queued",
    "fanoutJobId": 6514,
    "fanoutStatus": "queued",
    "requestId": "legacy_75a64474dad810f16e3538f94cd10445",
    "placementReplayProtected": true
  },
  "_duration_ms": 233.06,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=79835.52&target=80835.52&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_827"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.