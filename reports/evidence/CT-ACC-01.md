# Evidence Report: CT-ACC-01 — Authentication & Live Staging Account ID Validation

- **Category:** Account Management
- **Status:** `PASS`
- **Execution Time:** 0.0s
- **Timestamp:** 2026-11-06 13:00:26

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Master Authenticated | `True` | `True` | ✅ PASS |
| 2 | Master Account ID Match | `11060` | `11060` | ✅ PASS |
| 3 | Follower ctf1 Authenticated | `True` | `True` | ✅ PASS |
| 4 | Follower ctf1 Account ID Match | `11041` | `11041` | ✅ PASS |
| 5 | Follower ctf2 Authenticated | `True` | `True` | ✅ PASS |
| 6 | Follower ctf2 Account ID Match | `11043` | `11043` | ✅ PASS |
| 7 | Follower ctf3 Authenticated | `True` | `True` | ✅ PASS |
| 8 | Follower ctf3 Account ID Match | `11045` | `11045` | ✅ PASS |
| 9 | Follower ctf4 Authenticated | `True` | `True` | ✅ PASS |
| 10 | Follower ctf4 Account ID Match | `11048` | `11048` | ✅ PASS |
| 11 | Follower ctf5 Authenticated | `True` | `True` | ✅ PASS |
| 12 | Follower ctf5 Account ID Match | `11050` | `11050` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Verify Master Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/login/check.php` (POST) | Latency: 0.0ms
- **Details:** `{"name": "ctmaster", "live_account_id": "11060", "user_id": "1060"}`

### Step 2: Verify Follower ctf1 Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/dashboard/api/accountList.php` (GET) | Latency: 0.0ms
- **Details:** `{"name": "ctf1", "live_account_id": "11041", "user_id": "1041"}`

### Step 3: Verify Follower ctf2 Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/dashboard/api/accountList.php` (GET) | Latency: 0.0ms
- **Details:** `{"name": "ctf2", "live_account_id": "11043", "user_id": "1043"}`

### Step 4: Verify Follower ctf3 Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/dashboard/api/accountList.php` (GET) | Latency: 0.0ms
- **Details:** `{"name": "ctf3", "live_account_id": "11045", "user_id": "1045"}`

### Step 5: Verify Follower ctf4 Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/dashboard/api/accountList.php` (GET) | Latency: 0.0ms
- **Details:** `{"name": "ctf4", "live_account_id": "11048", "user_id": "1048"}`

### Step 6: Verify Follower ctf5 Authentication
- **Action:** `Check session and account ID`
- **Endpoint:** `https://stage.wavexone.com/dashboard/api/accountList.php` (GET) | Latency: 0.0ms
- **Details:** `{"name": "ctf5", "live_account_id": "11050", "user_id": "1050"}`

