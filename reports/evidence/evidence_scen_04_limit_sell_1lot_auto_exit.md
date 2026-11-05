# Evidence Report: Copy Trading: Limit SELL 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Automatic Exit (❌ FAIL)

**Test Identifier:** `evidence_scen_04_limit_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit SELL with trigger 2.0 pts above CMP. Follower replicates 3.00 lots pending. When filled, auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:15:20.972483` $\rightarrow$ `2026-11-05T17:16:25.742832` (64.77s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Pending Limit SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (80303.94) Replicated** | `80303.94` | `80303.94` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Limit SELL Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=limit`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 58738,
    "time": 0.09723782539367676
  },
  "_duration_ms": 284.7,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=1.00&sl=80308.94&target=80296.94&trigger=80303.94&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1232"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.