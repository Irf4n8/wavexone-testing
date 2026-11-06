# Evidence Report: Multiplier Mode: Stop HFT BUY 1.00 Lot (Trigger & Auto-Exit) (✅ PASS)

**Test Identifier:** `evidence_scen_05_mult_stop_buy_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT BUY (type=1) with trigger 4.0 pts above CMP. Follower replicates 3.00 lots. Fills and auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:27:46.586792` $\rightarrow$ `2026-11-05T18:28:31.716190` (45.13s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.0 Lots Pending Stop BUY** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (79565.98) Replicated** | `79565.98` | `79565.98` | ✅ PASS |  |
| 3 | **Stop BUY Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 0.2s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Stop HFT BUY 1.00 Lot (Trigger & Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 59729,
    "time": 0.07268285751342773
  },
  "_duration_ms": 288.53,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=buy&lotb=1.00&slb=79557.98&targetb=79573.98&triggerb=79565.98&lots=1.00&sls=&targets=&triggers=&symbol=X:BTCUSD&stop_hft_type=1&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1406"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.