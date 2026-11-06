# WavexOne Copy Trading Automation: Comprehensive Audit of Missing Assertions & Weak Validations

**Audit Date:** 2026-11-06  
**Auditor:** Senior QA Automation Engineer (Financial Trading Systems)  
**Target Platform:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** `tests/test_copy_trading_all_scenarios.py` (28 Scenarios) & `tests/test_balance_auto_squareoff.py` (100 Scenarios)

---

## 1. Executive Summary

A critical principle of automated financial QA is: **"HTTP 200 or `status: success` is never proof of trade execution, margin integrity, or broker reconciliation."**

Our audit revealed that while the core order placement and polling machinery is functional, **several tests contain superficial assertions, weak validation logic, or single-follower coverage gaps**. In several instances, tests reported `PASS` without mathematically verifying balances, without confirming position ledger closure across all followers, or by asserting trivial local conditions (such as `assert time.time() > 0`).

---

## 2. Category 1: Superficial & Weak Assertions (Trivial Passes)

The following tests in `tests/test_balance_auto_squareoff.py` passed execution but lacked genuine validation:

| Scenario ID | Test Name | Existing Assertion in Code | Why It Is Weak / Flawed | Required Rigorous Assertion |
| :--- | :--- | :--- | :--- | :--- |
| **BS13** | Balance decreases after profitable trade and charges | `assert float(bal.get("balance", 0)) > 0` | Does not execute a trade, does not calculate commissions, and merely asserts account balance is positive. | Record `B_pre`. Execute trade. Record `B_post`. Calculate `Realized_PnL` and `Commission`. Assert `B_post == B_pre + Realized_PnL - Commission`. |
| **BS14** | Balance increases after profitable trade | `assert float(bal.get("balance", 0)) > 0` | Does not execute a profitable trade; checks non-zero balance. | Place directional trade with take profit hit. Assert `B_post > B_pre` by the exact net profit amount. |
| **BS17** | Balance changes due to commission | `assert "balance" in bal` | Merely checks if the word `"balance"` exists in the dictionary returned by `/book/balance.php`. | Inspect trade receipt or `/client-portal/apiBootstrap` ledger to assert commission fee debit. |
| **BS33** | Master balance recovers after square-off | `assert float(bal.get("balance", 0)) > 0` | Checks balance > 0; does not verify balance recovery or margin release. | Verify `used_margin == 0.00` and `equity == balance` immediately following position square-off. |
| **BS42** | Follower balance recovers after square-off | `assert float(b.get("balance", 0)) > 0` | Checks balance > 0; does not audit follower P&L or balance recovery. | Verify follower balance reflects realized gain/loss and that used margin returned to 0.00. |
| **BS91** | Verify balance after square-off | `assert float(b.get("balance", 0)) > 0` | Asserts positive balance rather than auditing the mathematical delta from closed trades. | Assert `Final_Balance == Initial_Balance + sum(Realized_PnL_all_closed_positions)`. |
| **BS94** | Verify free margin after square-off | `assert float(b.get("fund", 0)) > 0` | Checks fund > 0; does not verify that Free Margin equals total Balance when no positions are open. | Assert `abs(free_margin - balance) < 0.01` and `used_margin == 0.00`. |
| **BS95** | Verify realized P&L | `assert "balance" in bal` | Asserts dictionary key presence; zero calculation of realized P&L. | Assert `Realized_PnL == (Close_Price - Open_Price) * Lot * Contract_Size * Direction`. |
| **BS96** | Verify transaction history | `assert r.status_code == 200` | Only checks HTTP status of `/client-portal/apiBootstrap`; does not inspect transactions list. | Parse `r.json()["data"]["transactions"]` and assert the closed trade's Order ID, lot size, and execution price exist in the array. |
| **BS98** | Verify square-off timestamps | `assert time.time() > 0` | **Critical QA Flaw:** Asserts Python's local Unix epoch time is positive, completely bypassing platform timestamp verification! | Extract `close_time` from order book / transaction receipt and assert it matches current UTC wall-clock time within $\pm 30$ seconds. |
| **BS99** | Verify audit logs and trigger reasons | `assert len(self.master.call_logs) > 0` | Asserts Python's in-memory requests log, not the broker platform's audit trail! | Query platform audit log / OMS events and assert trigger reason is recorded as `TP_HIT`, `SL_HIT`, or `USER_SQUAREOFF`. |
| **BS100** | Verify square-off notifications | `assert r.status_code in [200, 401, 404]` | **Critical QA Flaw:** Allows HTTP 401 Unauthorized or HTTP 404 Not Found to count as a PASS! | Require HTTP 200 and parse notification payload to verify squareoff alert was delivered to follower. |

---

## 3. Category 2: Single-Follower Verification Gaps (Followers 2–5 Unchecked)

A core requirement of copy trading automation is proving multi-tenant replication consistency across all connected follower accounts.

### In `tests/test_copy_trading_all_scenarios.py`:
- **Scenarios M-01 to M-07 (Multiplier Mode):** Replicates order on Master, but only polls and verifies `self.primary_follower` (`ctf1`). Followers `ctf2`, `ctf3`, `ctf4`, and `ctf5` are **never queried or asserted**. If the broker's fanout queue silently dropped followers 2 through 5, the tests would still report `PASS`.
- **Scenarios B-08 to B-14 (Balance Mode):** Same issue: only `ctf1` is checked for the balance-scaled lot size (~0.11 lots). The remaining 4 followers are unverified.
- **Scenarios E-15 to E-21 (Equity Mode):** Sizing guard only evaluates `ctf1`.

### In `tests/test_balance_auto_squareoff.py`:
- **Scenarios BS23, BS24, BS40, BS43, BS46, BS47, BS48, BS49, BS50, BS51, BS52, BS53, BS54, BS55, BS57, BS58, BS59, BS60, BS66, BS86, BS90:**
  - All assert closure strictly on `self.primary_follower.wait_for_all_closed()`.
  - Followers `ctf2` through `ctf5` are not verified during these tests, leaving open the risk of orphaned follower positions.

> [!IMPORTANT]
> Multi-follower verification was only properly implemented in **Scenarios AS-22 through AS-26** (`test_22_auto_squareoff_take_profit_hit_all_followers` to `test_26`), where an explicit loop checked all 5 followers. All other scenarios must adopt this pattern.

---

## 4. Category 3: Tests Checking HTTP Status Codes Only

The following tests rely primarily on HTTP status codes without auditing underlying database/broker state:

1. **`BS62` (Square-off API returns HTTP 200):**
   - Asserts `sq.get("status") == "success"`.
   - Missing assertion: Must verify that position status changed to `CLOSED` in database, margin was unlocked, and floating P&L ceased ticking.
2. **`BS63` (Square-off API returns an error on invalid ID):**
   - Asserts `sq.get("status") in ["fail", "error"]`.
   - Missing assertion: Must assert error message contains `Order not found` or `Invalid position identifier` and HTTP status code is appropriate.
3. **`BS96` (Verify transaction history):**
   - Asserts `r.status_code == 200` on bootstrap API without parsing transaction arrays.

---

## 5. Category 4: Incorrect Expected Results & Logic Flaws

1. **`BS86` (Account has no trading activity):**
   - Expected: `assert len(orders) == 0`.
   - Flaw: Due to preceding test failures where pending orders were not cancelled in teardown, `BS86` failed with residual pending orders from earlier tests rather than testing its own isolated condition.
2. **`BS93` (Verify used margin after square-off):**
   - Logic: Asserts `len(orders) == 0` to deduce used margin is 0.00.
   - Missing Assertion: Must explicitly query `/book/balance.php` or Web Trader DOM to assert `used_margin == 0.00` directly.
3. **`BS41` (Follower manual position during master squareoff):**
   - Logic assumed `f_manual` is always a `dict` with `{"data": {"orderId": "..."}}`.
   - Actual: When placing manual orders on staging, the API occasionally returns raw text or a list, crashing the test runner with `AttributeError: 'list' object has no attribute 'get'`.

---

## 6. Actionable Recommendations for Test Hardening

1. **Implement Mathematical Ledger Assertions:**
   - Create a reusable fixture `assert_account_ledger_balanced(session, pre_balance, post_balance, closed_orders)` that computes theoretical P&L against actual balance delta.
2. **Mandate Multi-Follower Verification Loop:**
   - Refactor `_execute_scenario()` in `test_copy_trading_all_scenarios.py` to iterate over all 5 follower sessions (`cls.followers`), asserting replication on every follower.
3. **Eliminate Trivial Epoch / Mock Assertions:**
   - Remove `assert time.time() > 0` (BS98) and `assert len(self.master.call_logs) > 0` (BS99); replace with live API order history timestamp validation.
4. **Stricter Teardown Guarantees:**
   - Ensure teardown loops through both market and pending order cancellation routines without crashing on missing methods.

