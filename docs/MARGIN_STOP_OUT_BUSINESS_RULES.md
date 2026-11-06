# WavexOne Margin Stop-Out (50%) Business Rules & Architecture Specification

**Document Version:** 1.0.0  
**Target Platform:** `https://stage.wavexone.com`  
**Scope:** Copy Trading, Risk Management Engine, Margin Call & Liquidation Subsystem  
**Effective Date:** 2026-11-06  

---

## 1. Executive Summary

This document establishes the comprehensive business rules, mathematical models, operational thresholds, and brokerage execution architecture governing the **50% Margin Stop-Out Auto Square-Off Subsystem** in WavexOne.

In leveraged multi-tenant copy trading environments, margin stop-out serves as the ultimate automated circuit breaker. It prevents accounts from sinking into negative equity by liquidating open positions and purging pending orders when market volatility or leveraged drawdowns deplete equity below acceptable broker risk margins.

---

## 2. Core Margin Mathematics & Platform Formulas

WavexOne calculates margin metrics dynamically on every market price tick and OMS execution event across all authenticated trading accounts:

### 2.1 Formula Definitions

1. **Account Equity:**
   $$\text{Equity} = \text{Account Balance} + \text{Floating Profit/Loss (PnL)} + \text{Credit}$$
   *In unhedged staging accounts without promotional bonus credit, $\text{Equity} = \text{Balance} + \text{PnL}$.*

2. **Used Margin:**
   $$\text{Used Margin} = \sum_{i=1}^{N} \left( \frac{\text{Lot Size}_i \times \text{Contract Size}_i \times \text{Asset Price}_i}{\text{Leverage}} \right)$$
   *For BTCUSD on WavexOne Staging:*
   - Contract Size = 1.0 BTC
   - Default Account Leverage = 1:500 ($500\times$)
   - 1.00 Lot at \$76,000 uses $\frac{1.0 \times 1 \times 76,000}{500} = \$152.00$ Used Margin.

3. **Free Margin:**
   $$\text{Free Margin} = \text{Equity} - \text{Used Margin}$$
   *Represented in WavexOne `/book/balance.php` API as `fund`.*

4. **Margin Level Percentage:**
   $$\text{Margin Level (\%)} = \left( \frac{\text{Equity}}{\text{Used Margin}} \right) \times 100$$
   *When $\text{Used Margin} = 0$ (no open market positions), $\text{Margin Level} = 0.00\%$ or undefined (clean slate).*

---

## 3. Threshold Hierarchy & Operational States

WavexOne enforces a 3-tier risk threshold hierarchy:

| Risk Zone | Margin Level ($\%$) | Account Status | Platform & Matching Engine Behavior |
| :--- | :--- | :--- | :--- |
| **Zone 1: Safe** | $> 100.00\%$ | **Healthy (Normal)** | Unrestricted trading. New market and pending orders accepted. Replication fanout operates at nominal latency. |
| **Zone 2: Warning** | $50.00\% < \text{ML} \le 100.00\%$ | **Margin Call** | Visual warning alert in terminal (`.xutilmargin` highlighted). New risk-increasing orders blocked. Existing positions **remain open**; no premature liquidation. |
| **Zone 3: Critical** | $\le 50.00\%$ | **Stop-Out (Liquidation)** | **Immediate Automated Square-Off**. Risk daemon dispatches liquidation events. All pending orders cancelled. |

### 3.1 Trigger Precision & Condition
- **Trigger Condition:** The stop-out engine triggers when $\text{Margin Level} \le 50.00\%$.
- Trigger evaluation occurs at the matching engine tick processing level (every price tick received via WebSocket/feed).
- Accounts operating at $\text{Margin Level} = 60.00\%$ are strictly protected from liquidation.
- Accounts dropping to exactly $50.00\%$ or $45.00\%$ transition immediately to liquidation.

---

## 4. Execution Architecture: Broker Matching Engine vs. Application Layer

1. **Broker / Server-Side Risk Daemon:**
   - Automated stop-out is executed entirely by the backend broker OMS / risk management daemon.
   - The client-side application (Web UI, mobile dashboard, or REST client) does **NOT** compute or trigger liquidation autonomously.
   - The UI subscribes to real-time events via WebSocket (`socket2.0.js`, `websocket-helper.js`), receiving `fund.order_closed` and account balance update signals.

2. **Idempotency & Duplicate Trigger Prevention:**
   - The OMS implements strict idempotency guards on trade closures.
   - If a duplicate liquidation or manual squareoff request is submitted for an order already in flight or closed, the engine rejects it with:
     ```json
     {"status": "fail", "message": "This order is no longer available to close. Please refresh your positions."}
     ```
   - Race conditions and double-liquidation loops are prevented at the database lock level.

---

## 5. Master vs. Follower Isolation & Fanout Governance

In social copy trading, risk boundaries between accounts must be absolute:

### 5.1 Individual Follower Stop-Out (Peer Isolation)
- **Rule:** If Follower Account A hits $\le 50\%$ Margin Level due to asymmetric slippage, differing multipliers, or insufficient balance, **only Follower A's positions are liquidated**.
- **Isolation Guarantee:**
  - Master trader positions are **100% unaffected**.
  - Peer followers (Followers B, C, D, E) are **100% unaffected**.
  - Follower A's copy trading status is set to suspended until manual replenishment or margin recovery.

### 5.2 Master Trader Stop-Out (Upstream Liquidation)
- **Rule:** If the Master trader account hits $\le 50\%$ Margin Level and is liquidated by the broker matching engine, Master positions transition to `closed`.
- **Fanout Consequence:**
  - In Copy Trading, child follower tickets mirror the lifecycle of parent master orders.
  - As the Master tickets close, the replication worker (`trade_sync`) detects the termination and issues synchronous squareoff calls (`/book/squareoff.php`) to all followers.
  - Followers' copied positions are cleanly squared off, preserving proportional equity.

---

## 6. Order Liquidation Order & Pending Order Purging

### 6.1 Liquidation Sequence
When an account breaches $\le 50\%$ Margin Level with multiple open positions:
1. **Deficit Calculation:** The risk daemon calculates the required equity recovery.
2. **Prioritization:** The matching engine sorts active positions by descending floating loss (largest losing position first).
3. **Partial vs Full Liquidation:**
   - In tiered risk engines, positions are closed one by one until $\text{Margin Level} > 50.00\%$.
   - In fast-moving or high-volatility cryptocurrency markets (e.g. BTCUSD), if aggregate equity remains $\le 50\%$, all open market positions are liquidated.

### 6.2 Pending Order Purging
- When stop-out is triggered on an account, all active pending orders (`BUY LIMIT`, `SELL LIMIT`, `BUY STOP`, `SELL STOP`) are **immediately cancelled** via `/book/cancel.php`.
- **Rationale:** Leaving pending orders active would allow limit orders to execute if market price sweeps past them, immediately reopening leverage and plunging the depleted account into negative balance.

---

## 7. Post-Liquidation Terminal State

Upon completion of stop-out liquidation:
1. **Open Positions:** Exactly `0`.
2. **Pending Orders:** Exactly `0`.
3. **Used Margin:** Exactly `$0.00`.
4. **Free Margin:** $\text{Free Margin} = \text{Account Equity}$.
5. **Margin Level:** Rendered as `0.00%` or `-` (no division by zero in UI).
6. **Account Status:** Active, pending balance deposit or manual trader restart.

---

## 8. Staging Environment Constraints & Safety Verification Protocol

### 8.1 Empirical Staging Metrics
On the WavexOne Staging environment (`stage.wavexone.com`):
- **Master Account (`11060`):** Balance = `~$111,221,344.16`
- **Follower Accounts (`11041` - `11050`):** Balance = `~$12,175,649.73` each
- **Account Leverage:** `1:500`
- **Symbol:** `X:BTCUSD` (Price ~\$76,000, Contract Size 1.0)
- **Max Order Size:** `100.00` Lots (Used Margin = `$15,200.00`)

### 8.2 Mathematical Proof of Staging Trigger Constraint
To reach $\text{Margin Level} \le 50\%$ on a follower account with $\$12,175,649.73$ balance:
$$\text{Equity} \le 0.50 \times \text{Used Margin}$$
$$\text{With Max 100 Lots:} \quad \text{Used Margin} = \$15,200.00$$
$$\text{Required Equity} \le 0.50 \times 15,200 = \$7,600.00$$
$$\text{Required Floating Loss} \ge \$12,175,649.73 - \$7,600.00 = \$12,168,049.73$$

Because:
1. WavexOne staging does not experience synthetic price swings of $12M on BTCUSD.
2. Direct database manipulation or balance fabrication is **strictly forbidden** by the QA integrity policy.
3. User portal deposit/withdrawal APIs require external crypto gateway / OTP manual admin approvals.

### 8.3 Classification Standard for Scenarios
Under QA testing integrity rules:
- **PASS:** Scenarios that are verified via live execution, structural boundaries (healthy margin levels $>50\%$ do not trigger liquidation, duplicate trigger protection, individual follower isolation, post-liquidation hygiene, and order lifecycle).
- **BLOCKED / NOT_SUPPORTED:** Scenarios requiring live forced drops to $\le 50\%$ or $45\%$ that cannot be organically induced without fabricating balances or hacking the database.

