# WavexOne Copy Trading: Phase 1 (P0) Comprehensive Automation Test Results

- **Execution Date:** 2026-11-06 13:01:21
- **Platform:** WavexOne Staging (`https://stage.wavexone.com`)
- **Pytest Exit Code:** `0` (Success)
- **Duration:** 70.11s
- **Pass Rate:** **100% (6 Passed / 0 Failed)**

---

## 1. Execution Summary

The P0 automation suite was executed with full end-to-end trading and replication validation using strict **0.50 lot** Master orders. All 6 staging accounts were independently verified, and safe teardown guaranteed a verified clean slate (0 open or pending positions) after each test cycle.

| Scenario ID | Scenario Title | Copy Method | Master Action | Expected Follower Lot | Actual Follower Lot | Status | Evidence File |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CT-ACC-01** | Multi-Account Auth & Account ID Match | N/A | Session Validation | N/A | Master: `11060`, Followers: `11041, 11043, 11045, 11048, 11050` | **PASS** | `reports/evidence/CT-ACC-01.json` |
| **CT-FOL-01** | Multi-Follower Subscription Verification | N/A | Read Follower Config | Active on Master `1060` | All 5 Active | **PASS** | `reports/evidence/CT-FOL-01.json` |
| **CT-MUL-01** | Multiplier 3.0x Proportional Replication | `multiplier` (3.0x) | BUY 0.50 BTCUSD | 1.50 lots each | 1.50 lots across all 5 followers | **PASS** | `reports/evidence/CT-MUL-01.json` |
| **CT-BAL-01** | Balance-Based Market BUY Dynamic Sizing | `balance` | BUY 0.50 BTCUSD | 0.05 lots each | 0.05 lots across all 5 followers | **PASS** | `reports/evidence/CT-BAL-01.json` |
| **CT-EQU-01** | Equity-Based Market BUY Dynamic Sizing | `equity` | BUY 0.50 BTCUSD | 0.05 lots each | 0.05 lots across all 5 followers | **PASS** | `reports/evidence/CT-EQU-01.json` |
| **CT-BAL-02** | Balance-Based Market SELL Replication | `balance` | SELL 0.50 BTCUSD | 0.05 lots each | 0.05 lots across all 5 followers | **PASS** | `reports/evidence/CT-BAL-02.json` |

---

## 2. Key Scenario Highlights

### 2.1 CT-MUL-01: Multiplier 3.0x Replication
- **Master Order:** BUY 0.50 lot on `X:BTCUSD` (Order #74660) @ $75,348.50.
- **Fanout Latency:** All 5 followers replicated within 1.12s.
- **Sizing Formula:** $0.50 \times 3.0 = 1.50$ lots.
- **Replication Outcome:**
  - `ctf1` (11041): 1.50 lots (Order #74665)
  - `ctf2` (11043): 1.50 lots (Order #74664)
  - `ctf3` (11045): 1.50 lots (Order #74663)
  - `ctf4` (11048): 1.50 lots (Order #74662)
  - `ctf5` (11050): 1.50 lots (Order #74661)
- **Teardown:** Full master square-off fanout closed all 6 positions; clean slate verified.

### 2.2 CT-BAL-01: Balance-Based Dynamic Sizing (BUY)
- **Configuration:** Updated all 5 followers to `balance` mode.
- **Master Order:** BUY 0.50 lot on `X:BTCUSD` (Order #74666) @ $75,350.10.
- **Sizing Ratio:** Follower balance ($10,000) / Master balance ($100,000) = 0.10 $\to$ $0.50 \times 0.10 = 0.05$ lots.
- **Replication Outcome:** All 5 followers opened exactly 0.05 lots (Orders #74667-#74671).
- **Teardown:** Auto square-off executed; clean slate verified.

### 2.3 CT-EQU-01: Equity-Based Dynamic Sizing (BUY)
- **Configuration:** Updated all 5 followers to `equity` mode.
- **Master Order:** BUY 0.50 lot on `X:BTCUSD` (Order #74672) @ $75,351.40.
- **Sizing Ratio:** Follower equity ($10,000) / Master equity ($100,000) = 0.10 $\to$ $0.50 \times 0.10 = 0.05$ lots.
- **Replication Outcome:** All 5 followers opened exactly 0.05 lots (Orders #74673-#74677).
- **Teardown:** Auto square-off executed; clean slate verified.

### 2.4 CT-BAL-02: Balance-Based Market SELL Replication
- **Configuration:** Followers in `balance` mode.
- **Master Order:** SELL 0.50 lot on `X:BTCUSD` (Order #74678) @ $75,349.80.
- **Replication Outcome:** All 5 followers opened SELL positions of 0.05 lots (Orders #74679-#74683).
- **Teardown:** Auto square-off executed; clean slate verified; baseline restored to multiplier 3.0x.

---

## 3. Account Clean Slate Verification

- **Post-Suite State:** All 6 accounts checked via fresh order-book queries.
- **Active Orders:** 0 across all accounts.
- **Pending Orders:** 0 across all accounts.
- **Baseline Configuration:** Restored to `multiplier` 3.0x on Master UID `1060`.
