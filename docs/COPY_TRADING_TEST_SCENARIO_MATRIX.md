# WavexOne Copy Trading: Comprehensive Test Scenario Matrix

**Document Version:** 2.0.0  
**Target Platform:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** Copy Trading ONLY (MAM & PAMM Excluded)  
**Target Accounts:**
- **Master:** `ctmaster` (UID: `1060`, Account ID: `11060`, Balance: $\approx \$111.2\text{M}$)
- **Followers:** `ctf1` (`11041`), `ctf2` (`11043`), `ctf3` (`11045`), `ctf4` (`11048`), `ctf5` (`11050`) (Balances: $\approx \$12.2\text{M}$ each)
- **Symbol:** `X:BTCUSD`

---

## 1. Scenario Matrix Overview

The matrix encompasses **25 functional categories** categorized by execution priority:
- **P0 (Critical Foundation):** Account setup, Auth, Follow/Unfollow, Multiplier Mode, Market Orders replication.
- **P1 (Core Copy Trading Logic):** Balance & Equity modes, Limit/Stop/Stop Both orders, Lot Calculation, TP/SL propagation, Order Modification, Master Square-Off & Peer Isolation.
- **P2 (Edge, Margin & Infrastructure):** Funds management, Margin verification, Insufficient margin, Network resilience, Concurrency, Residual bracket cancellation, Data reconciliation.

---

## 2. Complete Test Scenario Specifications

### Category 1: Account Management
#### `CT-ACC-01`: Multi-Account Concurrent Authentication & Live Account ID Validation
- **Feature/Module:** Account Management
- **Priority:** P0
- **Preconditions:** Credentials configured in `.env` for Master and 5 Followers.
- **Account Setup:** Master (`11060`), Followers `ctf1`–`ctf5` (`11041`, `11043`, `11045`, `11048`, `11050`).
- **Initial Values:** All sessions logged out.
- **Test Input:** POST credentials to `/login/check.php` for all 6 accounts.
- **Execution Steps:**
  1. Concurrently authenticate Master and all 5 Followers.
  2. For each account, call `/dashboard/api/accountList.php?token={token}`.
  3. Extract live trading account with `book == "a"`.
  4. Generate execution fingerprint via `/dashboard/api/create_fingerprint.php`.
- **Expected Result:** All 6 accounts authenticate successfully with valid session tokens; live account IDs match expected staging IDs (`11060`, `11041`, `11043`, `11045`, `11048`, `11050`).
- **Validation API:** `/login/check.php` returns `status=success`, `/dashboard/api/accountList.php` returns matching `account_id`.
- **Cleanup Requirements:** Retain session tokens in pool memory.
- **Evidence Requirements:** Session authentication log, UID and Account ID validation assertions.

#### `CT-ACC-02`: Invalid Credentials & Stale Token Rejection
- **Feature/Module:** Account Management
- **Priority:** P1
- **Preconditions:** Valid Master session established.
- **Account Setup:** Master account.
- **Initial Values:** Valid active session.
- **Test Input:** Attempt order query `/book/orders.php?token=INVALID_TOKEN_999`.
- **Execution Steps:**
  1. Call `/book/orders.php` using corrupted/stale token.
  2. Call `/login/check.php` with incorrect password for `ctmaster`.
- **Expected Result:** API rejects unauthenticated requests with `status=fail` or empty dataset. No unauthorized data leakage.
- **Validation API:** HTTP response inspection on `/book/orders.php`.
- **Cleanup Requirements:** Restore valid session.
- **Evidence Requirements:** Corrupted token request and error response payload.

---

### Category 2: Follow/Unfollow Lifecycle
#### `CT-FOL-01`: Multi-Follower Bulk Subscription Verification
- **Feature/Module:** Follow/Unfollow Lifecycle
- **Priority:** P0
- **Preconditions:** Master UID `1060` active. All 5 followers authenticated.
- **Account Setup:** All 5 followers set to follow Master `1060`.
- **Initial Values:** Followers subscribed with default settings.
- **Test Input:** GET `/user/follow.php?follow=1060&type=follow&method=multiplier&value=3.0`.
- **Execution Steps:**
  1. Send follow request for all 5 followers.
  2. Query Master's followers list via `/user/userCopyFollowers.php?token={master_token}`.
  3. Query each follower's active subscriptions via `/user/userCopyFollowers.php?token={follower_token}`.
- **Expected Result:** Master lists all 5 followers with `status="active"`. Each follower lists Master `1060` in `copyTradingList`.
- **Validation API:** JSON inspection of `copyFollowersList` and `copyTradingList`.
- **Cleanup Requirements:** Keep followers actively subscribed.
- **Evidence Requirements:** Follower subscription payload and relationship verification.

#### `CT-FOL-02`: Follower Unfollow and Subsequent Master Trade Isolation
- **Feature/Module:** Follow/Unfollow Lifecycle
- **Priority:** P1
- **Preconditions:** Follower `ctf5` (`11050`) subscribed to Master. No active positions.
- **Account Setup:** `ctf5` unfollows Master `1060`.
- **Initial Values:** 0 open orders across all accounts.
- **Test Input:** GET `/user/follow.php?follow=1060&type=unfollow` on `ctf5`. Master places $1.00$ lot BUY on `X:BTCUSD`.
- **Execution Steps:**
  1. Unfollow Master from `ctf5`.
  2. Verify `ctf5` status changes to inactive or removed.
  3. Master places $1.00$ lot BUY market order.
  4. Poll order books for all accounts.
- **Expected Result:** Followers `ctf1`–`ctf4` replicate the trade. Follower `ctf5` receives 0 orders.
- **Validation API:** `/book/orders.php` on `ctf5` remains empty.
- **Cleanup Requirements:** Square off Master. Resubscribe `ctf5` to Master (`multiplier=3.0`).
- **Evidence Requirements:** Order book snapshot of `ctf5` showing zero orders while peers have active positions.

---

### Category 3: Multiplier Copy Trading
#### `CT-MUL-01`: Standard Multiplier Scaling (3.0x Proportional Replication)
- **Feature/Module:** Multiplier Copy Trading
- **Priority:** P0
- **Preconditions:** All 5 followers set to `method=multiplier`, `value=3.0`. Master has 0 open orders.
- **Account Setup:** Master lot: $1.00$, Expected Follower lot: $3.00$.
- **Initial Values:** Balance $\ge \$10,000$, Free Margin $\ge \$10,000$.
- **Test Input:** Master places Market BUY $1.00$ lot on `X:BTCUSD`.
- **Execution Steps:**
  1. Master executes Market BUY $1.00$ lot.
  2. Record Master fill timestamp and price.
  3. Poll order books of all 5 followers every $500\text{ms}$ up to $10\text{s}$.
  4. Compare replicated lot size and verify against formula: $\text{FollowerLot} = 1.00 \times 3.0 = 3.00$.
- **Expected Result:** All 5 followers open exactly $3.00$ lots within $2.5\text{s}$. Fill price is within spread markup ($\le 6.0\text{ pts}$).
- **Validation API:** `/book/orders.php` asserting `lot == 3.00` and `symbol == "X:BTCUSD"`.
- **Cleanup Requirements:** Master square-off; verify all 5 followers closed.
- **Evidence Requirements:** Per-follower latency, fill price, and lot assertions.

#### `CT-MUL-02`: Asymmetric Multipliers Across Followers (1.0x, 2.0x, 3.0x, 0.5x, 5.0x)
- **Feature/Module:** Multiplier Copy Trading
- **Priority:** P1
- **Preconditions:** Followers configured with distinct multipliers: `ctf1` (1.0x), `ctf2` (2.0x), `ctf3` (3.0x), `ctf4` (0.5x), `ctf5` (5.0x).
- **Account Setup:** Asymmetric multiplier matrix.
- **Initial Values:** 0 open orders.
- **Test Input:** Master places Market SELL $1.00$ lot on `X:BTCUSD`.
- **Execution Steps:**
  1. Configure multipliers on all 5 followers via `/user/updateCopyTradingMethod.php`.
  2. Master places $1.00$ lot SELL.
  3. Poll all 5 follower order books.
  4. Assert `ctf1`=1.00, `ctf2`=2.00, `ctf3`=3.00, `ctf4`=0.50, `ctf5`=5.00 lots.
- **Expected Result:** Each follower replicates the exact configured multiplier independently.
- **Validation API:** `/book/orders.php` lot checks per follower.
- **Cleanup Requirements:** Master square-off. Reset all followers to 3.0x.
- **Evidence Requirements:** Multiplier configuration response and order book verification table.

---

### Category 4: Balance-Based Copy Trading
#### `CT-BAL-01`: Proportional Balance-Based Lot Sizing ($12.2\text{M} / 111.2\text{M} \to 0.11\text{ lots}$)
- **Feature/Module:** Balance-Based Copy Trading
- **Priority:** P1
- **Preconditions:** All 5 followers switched to `method=balance`.
- **Account Setup:** Query live ledger balance of Master and Followers via `/book/balance.php`.
- **Initial Values:** Master Balance $\approx \$111.22\text{M}$, Follower Balance $\approx \$12.23\text{M}$.
- **Test Input:** Master places Market BUY $1.00$ lot. Expected ratio: $\frac{12.23}{111.22} \times 1.00 = 0.1099 \to 0.11\text{ lots}$.
- **Execution Steps:**
  1. Update all followers to `method=balance` via `/user/updateCopyTradingMethod.php`.
  2. Fetch initial balance for Master and all followers.
  3. Calculate expected lot size using broker rounding rules.
  4. Master places $1.00$ lot BUY.
  5. Poll follower order books and assert exact lot equality ($0.11$).
- **Expected Result:** All 5 followers replicate with exactly $0.11$ lots within $2.5\text{s}$.
- **Validation API:** `/book/orders.php` asserting `lot == 0.11`.
- **Cleanup Requirements:** Master square-off. Verify all followers closed.
- **Evidence Requirements:** Balance query payloads, mathematical calculation proof, and follower order snapshots.

#### `CT-BAL-02`: Follower Balance Variation Leading to Distinct Replicated Lots
- **Feature/Module:** Balance-Based Copy Trading
- **Priority:** P2
- **Preconditions:** Followers have different balances (via admin deposit/withdrawal or differential accounts).
- **Account Setup:** Balance ratio variation.
- **Initial Values:** Distinct balances across followers.
- **Test Input:** Master places $2.00$ lots.
- **Execution Steps:**
  1. Record balances across all 5 followers.
  2. Compute theoretical lot for each follower: $\text{Lot}_i = \text{Round}\left(\frac{\text{Bal}_i}{\text{Bal}_M} \times 2.00, 0.01\right)$.
  3. Master places $2.00$ lots.
  4. Verify each follower opens their specific computed volume.
- **Expected Result:** Follower volumes dynamically scale in proportion to each follower's specific account balance.
- **Validation API:** `/book/orders.php` and `/book/balance.php`.
- **Cleanup Requirements:** Master square-off. Reset to multiplier mode.
- **Evidence Requirements:** Comparative balance vs lot size verification table.

---

### Category 5: Equity-Based Copy Trading
#### `CT-EQU-01`: Proportional Equity-Based Sizing Verification
- **Feature/Module:** Equity-Based Copy Trading
- **Priority:** P1
- **Preconditions:** All 5 followers switched to `method=equity`.
- **Account Setup:** Query live equity via `/book/balance.php`.
- **Initial Values:** Follower Equity $\approx \$12.23\text{M}$, Master Equity $\approx \$111.22\text{M}$.
- **Test Input:** Master places Market BUY $1.00$ lot.
- **Execution Steps:**
  1. Switch followers to `method=equity`.
  2. Read initial equity for Master and all 5 followers.
  3. Master places $1.00$ lot BUY on `X:BTCUSD`.
  4. Poll follower order books and assert lot size matches equity ratio ($0.11\text{ lots}$).
- **Expected Result:** Followers open positions with lot volume matching the live equity ratio.
- **Validation API:** `/book/orders.php` asserting `lot == 0.11`.
- **Cleanup Requirements:** Master square-off. Teardown all positions. Reset to multiplier.
- **Evidence Requirements:** Equity query payloads, mathematical proof, and follower tickets.

---

### Category 6: Market Orders
#### `CT-MKT-01`: Rapid Market Order Execution and Latency SLA ($\le 2.5\text{s}$)
- **Feature/Module:** Market Orders
- **Priority:** P0
- **Preconditions:** All followers following Master (`multiplier=3.0`). 0 open positions.
- **Account Setup:** Clean slate.
- **Initial Values:** Accounts idle.
- **Test Input:** Master places Market BUY $1.00$ lot on `X:BTCUSD`.
- **Execution Steps:**
  1. Record $T_0$ when Master `/trade/placeorder.php` is initiated.
  2. Record $T_1$ when Master receives fill response.
  3. Concurrently poll all 5 follower order books every $200\text{ms}$.
  4. Record $T_{\text{fill}, i}$ when follower $i$ order appears in `/book/orders.php`.
  5. Assert $T_{\text{fill}, i} - T_1 \le 2.5\text{ seconds}$ for all 5 followers.
- **Expected Result:** 100% replication success across all 5 followers within the $2.5\text{s}$ SLA.
- **Validation API:** Timestamp diffs between Master fill and Follower `/book/orders.php` discovery.
- **Cleanup Requirements:** Master square-off; verify full liquidation.
- **Evidence Requirements:** Per-follower latency breakdown chart and millisecond timestamps.

#### `CT-MKT-02`: Market Order Both Sides Execution (BUY followed by SELL)
- **Feature/Module:** Market Orders
- **Priority:** P0
- **Preconditions:** Clean state.
- **Account Setup:** Default multiplier (3.0x).
- **Test Input:** Master places Market BUY, holds 3s, closes; then places Market SELL, holds 3s, closes.
- **Execution Steps:**
  1. Master places BUY $1.00$ lot. Verify 5 followers open BUY $3.00$ lots.
  2. Master squares off BUY. Verify 5 followers close.
  3. Master places SELL $1.00$ lot. Verify 5 followers open SELL $3.00$ lots.
  4. Master squares off SELL. Verify 5 followers close.
- **Expected Result:** Symmetrical replication and auto-closure on both long and short sides.
- **Validation API:** `/book/orders.php` verifying `bs="buy"` then `bs="sell"`.
- **Cleanup Requirements:** Ensure zero residual orders on both Master and followers.
- **Evidence Requirements:** Order book snapshots for both cycles.

---

### Category 7: Limit Orders
#### `CT-LIM-01`: Buy Limit Pending Order Replication and Propagation
- **Feature/Module:** Limit Orders
- **Priority:** P1
- **Preconditions:** Master and 5 followers idle.
- **Account Setup:** Default multiplier.
- **Initial Values:** CMP probed dynamically (e.g., $\$75,500$).
- **Test Input:** Master places Buy Limit at $\text{CMP} - 50.0\text{ pts}$ ($1.00$ lot).
- **Execution Steps:**
  1. Master submits Buy Limit below CMP.
  2. Poll Master order book; verify status is `pending`.
  3. Poll all 5 follower order books.
  4. Assert followers receive replicated pending orders with appropriate lot size ($3.00$ lots).
- **Expected Result:** Pending limit order replicates across all followers without premature market execution.
- **Validation API:** `/book/orders.php` asserting `type="limit"` and `status="pending"`.
- **Cleanup Requirements:** Master cancels limit order via `/book/cancel.php`. Verify all follower pending orders are cancelled.
- **Evidence Requirements:** Pending order book snapshots on Master and followers.

#### `CT-LIM-02`: Limit Order Master Cancellation Fanout
- **Feature/Module:** Limit Orders
- **Priority:** P1
- **Preconditions:** Active pending limit orders across Master and 5 followers (from CT-LIM-01).
- **Account Setup:** Pending limit orders active.
- **Test Input:** Master sends `/book/cancel.php?id={master_limit_order_id}`.
- **Execution Steps:**
  1. Master cancels pending limit order.
  2. Poll all 5 follower order books every $500\text{ms}$ up to $10\text{s}$.
  3. Assert all follower pending limit orders disappear from `/book/orders.php`.
- **Expected Result:** Follower pending orders are automatically cancelled when Master cancels the pending order.
- **Validation API:** `/book/orders.php` returning empty array for all 6 accounts.
- **Cleanup Requirements:** None (cancellation verified).
- **Evidence Requirements:** Cancellation API response and clean order book confirmations.

---

### Category 8: Stop Orders
#### `CT-STP-01`: Buy Stop and Sell Stop Conditional Replication
- **Feature/Module:** Stop Orders
- **Priority:** P1
- **Preconditions:** Clean accounts.
- **Account Setup:** Default multiplier.
- **Test Input:** Master places Buy Stop at $\text{CMP} + 40.0\text{ pts}$ ($1.00$ lot).
- **Execution Steps:**
  1. Submit conditional Stop order via `/trade/placeorder.php?type=stop`.
  2. Verify Master pending Stop order.
  3. Verify all 5 followers receive replicated Stop order.
- **Expected Result:** Stop order replicates to all 5 followers as pending stop orders with $3.00$ lots.
- **Validation API:** `/book/orders.php`.
- **Cleanup Requirements:** Master cancels stop order via `/book/cancel.php`.
- **Evidence Requirements:** Stop order parameters and book status.

---

### Category 9: Stop BOTH Orders (Dual Breakout Brackets)
#### `CT-BTH-01`: Stop BOTH Dual Bracket Generation Protocol
- **Feature/Module:** Stop BOTH Orders
- **Priority:** P1
- **Preconditions:** Clean state.
- **Account Setup:** Default multiplier.
- **Test Input:** Master submits `type=stop`, `stop_hft_type=2`, `bs=buy`, `lotb=1.00`, `lots=1.00`, `triggerb=CMP+30`, `triggers=CMP-30`.
- **Execution Steps:**
  1. Send Stop BOTH request.
  2. Verify response contains compound order IDs (e.g. `"58777,58778"`).
  3. Poll order books for Master and 5 followers.
- **Expected Result:** Two pending bracket legs (Buy Stop and Sell Stop) are generated for Master and replicated to all 5 followers.
- **Validation API:** `/trade/placeorder.php` response string and `/book/orders.php`.
- **Cleanup Requirements:** Master cancels both bracket legs via `/book/cancel.php`.
- **Evidence Requirements:** Dual order ID extraction and order book snapshot.

#### `CT-BTH-02`: Stop BOTH Residual Bracket Leak Detection ([BUG-03])
- **Feature/Module:** Stop BOTH Orders
- **Priority:** P1
- **Preconditions:** Active dual bracket order on Master and followers.
- **Account Setup:** Default multiplier.
- **Test Input:** Market moves to trigger Buy Stop leg.
- **Execution Steps:**
  1. Monitor active leg conversion to market position.
  2. Square off active market position.
  3. Inspect follower order books for residual Sell Stop pending leg.
- **Expected Result:** Check whether opposite pending bracket leg is automatically cancelled or remains orphaned.
- **Validation API:** `/book/orders.php` checking for residual pending legs.
- **Cleanup Requirements:** Explicitly cancel any residual pending orders on all 6 accounts.
- **Evidence Requirements:** Document whether residual leg persists (logging platform defect BUG-03).

---

### Category 10: Lot Size Calculations
#### `CT-LOT-01`: Fractional Lot Precision and Rounding Validation
- **Feature/Module:** Lot Size Calculations
- **Priority:** P1
- **Preconditions:** Multiplier set to $0.33\text{x}$.
- **Account Setup:** Master lot: $1.00$.
- **Test Input:** Master places $1.00$ lot. Formula: $1.00 \times 0.33 = 0.33\text{ lots}$.
- **Execution Steps:**
  1. Update follower method to `multiplier=0.33`.
  2. Master places $1.00$ lot.
  3. Verify follower order book shows exactly $0.33$ lots (no precision overflow like $0.329999$).
- **Expected Result:** Replicated volume rounds strictly to two decimal places ($0.33$).
- **Validation API:** `/book/orders.php` asserting float equality within $0.001$.
- **Cleanup Requirements:** Master square-off. Reset multiplier to 3.0x.
- **Evidence Requirements:** JSON lot value verification.

#### `CT-LOT-02`: Sub-Minimum Lot Clamping / Rejection Boundary
- **Feature/Module:** Lot Size Calculations
- **Priority:** P2
- **Preconditions:** Multiplier set to $0.005\text{x}$. Master places $1.00$ lot ($\text{Result} = 0.005 < 0.01\text{ min lot}$).
- **Account Setup:** Sub-minimum lot configuration.
- **Test Input:** Master places $1.00$ lot.
- **Execution Steps:**
  1. Set follower multiplier to $0.005$.
  2. Master places $1.00$ lot.
  3. Inspect follower order book and broker error logs.
- **Expected Result:** Follower either clamps lot to minimum broker size ($0.01$) or safely rejects without affecting Master.
- **Validation API:** `/book/orders.php`.
- **Cleanup Requirements:** Master square-off. Reset multiplier to 3.0x.
- **Evidence Requirements:** Log of clamp/rejection behavior.

---

### Category 11: TP/SL Synchronization
#### `CT-TPSL-01`: TP and SL Value Replication with Spread Markup Offset
- **Feature/Module:** TP/SL Synchronization
- **Priority:** P1
- **Preconditions:** Clean accounts. Default multiplier (3.0x).
- **Account Setup:** CMP probed dynamically ($\text{CMP} \approx \$75,500$).
- **Initial Values:** Set Master $\text{TP} = \text{CMP} + 35.0$, $\text{SL} = \text{CMP} - 35.0$.
- **Test Input:** Master places Market BUY with TP/SL.
- **Execution Steps:**
  1. Place Master order with explicit `target` and `sl`.
  2. Poll all 5 follower order books.
  3. Assert TP and SL fields exist on all follower positions.
  4. Verify follower fill price incorporates spread markup ($\approx +5.5\text{ pts}$).
  5. Verify follower SL/TP preserves distance from fill price.
- **Expected Result:** TP and SL propagate to all followers; levels reflect broker spread markup safely.
- **Validation API:** `/book/orders.php` verifying `sl` and `target` keys.
- **Cleanup Requirements:** Master square-off.
- **Evidence Requirements:** TP/SL comparison table across Master and 5 followers.

---

### Category 12: Order Modification
#### `CT-MOD-01`: Dynamic TP/SL Modification Propagation
- **Feature/Module:** Order Modification
- **Priority:** P1
- **Preconditions:** Active replicated market position across Master and 5 followers.
- **Account Setup:** Initial position open.
- **Test Input:** Master modifies StopLoss via `/book/modify.php?id={master_order_id}&name=sl&val={new_sl}`.
- **Execution Steps:**
  1. Master submits modification request for new SL value.
  2. Verify Master order book updates to new SL.
  3. Poll all 5 follower order books.
  4. Assert whether follower positions automatically update to modified SL or retain original SL.
- **Expected Result:** Determine whether modification fans out to followers or requires manual follower action.
- **Validation API:** `/book/orders.php` inspecting `sl` on Master and Followers.
- **Cleanup Requirements:** Master square-off.
- **Evidence Requirements:** Modification API payload and updated order book snapshots.

---

### Category 13: Partial and Full Square-Off
#### `CT-SQO-01`: Full Position Square-Off Lifecycle
- **Feature/Module:** Partial and Full Square-Off
- **Priority:** P0
- **Preconditions:** Active position open on Master ($1.00$ lot) and 5 followers ($3.00$ lots).
- **Account Setup:** Open positions active.
- **Test Input:** Master calls `/book/squareoff.php?id={master_order_id}`.
- **Execution Steps:**
  1. Master initiates square-off.
  2. Poll Master order book until order is completely absent.
  3. Poll all 5 follower order books until all orders are completely absent.
  4. Assert all closures complete within $3.0\text{ seconds}$.
- **Expected Result:** 100% position liquidation across Master and all 5 followers.
- **Validation API:** `/book/orders.php` returning length 0 for all 6 accounts.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Square-off latency log and empty book confirmation.

#### `CT-SQO-02`: Master Partial Position Closure Propagation
- **Feature/Module:** Partial and Full Square-Off
- **Priority:** P1
- **Preconditions:** Master opens $2.00$ lots. 5 followers replicate $6.00$ lots ($3.0\text{x}$).
- **Account Setup:** Large position size.
- **Test Input:** Master partially closes $1.00$ lot via `/book/squareoff.php?close_mode=partial&partial_lot=1.00`.
- **Execution Steps:**
  1. Master submits partial close of $1.00$ lot.
  2. Verify Master remaining position is $1.00$ lot.
  3. Poll all 5 follower order books.
  4. Verify follower positions partially reduce to $3.00$ lots ($50\%$ partial close).
- **Expected Result:** Followers partially close volume proportional to Master's partial closure ratio.
- **Validation API:** `/book/orders.php` asserting remaining `lot == 3.00` on followers.
- **Cleanup Requirements:** Master squares off remaining $1.00$ lot.
- **Evidence Requirements:** Partial square-off request/response and updated lot verification.

---

### Category 14: Master Square-Off Fanout
#### `CT-FAN-01`: Multi-Follower Fanout Latency & Completeness SLA
- **Feature/Module:** Master Square-Off Fanout
- **Priority:** P0
- **Preconditions:** All 5 followers have active replicated positions.
- **Account Setup:** 5 followers running.
- **Test Input:** Master triggers square-off.
- **Execution Steps:**
  1. Record timestamp $T_{\text{sqo}}$.
  2. Master sends `/book/squareoff.php`.
  3. Concurrently poll all 5 follower order books every $200\text{ms}$.
  4. Measure exact closure timestamp $T_{\text{closed}, i}$ for each follower.
  5. Assert $\max(T_{\text{closed}, i}) - T_{\text{sqo}} \le 3.5\text{s}$.
- **Expected Result:** All 5 followers liquidated cleanly with zero hanging/orphaned tickets.
- **Validation API:** `/book/orders.php` per follower.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Fanout closure waterfall chart.

---

### Category 15: Follower Isolation (Peer Independence)
#### `CT-ISO-01`: Single Follower Manual Square-Off Isolation
- **Feature/Module:** Follower Isolation
- **Priority:** P0
- **Preconditions:** Master has $1.00$ lot open. All 5 followers have $3.00$ lots open.
- **Account Setup:** 6 concurrent active positions.
- **Test Input:** Follower `ctf2` (`11043`) executes `/book/squareoff.php?id={ctf2_order_id}`.
- **Execution Steps:**
  1. `ctf2` squares off their own position.
  2. Verify `ctf2` order book is empty.
  3. Verify Master order book STILL HAS $1.00$ lot open.
  4. Verify `ctf1`, `ctf3`, `ctf4`, `ctf5` STILL HAVE $3.00$ lots open.
- **Expected Result:** Early follower exit is completely isolated; Master and peer followers are unaffected.
- **Validation API:** `/book/orders.php` across all 6 accounts.
- **Cleanup Requirements:** Master square-off; verify remaining followers close.
- **Evidence Requirements:** Order book status matrix demonstrating peer isolation.

---

### Category 16: Funds and Balance Management
#### `CT-FND-01`: Realized P&L Ledger Settlement Verification
- **Feature/Module:** Funds and Balance Management
- **Priority:** P1
- **Preconditions:** Clean accounts. Record baseline balances via `/book/balance.php`.
- **Account Setup:** Baseline balance captured.
- **Test Input:** Master opens and closes a trade that moves into profit or loss.
- **Execution Steps:**
  1. Record initial balance $B_{\text{initial}}$ for Master and followers.
  2. Execute trade and square off after price moves.
  3. Query `/book/balance.php` post-trade ($B_{\text{final}}$).
  4. Verify $B_{\text{final}} - B_{\text{initial}} == \text{Realized P\&L} - \text{Commission}$.
- **Expected Result:** Realized P&L is accurately credited or debited to follower ledger balances.
- **Validation API:** `/book/balance.php`.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Balance reconciliation diff before and after trade.

---

### Category 17: Margin and Free Margin
#### `CT-MAR-01`: Margin Utilization and Free Margin Deduction upon Replication
- **Feature/Module:** Margin and Free Margin
- **Priority:** P1
- **Preconditions:** Clean accounts. Baseline margin recorded.
- **Account Setup:** Initial free margin $\approx \$12.2\text{M}$.
- **Test Input:** Master places Market BUY $1.00$ lot. Followers open $3.00$ lots.
- **Execution Steps:**
  1. Query pre-trade margin on followers: `margin`, `free_margin`.
  2. Master executes trade. Followers replicate.
  3. Query post-trade margin on followers.
  4. Assert: $\text{Free Margin}_{\text{post}} < \text{Free Margin}_{\text{pre}}$ and $\text{Used Margin} > 0$.
- **Expected Result:** Replicated position correctly reserves required margin on follower account.
- **Validation API:** `/book/balance.php`.
- **Cleanup Requirements:** Master square-off.
- **Evidence Requirements:** Margin calculation verification before and after fill.

---

### Category 18: Margin Call
#### `CT-MC-01`: Margin Level Threshold Warning Behavior
- **Feature/Module:** Margin Call
- **Priority:** P2
- **Preconditions:** Follower account with reduced free margin (via withdrawal or high leverage).
- **Account Setup:** Low margin level setup.
- **Test Input:** Follower margin level drops below broker warning threshold ($100\%$).
- **Execution Steps:**
  1. Query follower account margin level.
  2. Attempt to replicate additional master order.
  3. Inspect platform warning response or replication restriction.
- **Expected Result:** Broker flags margin call status; subsequent orders restricted if margin level is critical.
- **Validation API:** `/book/balance.php` inspecting `margin_level`.
- **Cleanup Requirements:** Ensure account returns to healthy margin state.
- **Evidence Requirements:** Margin call status log.

---

### Category 19: Stop-Out and Automatic Liquidation
#### `CT-STO-01`: Broker Stop-Out Liquidation Isolation
- **Feature/Module:** Stop-Out and Automatic Liquidation
- **Priority:** P2
- **Preconditions:** One follower account equity drops below broker liquidation threshold (e.g. $20\%-50\%$).
- **Account Setup:** Simulating stop-out condition on follower.
- **Test Input:** Forced liquidation event on single follower.
- **Execution Steps:**
  1. Monitor single follower liquidation.
  2. Assert single follower position is auto-liquidated by matching engine.
  3. Verify Master position and remaining 4 healthy followers REMAIN OPEN.
- **Expected Result:** Stop-out liquidation is strictly isolated to the distressed follower.
- **Validation API:** `/book/orders.php` and `/book/balance.php`.
- **Cleanup Requirements:** Master square-off.
- **Evidence Requirements:** Liquidation event log and peer account stability verification.

---

### Category 20: Insufficient Margin
#### `CT-INM-01`: Insufficient Margin Rejection on Follower Replication
- **Feature/Module:** Insufficient Margin
- **Priority:** P1
- **Preconditions:** Follower configured with extreme multiplier (e.g., $100.0\text{x}$) or balance depleted.
- **Account Setup:** `ctf1` multiplier set to $100.0\text{x}$.
- **Initial Values:** Master places $5.00$ lots (requires $500.00$ lots on follower, exceeding margin).
- **Test Input:** Master places Market BUY $5.00$ lots.
- **Execution Steps:**
  1. Update `ctf1` to `multiplier=100.0`.
  2. Master places $5.00$ lots.
  3. Poll order books across all accounts.
  4. Assert Master fills $5.00$ lots.
  5. Assert followers `ctf2`–`ctf5` (at 3.0x) fill $15.00$ lots.
  6. Assert `ctf1` order is cleanly rejected with `ERR_INSUFFICIENT_MARGIN` without hanging queue.
- **Expected Result:** Over-leveraged follower is rejected gracefully; Master and other followers execute unaffected.
- **Validation API:** `/book/orders.php`.
- **Cleanup Requirements:** Master square-off. Reset `ctf1` to 3.0x.
- **Evidence Requirements:** Rejection payload and peer execution logs.

---

### Category 21: Network Failure and Recovery
#### `CT-NET-01`: Temporary API Disconnection and Re-Authentication Recovery
- **Feature/Module:** Network Failure and Recovery
- **Priority:** P2
- **Preconditions:** Active sessions running.
- **Account Setup:** Simulate session timeout or network disconnect.
- **Test Input:** Expire session token or sever connection, then attempt order query.
- **Execution Steps:**
  1. Clear cached session cookie/token on follower client.
  2. Execute query requiring authentication.
  3. Automated client intercepts `status=fail`, invokes `authenticate()`, and retries request.
  4. Verify request succeeds on retry without dropping test execution.
- **Expected Result:** Automation framework gracefully recovers from session expiration and resumes execution.
- **Validation API:** Re-authentication response and retried query output.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Network reconnect log and retry telemetry.

---

### Category 22: Duplicate Order Prevention
#### `CT-DUP-01`: Idempotent Order Placement Guard (Fingerprint & Token Protection)
- **Feature/Module:** Duplicate Order Prevention
- **Priority:** P1
- **Preconditions:** Master session active.
- **Account Setup:** Rapid duplicate submission test.
- **Test Input:** Master submits exact identical order request twice within $50\text{ms}$ with same fingerprint.
- **Execution Steps:**
  1. Fire two identical HTTP requests with same fingerprint to `/trade/placeorder.php`.
  2. Inspect response codes and order books.
  3. Verify whether broker deduplicates request or rejects second order as duplicate.
- **Expected Result:** Engine rejects duplicate fingerprint or executes only 1 order, preventing double fill.
- **Validation API:** `/trade/placeorder.php` responses and `/book/orders.php` order count.
- **Cleanup Requirements:** Master square-off.
- **Evidence Requirements:** Duplicate submission telemetry.

---

### Category 23: Concurrent Execution
#### `CT-CON-01`: Rapid Master Multi-Order Placement Pacing and Fanout Integrity
- **Feature/Module:** Concurrent Execution
- **Priority:** P2
- **Preconditions:** Clean accounts. Default multiplier.
- **Account Setup:** Sequential rapid order burst.
- **Test Input:** Master places 3 consecutive market orders ($1.00$ lot each) spaced $1.0\text{s}$ apart.
- **Execution Steps:**
  1. Place Order 1, wait 1.0s.
  2. Place Order 2, wait 1.0s.
  3. Place Order 3.
  4. Poll all 5 follower order books.
  5. Assert each follower holds exactly 3 corresponding positions ($3.00$ lots each).
  6. Verify fanout queue does not drop or reorder tickets.
- **Expected Result:** All 3 orders replicated cleanly across all 5 followers (total 15 follower positions).
- **Validation API:** `/book/orders.php` asserting `len(orders) == 3` for all 6 accounts.
- **Cleanup Requirements:** Master squares off all positions. Verify all 15 follower orders liquidated.
- **Evidence Requirements:** Burst order submission log and order book audit.

---

### Category 24: Pending Order Cancellation
#### `CT-CAN-01`: Pending Limit/Stop Order Cancellation Synchronization
- **Feature/Module:** Pending Order Cancellation
- **Priority:** P1
- **Preconditions:** Pending Buy Limit placed across Master and 5 followers.
- **Account Setup:** Active pending limit orders.
- **Test Input:** Master cancels order via `/book/cancel.php?id={master_pending_id}`.
- **Execution Steps:**
  1. Record pending order IDs for Master and followers.
  2. Master sends cancel request.
  3. Poll all 5 follower order books.
  4. Verify all pending follower orders are cancelled within $2.5\text{s}$.
- **Expected Result:** Master cancellation fans out and purges pending orders from all follower accounts.
- **Validation API:** `/book/orders.php` asserting 0 pending orders.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Cancellation timestamps and verification of empty pending books.

---

### Category 25: Data Integrity and Reconciliation
#### `CT-INT-01`: End-to-End Position Book vs Database Ledger Reconciliation
- **Feature/Module:** Data Integrity and Reconciliation
- **Priority:** P2
- **Preconditions:** All trades squared off.
- **Account Setup:** Idle state after a completed trade cycle.
- **Test Input:** Reconcile open orders, balance, margin, and copy subscription status.
- **Execution Steps:**
  1. Poll `/book/orders.php` for Master and all 5 followers: assert `len == 0`.
  2. Poll `/book/balance.php` for all accounts: assert `used_margin == 0` and `free_margin == balance`.
  3. Poll `/user/userCopyFollowers.php`: assert all 5 followers remain actively subscribed to Master `1060`.
  4. Verify zero orphan records or stuck locks.
- **Expected Result:** 100% system consistency; zero residual orders, zero stuck margin, all accounts healthy.
- **Validation API:** `/book/orders.php`, `/book/balance.php`, `/user/userCopyFollowers.php`.
- **Cleanup Requirements:** None.
- **Evidence Requirements:** Complete system reconciliation audit report.

---

## 3. Priority Summary Matrix

| Priority | Categories Covered | Scenario IDs | Primary Automation Focus |
|---|---|---|---|
| **P0** | 1, 2, 3, 6, 13, 14, 15 | `CT-ACC-01`, `CT-FOL-01`, `CT-MUL-01`, `CT-MKT-01`, `CT-MKT-02`, `CT-SQO-01`, `CT-FAN-01`, `CT-ISO-01` | Auth, Account ID guard, Bulk follow, Multiplier scaling, Market execution, Square-off fanout, Peer isolation |
| **P1** | 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 16, 17, 20, 22, 24 | `CT-ACC-02`, `CT-FOL-02`, `CT-MUL-02`, `CT-BAL-01`, `CT-EQU-01`, `CT-LIM-01`, `CT-LIM-02`, `CT-STP-01`, `CT-BTH-01`, `CT-BTH-02`, `CT-LOT-01`, `CT-TPSL-01`, `CT-MOD-01`, `CT-SQO-02`, `CT-FND-01`, `CT-MAR-01`, `CT-INM-01`, `CT-DUP-01`, `CT-CAN-01` | Balance mode, Equity mode, Asymmetric multipliers, Limit/Stop replication, Stop BOTH brackets, TP/SL offset, Order modify, Realized P&L, Margin deduct, Pending cancellation |
| **P2** | 4, 10, 18, 19, 21, 23, 25 | `CT-BAL-02`, `CT-LOT-02`, `CT-MC-01`, `CT-STO-01`, `CT-NET-01`, `CT-CON-01`, `CT-INT-01` | Balance variations, Min lot clamping, Margin call warning, Stop-out isolation, Reconnect retry, Concurrency burst, Reconciliation |

