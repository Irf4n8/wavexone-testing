# Evidence Report: Copy Trading: Limit SELL 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Automatic Exit (❌ FAIL)

**Test Identifier:** `evidence_scen_04_limit_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Limit SELL with trigger 1.5 pts above CMP. Follower replicates 3.00 lots pending. When filled, auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:30:04.721794` $\rightarrow$ `2026-11-05T17:30:27.051306` (22.33s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (0/0 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Limit SELL Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=limit`
```json
// Server Response:
{
  "status": "fail",
  "message": "Trading temporarily unavailable. Please try again shortly.",
  "data": [],
  "_duration_ms": 199.27,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=sell&lot=1.00&sl=80459.50&target=80443.50&trigger=80451.50&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1301"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.