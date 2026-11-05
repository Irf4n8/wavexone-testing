# Evidence Report: Copy Trading: Proportional Equity-Based Lot Sizing (✅ PASS)

**Test Identifier:** `evidence_03_equity_based_copy_trade`  
**Objective:** Verify that updating copy method to 'equity' scales follower order lot size proportionally to follower live equity vs. master live equity.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:45:49.115787` $\rightarrow$ `2026-11-05T13:45:56.035101` (6.92s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Method Update Status** | `success` | `success` | ✅ PASS |  |
| 2 | **Equity Proportional Lot Match** | `0.11` | `0.11` | ✅ PASS | Scaled accurately from equity ratio 0.1099 |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Update Copy Method to Equity
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
- **Action:** `Computed expected equity scaling`
- **Telemetry / Details:** `{"master_equity": 111198232.42, "follower_equity": 12223200.54, "ratio": 0.10992261544079676, "expected_lot": 0.11}`

### Step 3: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53934",
    "intentId": "1edd2b81cf8b97573a182ca30c8510d3",
    "executionStatus": "queued",
    "fanoutJobId": 6008,
    "fanoutStatus": "queued",
    "requestId": "legacy_fc603cb6c882a8844d24e1d995cd036b",
    "placementReplayProtected": true
  },
  "_duration_ms": 251.87,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_218"
}
```

### Step 4: Follower Order Snapshot
- **Action:** `GET /book/orders.php?snapshot=1`
- **Telemetry / Details:** `{"order_id": "53939", "actual_lot": 0.11, "expected_lot": 0.11}`

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