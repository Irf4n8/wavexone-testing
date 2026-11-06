# Evidence Report: Multiplier Mode: Stop HFT BOTH 1.00 Lot (Dual Breakout & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_07_mult_stop_both_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BOTH (type=2) with dual breakout triggers. Follower replicates dual 3.00 lots. Active leg fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:29:56.582121` $\rightarrow$ `2026-11-05T18:30:26.706327` (30.12s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Dual Order IDs Returned for Stop BOTH** | `2` | `2` | ✅ PASS |  |
| 2 | **Follower Replicated Dual Stop Orders (3.0 lots)** | `2` | `2` | ✅ PASS |  |
| 3 | **Active Breakout Leg Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 0.21s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Stop HFT BOTH 1.00 Lot (Dual Breakout & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": "59752,59753",
    "time": 0.06702399253845215
  },
  "_duration_ms": 276.68,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=79581.41&targetb=79597.41&triggerb=79589.41&lots=1.00&sls=79589.41&targets=79573.41&triggers=79581.41&symbol=X:BTCUSD&stop_hft_type=2&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1415"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.