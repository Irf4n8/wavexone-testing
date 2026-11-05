# Evidence Report: Copy Trading: apiRedeemConfig Open Orders Ratio Safeguard (✅ PASS)

**Test Identifier:** `evidence_06a_withdrawal_redeem_config`  
**Objective:** Verify that apiRedeemConfig correctly increments open_orders and caps withdrawable ratio to 0.8 when copy trading positions are open, and restores ratio to 1.0 upon closure.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:58:21.138927` $\rightarrow$ `2026-11-05T14:58:31.079695` (9.94s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (6/6 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Pre-Trade Open Orders is 0** | `0` | `0` | ✅ PASS |  |
| 2 | **Pre-Trade Ratio is 1.0** | `1.0` | `1.0` | ✅ PASS |  |
| 3 | **In-Trade Open Orders Detected (>=1)** | `>=1` | `1` | ✅ PASS |  |
| 4 | **In-Trade Withdrawable Ratio Capped to 0.8** | `0.8` | `0.8` | ✅ PASS | Engine preserves margin by capping withdrawal ratio to 80% |
| 5 | **Post-Trade Open Orders Restored to 0** | `0` | `0` | ✅ PASS |  |
| 6 | **Post-Trade Ratio Restored to 1.0** | `1.0` | `1.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Pre-Trade Redeem Config Query
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 12249243.45,
  "open_orders": 0,
  "ratio": 1,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

### Step 2: In-Trade Redeem Config Query
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 9799009.54,
  "open_orders": 1,
  "ratio": 0.8,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

### Step 3: Post-Trade Redeem Config Query
- **Action:** `GET /client-portal/apiRedeemConfig`
```json
// Server Response:
{
  "available": 12249219.32,
  "open_orders": 0,
  "ratio": 1,
  "pending_withdraw": 0,
  "pamm_follower_reserve": 0
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.