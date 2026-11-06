# Evidence Report: Multiplier Mode: Market SELL 1.00 Lot (Auto-Exit) (❌ FAIL)

**Test Identifier:** `evidence_scen_02_mult_market_sell_1lot_auto_exit`  
**Objective:** Master places 1.00 whole lot Market SELL with tight TP/SL. Follower replicates 3.00 lots (3.0x). Position auto-exits via TP/SL.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:26:52.169059` $\rightarrow$ `2026-11-05T18:27:03.680732` (11.51s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (1/1 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Placed 1.00 Whole Lot (No Decimals)** | `1.0` | `1.0` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Multiplier Mode: Market SELL 1.00 Lot (Auto-Exit) Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "59691",
    "intentId": "fe5c7fcb2ac0a7ef90fb4eeacf0d1ef8",
    "executionStatus": "queued",
    "fanoutJobId": 6958,
    "fanoutStatus": "queued",
    "requestId": "legacy_5c5e5eeab37b2e8a795dc6591097558a",
    "placementReplayProtected": true
  },
  "_duration_ms": 293.13,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=sell&lot=1.00&sl=79631.74&target=79615.74&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_1399"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.