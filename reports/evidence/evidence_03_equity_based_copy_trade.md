# Evidence Report: Copy Trading: Proportional Equity-Based Lot Sizing with Floating P&L (⚠️ INCONCLUSIVE)

**Test Identifier:** `evidence_03_equity_based_copy_trade`  
**Objective:** Verify that updating copy method to 'equity' scales follower order lot size proportionally to live equity vs master live equity with active floating P&L. If equity==balance or difference < 1 lot step, marks INCONCLUSIVE.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T15:06:29.191154` $\rightarrow$ `2026-11-05T15:06:41.801940` (12.61s)  
**Overall Verification Status:** **⚠️ INCONCLUSIVE**  
**Error Details:** `Floating P&L divergence insufficient: lot_diff=0.0`  

---

## 📊 Verification Assertions (0/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Equity Differs From Balance by >= 1 Lot Step** | `>= 0.01` | `0.0` | ❌ FAIL | Marked INCONCLUSIVE per spec: insufficient equity divergence |

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

### Step 2: Live Balance & Equity Probe
- **Action:** `GET /book/balance.php`
- **Telemetry / Details:** `{"master_balance": 111223988.87, "master_equity": 111223988.87, "master_floating_pnl": 0.0, "follower_balance": 12248902.03, "follower_equity": 12248902.03}`

### Step 3: Lot Scaling Computation
- **Action:** `Calculated equity vs balance expected lots`
- **Telemetry / Details:** `{"test_order_lot": 5.0, "expected_equity_lot": 0.55, "expected_balance_lot": 0.55, "lot_difference": 0.0}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.