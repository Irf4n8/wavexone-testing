# Evidence Report: Copy Trading: Proportional Balance-Based Lot Sizing (✅ PASS)

**Test Identifier:** `evidence_02_balance_based_copy_trade`  
**Objective:** Verify that updating copy method to 'balance' scales follower order lot size proportionally to follower balance vs. master balance.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:45:42.274357` $\rightarrow$ `2026-11-05T13:45:49.110981` (6.84s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Method Update Status** | `success` | `success` | ✅ PASS |  |
| 2 | **Balance Proportional Lot Match** | `0.11` | `0.11` | ✅ PASS | Scaled accurately from ratio 0.1099 |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Update Copy Method to Balance
- **Action:** `GET /user/updateCopyTradingMethod.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Update Successfully",
  "data": []
}
```

### Step 2: Ratio Calculation
- **Action:** `Computed expected balance scaling`
- **Telemetry / Details:** `{"master_balance": 111198239.55, "follower_balance": 12223200.72, "ratio": 0.1099226100113201, "expected_lot": 0.11}`

### Step 3: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53928",
    "intentId": "759aa249e77e9fde9f0e160c2e3dd78e",
    "executionStatus": "queued",
    "fanoutJobId": 6007,
    "fanoutStatus": "queued",
    "requestId": "legacy_15f14d84c0e4ba454797d83a4f8ba8ad",
    "placementReplayProtected": true
  },
  "_duration_ms": 248.66,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_216"
}
```

### Step 4: Follower Order Snapshot
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"order_id": "53933", "actual_lot": 0.11, "expected_lot": 0.11}`

### Step 5: Restore Multiplier Method
- **Action:** `GET /user/updateCopyTradingMethod.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Update Successfully",
  "data": []
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.