# Evidence Report: Copy Trading: Batch Concurrent Master Squareoff Fans Out Auto Squareoff to All Followers (❌ FAIL)

**Test Identifier:** `evidence_scen_28_batch_concurrent_auto_squareoff`  
**Objective:** Master places 3 concurrent 1.00 lot orders. All 5 followers replicate all 3 orders. Master squares off all 3 positions in batch. Broker fanout engine auto squares off all followers with 0 dropped closures.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T18:38:07.042251` $\rightarrow$ `2026-11-05T18:38:34.770242` (27.73s)  
**Overall Verification Status:** **❌ FAIL**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Follower ctf1 Received 3 Concurrent Orders** | `3` | `3` | ✅ PASS |  |
| 2 | **Follower ctf2 Received 3 Concurrent Orders** | `3` | `3` | ✅ PASS |  |
| 3 | **Follower ctf3 Received 3 Concurrent Orders** | `3` | `3` | ✅ PASS |  |
| 4 | **Follower ctf4 Received 3 Concurrent Orders** | `3` | `3` | ✅ PASS |  |
| 5 | **Follower ctf5 Received 3 Concurrent Orders** | `3` | `3` | ✅ PASS |  |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Master Placed 3 Concurrent Orders
- **Action:** `POST /trade/placeorder.php`
- **Telemetry / Details:** `{"order_ids": ["59878", "59884", "59890"]}`

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.