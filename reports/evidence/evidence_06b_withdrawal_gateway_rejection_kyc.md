# Evidence Report: Copy Trading: Withdrawal Gateway Rejection & KYC Safeguards (✅ PASS)

**Test Identifier:** `evidence_06b_withdrawal_gateway_rejection_kyc`  
**Objective:** Verify server gateway rejection on excessive/invalid withdrawal requests. Tags KYC status and enforces critical safety guard to abort if OTP succeeds.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:58:33.481809` $\rightarrow$ `2026-11-05T14:58:34.623059` (1.14s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower KYC Verification Tagged** | `1` | `1` | ✅ PASS | KYC status: accountVerified=True, kycVerified=1 |
| 2 | **Excessive Withdrawal Rejected by Gateway** | `True` | `True` | ✅ PASS | Server message: 'Insufficient fund. Maximum withdraw is 0.00' |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: KYC Status Verification
- **Action:** `Read portal user accountVerified and redeem kycVerified`
- **Telemetry / Details:** `{"is_account_verified": true, "kyc_verified_code": 1}`

### Step 2: Trigger Over-Limit OTP Request
- **Action:** `POST /client-portal/apiSendWithdrawOtp`
- **Telemetry / Details:** `{"requested_amount": 62249219.32, "method": "USDT TRC20", "sourceId": "account:11041"}`

### Step 3: Gateway Response
- **Action:** `apiSendWithdrawOtp output`
```json
// Server Response:
{
  "status": "fail",
  "message": "Insufficient fund. Maximum withdraw is 0.00"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.