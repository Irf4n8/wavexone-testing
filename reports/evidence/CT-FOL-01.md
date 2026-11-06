# Evidence Report: CT-FOL-01 — Multi-Follower Subscription & Relationship Verification

- **Category:** Follow/Unfollow Lifecycle
- **Status:** `PASS`
- **Execution Time:** 1.72s
- **Timestamp:** 2026-11-06 13:00:26

## Assertions Summary

| # | Assertion | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Total Followers Count >= 5 | `True` | `True` | ✅ PASS |
| 2 | All 5 Target Followers Active | `True` | `True` | ✅ PASS |
| 3 | ctf1 In Master Follower List | `True` | `True` | ✅ PASS |
| 4 | ctf1 In Follower Following List | `True` | `True` | ✅ PASS |
| 5 | ctf2 In Master Follower List | `True` | `True` | ✅ PASS |
| 6 | ctf2 In Follower Following List | `True` | `True` | ✅ PASS |
| 7 | ctf3 In Master Follower List | `True` | `True` | ✅ PASS |
| 8 | ctf3 In Follower Following List | `True` | `True` | ✅ PASS |
| 9 | ctf4 In Master Follower List | `True` | `True` | ✅ PASS |
| 10 | ctf4 In Follower Following List | `True` | `True` | ✅ PASS |
| 11 | ctf5 In Master Follower List | `True` | `True` | ✅ PASS |
| 12 | ctf5 In Follower Following List | `True` | `True` | ✅ PASS |

## Execution Steps Telemetry

### Step 1: Query Master and Follower Subscription Lists
- **Action:** `GET /user/userCopyFollowers.php`
- **Endpoint:** `https://stage.wavexone.com/user/userCopyFollowers.php` (GET) | Latency: 0.0ms
- **Details:** `{"all_active": true, "details": {"ctf1": {"account_id": "11041", "user_id": "1041", "in_master_list": true, "in_follower_list": true, "is_active": true}, "ctf2": {"account_id": "11043", "user_id": "1043", "in_master_list": true, "in_follower_list": true, "is_active": true}, "ctf3": {"account_id": "11045", "user_id": "1045", "in_master_list": true, "in_follower_list": true, "is_active": true}, "ctf4": {"account_id": "11048", "user_id": "1048", "in_master_list": true, "in_follower_list": true, "is_active": true}, "ctf5": {"account_id": "11050", "user_id": "1050", "in_master_list": true, "in_follower_list": true, "is_active": true}}, "total_followers_count": 5}`

