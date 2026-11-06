# WavexOne Copy Trading: Comprehensive Edge Cases & Failure Modes

**Document Version:** 1.0.0  
**Target Platform:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** Copy Trading Edge Cases, Race Conditions & Failure Handling  
**Audience:** QA Engineers, System Architects, Backend Developers

---

## 1. Executive Summary

This document catalogues the critical edge cases, boundary conditions, race conditions, and architectural failure modes inherent to the WavexOne Copy Trading ecosystem. Testing and hardening these edge cases is critical to preventing account desynchronization, financial leakage, margin cascades, and orphaned orders.

---

## 2. Copy Sizing Edge Cases

### EC-LOT-01: Sub-Minimum Lot Size Truncation
- **Condition:** Follower balance or multiplier calculation results in a lot size smaller than the broker minimum allowable lot size ($\text{MinLot} = 0.01$).
  - *Example in Balance Mode:* Master Balance = $\$111,220,000$, Follower Balance = $\$100$, Master places $1.00$ lot.
  - $\text{Calculated Lot} = \frac{100}{111,220,000} \times 1.00 = 0.00000089\text{ lots}$.
- **Expected Platform Behavior:** Either round up to minimum lot ($0.01$) if margin allows, or cleanly reject the replication with code `ERR_BELOW_MIN_LOT` without failing the master trade.
- **Observed / Risk:** Silent failure where follower trade never replicates and no alert is emitted to the user.

### EC-LOT-02: Zero or Negative Master Balance (Division by Zero)
- **Condition:** Master account suffers extreme drawdown or has a $\$0.00$ ledger balance while in `balance` or `equity` copy mode.
- **Expected Platform Behavior:** Defensive boundary guard prevents `DivisionByZero` in PHP backend. Replications are suspended; follower is alerted.
- **Risk:** Uncaught PHP Warning / Fatal Exception resulting in HTTP 500 error and hanging fanout queue.

### EC-LOT-03: Sudden Multiplier Sizing Exceeding Follower Margin
- **Condition:** Follower sets a high multiplier (e.g., $10.0\text{x}$ or $20.0\text{x}$) or Master enters a large position ($5.0\text{ lots} \times 10.0 = 50.0\text{ lots}$).
- **Expected Platform Behavior:** Follower margin validation rejects the order (`ERR_INSUFFICIENT_MARGIN`).
- **Isolation Requirement:** The Master trade and other 4 followers MUST execute unaffected. Rejection must be isolated solely to the over-leveraged follower.

---

## 3. Order Execution & Matching Engine Edge Cases

### EC-ORD-01: Follower Spread Markup Leading to Immediate SL Breaches
- **Observed Fact:** Replicated follower orders fill with a broker markup of approximately $+5.4$ to $+5.6$ points relative to Master on `X:BTCUSD`.
- **Condition:** Master sets a tight Stop Loss (e.g., $-4.0$ points from Master fill price).
- **Failure Mode:** Follower order fills at $+5.5$ pts, causing the market price to immediately sit below or at the follower's Stop Loss, triggering an instantaneous SL auto-closure.
- **Architectural Safeguard:** Master orders must maintain a minimum distance buffer of $\ge 8.0\text{ to }10.0\text{ points}$ for TP/SL to ensure followers do not get stopped out instantly upon fill.

### EC-ORD-02: Stop HFT BOTH Residual Orphaned Bracket Leg ([BUG-03])
- **Observed Fact:** Dual breakout bracket orders (`type=stop`, `stop_hft_type=2`) generate two linked pending legs (Buy Stop and Sell Stop, e.g. `"58777,58778"`).
- **Failure Mode:** When market rallies, the Buy Stop triggers, converts to market position, and eventually hits TP or gets squared off. The Sell Stop pending leg **remains active on the follower account indefinitely**.
- **Severe Financial Risk:** If the market later drops, the residual Sell Stop unexpectedly triggers an un-hedged follower trade with no master tracking.
- **Required Fix:** The matching engine must enforce One-Cancels-the-Other (OCO) logic: when one leg fills or the resulting position is closed, the opposite pending bracket leg MUST be automatically purged.

### EC-ORD-03: Stale Price Rejection on Rapid Market Volatility
- **Condition:** High-frequency price movement on `BTCUSD` between Master order fill and Follower fanout execution.
- **Failure Mode:** Staging API returns `"Stop Loss should be less than CMP"` or `"Invalid Price"`.
- **Handling:** Asynchronous replication queue must fetch a fresh CMP tick for each follower order rather than reusing the Master's stale fill timestamp.

---

## 4. Account Lifecycle & Subscription Edge Cases

### EC-SUB-01: Unfollow During Open Position (Orphaned Trade Risk)
- **Condition:** Follower clicks "Unfollow" or sends `/user/follow.php` with `action=unfollow` while Master has an open replicated position.
- **Expected Behavior Matrix:**
  1. *Option A (Default Broker Standard):* Existing replicated position remains open; user assumes manual management. Future master orders are not copied.
  2. *Option B (Protective Standard):* Platform prompts user: "Close open positions or retain them?".
- **Verification Requirement:** Must verify whether Master square-off still closes the position after unfollowing, or if the trade becomes orphaned.

### EC-SUB-02: Switching Copy Mode While Positions are Active
- **Condition:** Follower switches from `multiplier` ($3.0\text{x}$) to `balance` mode while a $3.00$-lot trade is currently active.
- **Expected Behavior:** Active positions retain their original $3.00$ lot size. Only subsequent new Master orders adopt the new `balance` sizing calculation. Under no circumstances should the engine attempt to retroactively scale an existing open position.

### EC-SUB-03: Master Account Suspension / Password Change
- **Condition:** Master credentials change or Master account is suspended by Admin.
- **Expected Behavior:** Active follower positions must either be auto-closed with notification or preserved safely with stop losses intact. Pending follower orders must be cancelled.

---

## 5. System Latency, Timeouts & Concurrency Edge Cases

### EC-CON-01: Rapid Back-to-Back Master Order Submissions (Fanout Saturation)
- **Condition:** Master places 5 market orders in rapid succession ($< 500\text{ms}$ interval).
- **Risk:** Staging server Apache/PHP thread pool becomes saturated. Fanout worker experiences race conditions, leading to out-of-order execution, dropped follower tickets, or HTTP 504 / Read Timeouts.
- **Hardening:** Queue workers must implement FIFO sequencing per follower with rate-limiting backpressure.

### EC-CON-02: Follower Closes Position Simultaneously with Master Square-Off
- **Condition:** Follower initiates individual square-off at the exact millisecond Master initiates global square-off.
- **Risk:** Double-close race condition (`ERR_POSITION_ALREADY_CLOSED` or duplicate realized P&L deductions).
- **Platform Safeguard:** Atomic database row locking (`SELECT ... FOR UPDATE`) on position records.

---

## 6. Auto Square-Off & Balance Threshold Edge Cases

### EC-BAL-01: Absence of Configurable Balance Threshold Endpoint ([ARCH-01])
- **Finding:** Endpoints `/user/risk.php`, `/user/auto_squareoff.php`, and `/client-portal/apiAutoSquareOff` return HTTP 404. Neither the Web Trader nor Client Portal provides a custom balance threshold setting.
- **Impact:** Scenarios expecting custom user-defined balance stop-out thresholds cannot be configured via user-facing APIs on Staging.
- **Broker Level Reality:** Staging relies on system-level Stop-Out when Margin Level falls below the broker liquidation percentage (typically $20\%$ or $50\%$).

### EC-BAL-02: Static Equity Anomaly on Staging
- **Finding:** Live responses from `/book/balance.php` return identical values for `balance` and `equity` even when positions have significant floating P&L.
- **Impact:** Testing equity-based square-off triggers vs balance-based triggers requires verifying whether the matching engine internally tracks live equity separately from the `/book/balance.php` polling endpoint.

---

## 7. Edge Case Testing & Hardening Checklist

| Edge Case ID | Category | Severity | Current Status on Staging | Automation Strategy |
|---|---|---|---|---|
| **EC-LOT-01** | Sizing | Medium | Needs verification with tiny balance follower | Assert follower rejection or 0.01 lot clamp |
| **EC-LOT-02** | Sizing | Critical | Unhandled potential 500 error | Boundary unit test with $0 master balance |
| **EC-LOT-03** | Margin | High | Verified: isolates to single follower | Test with 1 follower having depleted margin |
| **EC-ORD-01** | Spread | High | Verified: requires $\ge 8.0$ pt buffer | Use dynamic CMP probe with safety offset |
| **EC-ORD-02** | Order Book | Critical | Confirmed Platform Defect ([BUG-03]) | Explicit residual pending teardown in tests |
| **EC-SUB-01** | Lifecycle | High | Requires Dev clarification | Test unfollow with active trade; check squareoff |
| **EC-SUB-02** | Lifecycle | Medium | Verified: only affects subsequent orders | Switch mode mid-trade; assert lot stability |
| **EC-CON-01** | Concurrency| High | Known Staging Apache/PHP timeout | Enforce 3.0s inter-test pacing delay |
| **EC-CON-02** | Concurrency| Medium | Handled via DB locks | Concurrently trigger master & follower exit |
| **EC-BAL-01** | Auto Square | Critical | Known Architecture Limitation ([ARCH-01]) | Mark custom threshold tests INCONCLUSIVE |

