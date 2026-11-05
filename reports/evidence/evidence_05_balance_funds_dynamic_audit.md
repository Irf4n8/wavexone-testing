# Evidence Report: Copy Trading: Dynamic Balance, Funds & Margin Audit (✅ PASS)

**Test Identifier:** `evidence_05_balance_funds_dynamic_audit`  
**Objective:** Verify baseline balances, in-trade margin allocation (fund drops to secure active positions), live equity fluctuations, and post-close margin release back to settled balance.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T13:46:14.181214` $\rightarrow$ `2026-11-05T13:46:25.285866` (11.1s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (5/5 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Master Balance Positive** | `True` | `True` | ✅ PASS |  |
| 2 | **Follower Balance Positive** | `True` | `True` | ✅ PASS |  |
| 3 | **Master Margin Utilized in Trade** | `>0` | `160.87` | ✅ PASS | Locked margin for 1.00 Lot BTCUSD: $160.87 |
| 4 | **Follower Margin Utilized in Trade** | `>0` | `482.61` | ✅ PASS | Locked margin for 3.00 Lots BTCUSD: $482.61 |
| 5 | **Master Margin Fully Released** | `True` | `True` | ✅ PASS | Fund restored to equity upon closure |

---

## 📜 Chronological Execution Steps & Telemetry

### Step 1: Pre-Trade Master Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "111198183.41",
  "balance": "111198183.41",
  "equity": "111198183.41"
}
```

### Step 2: Pre-Trade Follower Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "12223139.64",
  "balance": "12223139.64",
  "equity": "12223139.64"
}
```

### Step 3: Client Portal Bootstrap Summary
- **Action:** `GET /client-portal/apiBootstrap`
```json
// Server Response:
{
  "totalFund": 111198183.41,
  "totalBalance": 111198183.41,
  "totalEquity": 111198183.41,
  "accountCount": 1,
  "referralCount": 0,
  "referralBonus": 0,
  "growthPercent30d": 0
}
```

### Step 4: Open Trade Placement
- **Action:** `POST /trade/placeorder.php`
```json
// Server Response:
{
  "status": "success",
  "message": "Order accepted for processing",
  "data": {
    "orderId": "53951",
    "intentId": "024453da94e960ad6bab64a17c65bf47",
    "executionStatus": "queued",
    "fanoutJobId": 6011,
    "fanoutStatus": "queued",
    "requestId": "legacy_a4e3fa1d463af82c549d89ea24b0cde8",
    "placementReplayProtected": true
  },
  "_duration_ms": 266.54,
  "_request_url": "https://stage.wavexone.com/trade/placeorder.php?type=market&bs=buy&lot=1.00&sl=&target=&symbol=X:BTCUSD&token=UHZIKS5BXD&clicked=yes&fingerprint=060d191b0e0707726a777e74726273641f45415621_224"
}
```

### Step 5: In-Trade Master Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "111198022.54",
  "balance": "111198183.41",
  "equity": "111198183.41"
}
```

### Step 6: In-Trade Follower Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "12222657.03",
  "balance": "12223139.64",
  "equity": "12223139.64"
}
```

### Step 7: Post-Trade Master Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "111198169.69",
  "balance": "111198169.69",
  "equity": "111198169.69"
}
```

### Step 8: Post-Trade Follower Balance Query
- **Action:** `GET /book/balance.php`
```json
// Server Response:
{
  "status": "success",
  "fund": "12223128.73",
  "balance": "12223128.73",
  "equity": "12223128.73"
}
```

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.