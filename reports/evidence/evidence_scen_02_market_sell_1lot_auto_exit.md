# Evidence Report: Copy Trading: Market SELL 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit (❌ FAIL)

**Test Identifier:** `evidence_scen_02_market_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market SELL with tight TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:33:19.397182` $\rightarrow$ `2026-11-05T17:33:31.283149` (11.89s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Market SELL Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59098",
    "intentId": "9fb29c784091abc6efdf1babd086f759",
    "executionStatus": "queued",
    "fanoutJobId": 6871,
    "fanoutStatus": "queued",
    "requestId": "legacy_c80a8a402e15b8d7414e0482e37ed1ca",
    "placementReplayProtected": true
  },
  "_duration_ms": 537.29,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=80145.80&target=80129.80&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1332"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.