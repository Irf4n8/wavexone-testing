# Evidence Report: Copy Trading: Stop HFT BOTH 1.00 Lot Dual Breakout & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_07_stop_hft_both_1lot_auto_exit`  
**Objective:** Master places Stop HFT BOTH (type=2) with dual BUY and SELL triggers 5.0 pts around CMP. Follower replicates dual 3.00 lot orders. Active leg fills & auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:17:47.159886` $\rightarrow$ `2026-11-05T17:17:57.511078` (10.35s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Dual Order IDs Returned for Stop BOTH** | `2` | `2` | ✅ PASS |  |
| 2 | **Follower Replicated Dual Pending Stop Orders** | `2` | `2` | ✅ PASS |  |
| 3 | **Active Breakout Leg Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 2.55s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Stop HFT BOTH Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=2`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": "58777,58778",
    "time": 0.11959290504455566
  },
  "_duration_ms": 316.88,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=80266.99&targetb=80281.99&triggerb=80276.99&lots=1.00&sls=80276.99&targets=80261.99&triggers=80266.99&symbol=X:BTCUSD&stop_hft_type=2&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1243"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.