# WavexOne Copy Trading Automation: Strategic Roadmap & Recommended Next Tests

**Audit Date:** 2026-11-06  
**Auditor:** Senior QA Automation Engineer (Financial Trading Systems)  
**Target Platform:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** Immediate Hardening & Next Phase Execution

---

## 1. Phase 1: Test Framework Hardening & Remediation (P0)

Before expanding test coverage, the existing automation framework must be hardened to eliminate false positives and false negatives:

### Action Item 1: Refactor All Scenarios for 5-Follower Concurrent Verification
- **Issue:** Currently, Scenarios 01–21 in `test_copy_trading_all_scenarios.py` and most BS scenarios in `test_balance_auto_squareoff.py` only verify `ctf1`.
- **Implementation:** Replace single-follower checks with a standardized helper:
  ```python
  def assert_all_followers_replicated(self, symbol, side, expected_lot, order_type="market", timeout=10.0):
      results = {}
      for f in self.followers:
          ord_match = f.wait_for_order_in_book(symbol=symbol, side=side, expected_lot=expected_lot, order_type=order_type, timeout=timeout)
          assert ord_match is not None, f"Follower {f.name} failed to replicate {expected_lot} lots {side}!"
          results[f.name] = ord_match["id"]
      return results
  ```

### Action Item 2: Replace Superficial Assertions with Mathematical Ledger Audits
- **Issue:** Tests BS13, BS14, BS17, BS33, BS42, BS91, BS94, BS95 only check `balance > 0`.
- **Implementation:** Implement mathematical pre/post balance reconciliation:
  ```python
  def assert_realized_pnl_reconciled(self, session, pre_bal, post_bal, open_price, close_price, lot, side):
      contract_size = 1.0  # BTCUSD
      direction = 1.0 if side.lower() == "buy" else -1.0
      expected_pnl = (close_price - open_price) * lot * contract_size * direction
      actual_delta = post_bal - pre_bal
      # Allow small tolerance for broker commissions/swap
      assert abs(actual_delta - expected_pnl) < 5.0, f"Balance delta ({actual_delta}) does not match realized P&L ({expected_pnl})!"
  ```

### Action Item 3: Implement an Adaptive Concurrency & Pacing Controller
- **Issue:** Running rapid back-to-back tests saturates Staging's Apache/PHP thread pool, causing read timeouts.
- **Implementation:** Add an adaptive queue pacer in `run_all_scenarios.py` that waits for server thread pool drain (`time.sleep(3.5)` between order cycles and validates clean HTTP 200 health before each scenario).

---

## 2. Phase 2: High-Value New Test Scenarios to Implement (P1)

Once the framework is hardened, execute these high-priority trading platform scenarios:

### Test Scenario N-01: Low-Balance Follower Margin Exhaustion (Real Margin Call / Stop-Out)
- **Objective:** Verify broker copy engine behavior when a follower account has insufficient free margin to replicate a Master order.
- **Preconditions:** Request dev team to set `ctf5` account balance to **$250.00** (or configure a dedicated low-balance account).
- **Execution:**
  1. Master places 1.00 lot BTCUSD (requires ~$160 margin).
  2. Multiplier is 3.0x -> Follower requires ~$480 margin.
  3. Follower only has $250 -> Free margin is exhausted.
- **Assertions:**
  - Follower replication is cleanly rejected with `Insufficient Margin`.
  - Master order and all 4 healthy followers (`ctf1`–`ctf4`) remain completely unaffected.
  - Follower account does not enter negative balance.

### Test Scenario N-02: Follower Early Manual Square-Off (Peer & Master Independence)
- **Objective:** Verify that when one follower manually closes a copied position from their own terminal, Master and other followers remain open.
- **Execution:**
  1. Master places 1.00 lot BUY. All 5 followers replicate 3.00 lots.
  2. Follower `ctf1` calls `/book/squareoff.php` on its own order ID.
- **Assertions:**
  - Follower `ctf1` position is closed.
  - Master position remains open and unaffected.
  - Followers `ctf2`, `ctf3`, `ctf4`, `ctf5` remain open and unaffected.
  - When Master eventually squares off, `ctf1` does not crash or receive duplicate close events.

### Test Scenario N-03: Outside-Market-Hours Behavior on Non-Crypto Instrument (`C:EURUSD`)
- **Objective:** Verify replication and rejection handling when Master or Follower attempts an order while the instrument's market is closed.
- **Schedule:** Execute on Saturday or Sunday when Forex markets are closed.
- **Execution:** Master places 1.00 lot on `C:EURUSD`.
- **Assertions:**
  - Backend returns clean rejection: `Market is closed for C:EURUSD`.
  - Zero pending or open positions created on Master or Followers.

### Test Scenario N-04: Fixed Markup vs. Dynamic Slippage Discrepancy Probe
- **Objective:** Systematically analyze the consistent 5.4 to 5.6 point price discrepancy observed between Master fill price and Follower fill price on `X:BTCUSD`.
- **Execution:**
  1. Capture exact millisecond timestamp of Master fill.
  2. Capture exact millisecond timestamp of all 5 Follower fills across 20 consecutive trades.
- **Analysis:**
  - If discrepancy is exactly 5.50 points across all market volatility regimes, it is a **configured broker spread markup**.
  - If discrepancy varies with execution latency, it is **market execution slippage**.

### Test Scenario N-05: Real Pause vs. Unfollow State Validation
- **Objective:** Validate whether the platform supports a non-destructive "Pause" state versus terminal "Unfollow".
- **Execution:**
  1. Follower pauses subscription (if supported by UI / API).
  2. Master places order. Assert order is not copied.
  3. Follower resumes subscription.
  4. Assert previous trade is NOT retroactively copied, but new subsequent trades are copied.

---

## 3. Implementation Priority Matrix

| Phase | Milestone | Priority | Estimated Effort | Target Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | Framework Hardening: Fix `cancel_order`, add 5-follower assertion loops, fix BS41 parsing | Critical | 1 Day | Hardened `core/client.py` & `test_balance_auto_squareoff.py` |
| **P0** | Mathematical Ledger Assertions: Replace weak `balance > 0` checks with exact P&L reconciliation | Critical | 1 Day | Validated BS11–BS20, BS91–BS95 |
| **P1** | Low-Balance Margin Call Test (`ctf5` at $250) | High | 0.5 Day | `evidence_insufficient_margin.json` |
| **P1** | Follower Early Manual Square-Off (Peer Isolation) | High | 0.5 Day | `evidence_follower_early_close.json` |
| **P2** | Weekend Forex Closure Verification (`C:EURUSD`) | Medium | Weekend | `evidence_market_closed_forex.json` |
| **P2** | Master-Follower Spread Markup vs Slippage Statistical Study | Medium | 1 Day | `reports/slippage_markup_study.md` |

