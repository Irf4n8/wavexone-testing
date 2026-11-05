# Evidence Report: Copy Trading: Stop HFT SELL 1.00 Lot with Trigger, TP/SL & Automatic Exit (✅ PASS)

**Test Identifier:** `evidence_scen_06_stop_hft_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Stop HFT SELL (type=0) with trigger 5.0 pts below CMP. Follower replicates 3.00 lots. Triggers into fill, then auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:17:32.905269` $\rightarrow$ `2026-11-05T17:17:45.972361` (13.07s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower Replicated 3.00 Lots Pending Stop SELL** | `3.0` | `3.0` | ✅ PASS |  |
| 2 | **Follower Trigger (80273.61) Replicated** | `80273.61` | `80273.61` | ✅ PASS |  |
| 3 | **Stop HFT SELL Triggered & Filled into Position** | `True` | `True` | ✅ PASS |  |
| 4 | **Master Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Order auto-closed in 6.1s without manual close. |
| 5 | **Follower Synchronous Automatic Exit via TP/SL Hit** | `True` | `True` | ✅ PASS | Follower must auto-close when Master position is terminated by TP/SL hit. |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Stop HFT SELL Placement (1.00 Lot)
- **Action:** `POST /trade/placeorder.php?type=stop&stop_hft_type=0`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 58764,
    "time": 0.05817890167236328
  },
  "_duration_ms": 245.05,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=stop&bs=sell&lotb=1.00&slb=&targetb=&triggerb=&lots=1.00&sls=80283.61&targets=80268.61&triggers=80273.61&symbol=X:BTCUSD&stop_hft_type=0&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1240"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.