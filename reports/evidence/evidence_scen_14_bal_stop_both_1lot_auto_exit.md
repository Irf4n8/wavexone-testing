# Evidence Report: Balance Mode: Stop HFT BOTH 1.00 Lot (Dual Breakout & Auto-Exit) (❌ FAIL)

**Test Identifier:** `evidence_scen_14_bal_stop_both_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BOTH (type=2) with dual triggers. Follower replicates dual balance-scaled lots. Active breakout leg fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:32:39.569346` $\rightarrow$ `2026-11-05T18:33:09.338299` (29.77s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (4/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Dual Order IDs Returned for Stop BOTH** | `2` | `2` | ✅ PASS |  |
| 2 | **Follower Replicated Dual Stop Orders (0.11 lots)** | `2` | `2` | ✅ PASS |  |
| 3 | **Active Breakout Leg Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 4.99s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `False` | ❌ FAIL | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Balance Mode: Stop HFT BOTH 1.00 Lot (Dual Breakout & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": "59812,59813",
    "time": 0.0569300651550293
  },
  "_duration_ms": 269.28,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=79638.68&targetb=79654.68&triggerb=79646.68&lots=1.00&sls=79646.68&targets=79630.68&triggers=79638.68&symbol=X:BTCUSD&stop_hft_type=2&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1437"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.