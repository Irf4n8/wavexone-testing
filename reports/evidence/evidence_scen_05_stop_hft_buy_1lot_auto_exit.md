# Evidence Report: Copy Trading: Stop HFT BUY 1.00 Lot with Trigger, TP/SL & Automatic Exit (❌ FAIL)

**Test Identifier:** `evidence_scen_05_stop_hft_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BUY (type=1) with trigger 4.0 pts above CMP. Follower replicates 3.00 lots. Triggers into fill, then auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:30:28.301087` $\rightarrow$ `2026-11-05T17:30:34.817899` (6.52s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (0/0 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Stop HFT BUY Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=1`
```json
// Server Response:
{
  "status": "fail",
  "message": "Trading temporarily unavailable. Please try again shortly.",
  "data": [],
  "_duration_ms": 192.79,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=80446.00&targetb=80462.00&triggerb=80454.00&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1307"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.