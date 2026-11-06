# WavexOne Copy Trading Automation: Confirmed Test Framework Issues vs. Platform Defects

**Audit Date:** 2026-11-06  
**Auditor:** Senior QA Automation Engineer (Financial Trading Systems)  
**Target Platform:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** `tests/test_copy_trading_all_scenarios.py` & `tests/test_balance_auto_squareoff.py`

---

## 1. Executive Summary

A critical responsibility of QA engineering is to **rigorously distinguish between platform defects (real bugs in the application under test) and test automation framework defects (bugs in test scripts, harnesses, or runners)**. 

Conflating automation framework bugs with platform bugs leads to false bug reports, wastes developer time, and conceals genuine platform risks. This document categorizes all confirmed defects identified during our comprehensive audit.

---

## 2. Confirmed Test Framework Defects (Internal Automation Bugs)

These issues reside inside the test code, helper classes, or execution runners and must be corrected by the QA automation team:

| Defect ID | Affected File / Function | Description | Root Cause | Impact |
| :--- | :--- | :--- | :--- | :--- |
| **FW-01** | `test_balance_auto_squareoff.py` (BS57–BS60, Teardown) | Calling non-existent method `sess.cancel_pending_order(oid)` | The method in `core/client.py` is named `cancel_order(order_id)`. | Scenarios BS57, BS58, BS59, BS60 crashed with `AttributeError`. Teardown failed to cancel pending orders, causing cascading failures in BS86 and BS93. |
| **FW-02** | `test_balance_auto_squareoff.py` (BS41) | Crash on `f_manual.get(...)` | `place_order()` occasionally returns a JSON list `[...]` instead of a dictionary `{...}`. Test code did not type-check the response. | Test crashed with `AttributeError: 'list' object has no attribute 'get'`. |
| **FW-03** | `test_copy_trading_all_scenarios.py` (`_execute_scenario`) | Incomplete Follower Coverage | Scenarios 01–21 only poll and assert against `self.primary_follower` (`ctf1`). | Followers `ctf2` through `ctf5` are never asserted during standard Multiplier, Balance, and Equity mode tests. |
| **FW-04** | `run_all_scenarios.py` & `run_balance_auto_squareoff.py` | Inadequate Inter-Test Delay / Pacing | Tests run in rapid burst mode with only 1.2s to 2.5s delay. | Saturates Staging's Apache/PHP connection pool and fanout queue, causing HTTP Read Timeouts and false test failures (e.g. AS-22 to AS-28 in batch runner). |
| **FW-05** | `test_balance_auto_squareoff.py` (BS98, BS99, BS100) | Invalid / Mock Assertions | `assert time.time() > 0` (BS98), `assert len(self.master.call_logs) > 0` (BS99), and `assert r.status_code in [200, 401, 404]` (BS100). | Trivial or non-functional passes that do not validate the platform under test. |
| **FW-06** | `test_copy_trading_all_scenarios.py` (BS52, BS54, AS-28) | Tight Polling Timeouts on Fanout | Follower wait loop uses an 8.0s timeout with immediate polling after master squareoff. | Fast-ticking crypto markets or multi-follower fanouts often take 8.5s–12.0s to settle, causing false timeout assertions. |

---

## 3. Confirmed Platform Engine Defects (Genuine Staging Bugs)

These issues are genuine functional defects in the WavexOne brokerage engine, confirmed through repeatable API evidence and multi-account state analysis:

### [BUG-01] High-Concurrency Fanout Queue Drop (Batch Squareoff Failure)
- **Affected Scenarios:** AS-28, BS66
- **Severity:** HIGH / CRITICAL
- **Reproduction Steps:**
  1. Master places 3 concurrent orders on `X:BTCUSD` (1.00 lot each).
  2. All 5 followers replicate all 3 orders (15 total follower positions).
  3. Master calls `/book/squareoff.php` in rapid succession for all 3 master positions.
  4. Query `/book/orders.php` across all 5 followers after 35 seconds.
- **Expected Result:** All 15 follower positions are cleanly squared off.
- **Actual Result:** Server fanout queue drops closures on follower `ctf1` and `ctf2`, leaving orphaned open positions actively exposed to market risk.
- **Evidence File:** `reports/evidence/evidence_scen_28_batch_concurrent_auto_squareoff.json`

### [BUG-02] Unfollowed Follower Position Closes Erroneously on Master Squareoff
- **Affected Scenarios:** BS43, Historical Scenario 07
- **Severity:** MEDIUM / HIGH
- **Reproduction Steps:**
  1. Follower replicates an open position from Master 1060.
  2. Follower calls `/user/follow.php?follow=1060&type=unfollow`. Unfollow succeeds (`status: success`).
  3. Master squares off its open position.
- **Expected Result:** The follower's position was opened before unfollowing and should either remain open under independent follower management or transition cleanly.
- **Actual Result:** The broker matching engine erroneously fires a square-off fanout to the follower even after the subscription record was deleted.
- **Evidence File:** `reports/evidence/evidence_07_unfollow_with_open_position.json`

### [BUG-03] Stop HFT Breakout Dual-Leg Residual Order Leak
- **Affected Scenarios:** M-07, B-14
- **Severity:** MEDIUM
- **Reproduction Steps:**
  1. Master places Stop HFT BOTH (`type=stop`, `stop_hft_type=2`).
  2. Breakout leg triggers on market move and fills into a live position.
  3. Master position auto-closes on TP/SL hit.
- **Expected Result:** When the active position auto-closes, the inactive opposite pending stop leg should be cancelled automatically.
- **Actual Result:** Inactive pending stop order remains stranded in the follower's order book (e.g. Follower order `59800`), risking unexpected future fills.
- **Evidence File:** `reports/evidence/evidence_scen_14_bal_stop_both_1lot_auto_exit.json`

### [BUG-04] Staging Orders API Returns Static Equity Equal to Balance
- **Affected Scenarios:** E-15 through E-21, BS21 through BS27
- **Severity:** MEDIUM
- **Reproduction Steps:**
  1. Open a 1.00 lot position on `X:BTCUSD`.
  2. Allow position to accumulate floating P&L of $+500.00$ or $-500.00$.
  3. Query `GET /book/balance.php?token={token}`.
- **Expected Result:** `equity` reflects `balance + floating_pnl`.
- **Actual Result:** `/book/balance.php` statically returns `'equity': '111223378.80'` == `'balance': '111223378.80'`.
- **Impact:** Equity-based copy trading is functionally identical to balance-based copy trading on Staging, forcing all equity tests to be marked `INCONCLUSIVE` per specification guard.

---

## 4. Staging Platform & Infrastructure Limitations (Inconclusive Scenarios)

These scenarios cannot be marked as PASS or FAIL because the staging environment intentionally or architecturally lacks the prerequisite infrastructure:

1. **Missing Balance-Based Auto Square-Off Configuration API ([ARCH-01]):**
   - **Scenarios:** BS01–BS10, BS70–BS80.
   - **Finding:** The platform has no user-facing or API endpoints for setting arbitrary balance protection thresholds. Routes `/user/risk.php`, `/user/auto_squareoff.php`, `/user/settings.php`, and `/client-portal/apiAutoSquareOff` return HTTP 404.
   - **Classification:** Properly classified as **INCONCLUSIVE / BLOCKED**.
2. **Artificial High-Balance Accounts ($12M to $111M) with 1:500 Leverage:**
   - **Scenarios:** BS45 (Insufficient Margin), BS84 (Zero Balance), BS85 (Negative Balance).
   - **Finding:** With $12,246,000 balance and 1:500 leverage, a 1.00 lot BTCUSD position uses only ~$160 margin. Margin level exceeds 7,000,000%. Stop-out liquidation cannot be triggered without direct database balance reduction.
3. **Forex 24/5 Market Hours on Weekend:**
   - **Scenario:** BS68.
   - **Finding:** BTCUSD trades 24/7. Validating market closed behavior requires testing on `C:EURUSD` or `M:XAUUSD` outside trading hours.
4. **Third-Party Gateways (Deposits, Withdrawals, KYC):**
   - **Scenarios:** BS15 (Deposit), BS16 (Withdrawal).
   - **Finding:** Staging payment gateways require live banking credentials or manual admin portal approvals.

