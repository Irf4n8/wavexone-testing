# Evidence Report: Copy Trading: Withdrawal Limits and Open-Order Margin Safeguards (✅ PASS)

**Test Identifier:** `evidence_06_withdrawal_limits_open_orders`  
**Objective:** Verify that available withdrawable funds cap when open orders exist to preserve required margin and that excessive withdrawal attempts are strictly rejected.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:46:25.292991` $\rightarrow$ `2026-11-05T13:46:36.372557` (11.08s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (7/7 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Pre-Trade Open Orders is 0** | `0` | `0` | ✅ PASS |  |
| 2 | **Pre-Trade Available Withdrawable Positive** | `>0` | `12223128.73` | ✅ PASS |  |
| 3 | **In-Trade Open Orders Detected** | `>=1` | `1` | ✅ PASS | Open position successfully detected by withdrawal subsystem |
| 4 | **Withdrawable Ratio Capped** | `0.8` | `0.8` | ✅ PASS | Platform capped available funds to 80% to protect margin |
| 5 | **Excessive Withdrawal Rejected by Server** | `True` | `True` | ✅ PASS | Server rejection message: 'Insufficient fund. Maximum withdraw is 0.00' |
| 6 | **Post-Trade Open Orders Restored to 0** | `0` | `0` | ✅ PASS |  |
| 7 | **Withdrawable Ratio Restored to 1.0** | `1.0` | `1.0` | ✅ PASS | Full available withdrawal restored: $12,223,079.84 |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Pre-Trade Withdraw Limit Check
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 12223128.73,
  "open_orders": 0,
  "ratio": 1,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

### Step 2: Master Order Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53957",
    "intentId": "36f651718d825b7ff2058ce0d635e337",
    "executionStatus": "queued",
    "fanoutJobId": 6012,
    "fanoutStatus": "queued",
    "requestId": "legacy_6347cde66f315b06e7ec5bb14d582f0c",
    "placementReplayProtected": true
  },
  "_duration_ms": 267.15,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_226"
}
```

### Step 3: In-Trade Withdraw Limit Check
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 9778116.86,
  "open_orders": 1,
  "ratio": 0.8,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

### Step 4: Excessive Withdrawal Attempt
- **Action:** `POST /client-portal/apiSendWithdrawOtp`
```json
// Server Response:
{
  "status": "fail",
  "message": "Insufficient fund. Maximum withdraw is 0.00"
}
```

### Step 5: Post-Trade Withdraw Limit Check
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 12223079.84,
  "open_orders": 0,
  "ratio": 1,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.