# Evidence Report: Copy Trading: Proportional Equity-Based Lot Sizing with Floating P&L (❌ FAIL)

**Test Identifier:** `evidence_03_equity_based_copy_trade`  
**Objective:** Verify that updating copy method to 'equity' scales follower order lot size proportionally to live equity vs master live equity with active floating P&L. If equity==balance or difference < 1 lot step, marks INCONCLUSIVE.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T16:59:54.113493` $\rightarrow$ `2026-11-05T17:00:01.423385` (7.31s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (0/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Equity vs Balance Lot Differentiation Guard (>= 0.01 lot)** | `>= 0.01 lot difference` | `Delta=0.0 (EqLot=1.1, BalLot=1.1)` | ❌ FAIL | INCONCLUSIVE: Floating P&L did not produce >= 1 lot-step difference. EquityLot=1.1, BalanceLot=1.1, Delta=0.0. MasterFloatingP&L=$0.00. Marking INCONCLUSIVE per spec. |

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

### Step 2: Floating P&L Position Opened
- **Action:** `50.0 Lots BTCUSD placed on Master`
- **Telemetry / Details:** `{"order_id": "58431"}`

### Step 3: Live Balance & Equity Probe
- **Action:** `GET /book/balance.php`
- **Telemetry / Details:** `{"master_balance": 111223744.87, "master_equity": 111223744.87, "master_floating_pnl": 0.0, "follower_balance": 12247746.43, "follower_equity": 12247746.43}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.