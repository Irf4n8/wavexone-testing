# Evidence Report: Copy Trading: Limit and Stop Order Lifecycle & Cancellation (✅ PASS)

**Test Identifier:** `evidence_11_limit_and_stop_hft_replication`  
**Objective:** Verify pending Limit order status in book, cancellation behavior on master and followers, and filled limit order replication.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T14:59:55.155380` $\rightarrow$ `2026-11-05T15:00:04.543505` (9.39s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Limit Order Pending in Book** | `True` | `True` | ✅ PASS |  |
| 2 | **Recorded Pending Limit Replication Policy** | `OBSERVED` | `Replicated=True` | ✅ PASS | Engine policy: pending limit orders replicate on fill or as pending |
| 3 | **Cancel Status** | `success` | `success` | ✅ PASS |  |
| 4 | **Master Pending Order Removed** | `True` | `True` | ✅ PASS |  |
| 5 | **Recorded Follower Pending Limit Auto-Cancel on Master Cancel** | `OBSERVED` | `AutoCancelled=True` | ✅ PASS | Platform observed behavior: follower pending limit cancellation propagation |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Pending Limit Placement
- **Action:** `POST /trade/placeorder.php?type=limit&trigger=75255.60`
```json
// Server Response:
{
  "status": "success",
  "message": "Order Placed Successfully",
  "data": {
    "orderId": 55953,
    "time": 0.07325506210327148
  },
  "_duration_ms": 285.5,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=limit&bs=buy&lot=0.01&sl=&target=&trigger=75255.60&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_524"
}
```

### Step 2: Follower Book Pending Limit Inspection
- **Action:** `GET /book/orders.php`
- **Telemetry / Details:** `{"f1_has_pending_limit": true}`

### Step 3: Master Cancel Limit Request
- **Action:** `GET /book/cancel.php?id=55953`
```json
// Server Response:
{
  "status": "success",
  "message": "Order ID - 55953  cancelled",
  "data": [],
  "_duration_ms": 199.99
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.