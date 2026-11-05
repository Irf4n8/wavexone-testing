# Evidence Report: Copy Trading Matrix: Multiplier Mode - Market SELL with TP/SL (✅ PASS)

**Test Identifier:** `evidence_matrix_02_multiplier_market_sell_tpsl`  
**Objective:** Verify that placing 1.00 lot Market SELL with explicit TP and SL replicates 3.00 lots SELL to follower with identical TP/SL and clean squareoff.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:47:04.055269` $\rightarrow$ `2026-11-05T15:47:13.363542` (9.31s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Master Book SL Matches Expected** | `80827` | `80827` | ✅ PASS |  |
| 3 | **Master Book TP Matches Expected** | `79827` | `79827` | ✅ PASS |  |
| 4 | **Follower Book SL Replicated** | `80827` | `80827` | ✅ PASS |  |
| 5 | **Follower Book TP Replicated** | `79827` | `79827` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Place Market SELL with TP/SL
- **Action:** `POST /trade/placeorder.php?type=market&bs=sell&sl=80827.95&target=79827.95`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "57399",
    "intentId": "238b67d19a05578f4b858f282d446c92",
    "executionStatus": "queued",
    "fanoutJobId": 6515,
    "fanoutStatus": "queued",
    "requestId": "legacy_4efa25d3e534563b895610c2587bbcb9",
    "placementReplayProtected": true
  },
  "_duration_ms": 287.86,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=80827.95&target=79827.95&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_830"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.