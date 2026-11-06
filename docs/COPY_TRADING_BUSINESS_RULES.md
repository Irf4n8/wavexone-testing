# WavexOne Copy Trading: Complete Business Rules & Logic Specifications

**Document Version:** 1.0.0  
**Environment:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** Core Financial Business Rules & Expected Broker Behavior  
**Author:** Senior QA Automation Architect (Financial Trading & Brokerage Platforms)

---

## 1. Account Sizing & Lot Calculation Business Rules

### Rule BR-LOT-01: Multiplier Sizing Logic
- **Definition:** Follower lot size is directly proportional to Master lot size by a fixed user-defined multiplier coefficient.
- **Formula:**
  $$\text{Lot}_{\text{follower}} = \text{Round}(\text{Lot}_{\text{master}} \times \text{Multiplier}, 2)$$
- **Constraints:**
  - Multiplier must be strictly $> 0$ (e.g., `3.0`).
  - Staging Master placements strictly use `1.00` whole lot $\implies$ Follower replicates strictly **`3.00` lots**.
  - Minimum lot size permitted: `0.01` lot.
  - Maximum lot size permitted: Subject to account group/risk limits (default `100.00` lots).

---

### Rule BR-LOT-02: Balance-Based Proportional Sizing Logic
- **Definition:** Follower lot size scales dynamically according to the ratio of the Follower's balance to the Master's balance at the exact millisecond of order placement.
- **Formula:**
  $$\text{Ratio} = \frac{\text{Follower Balance}}{\text{Master Balance}}$$
  $$\text{Lot}_{\text{follower}} = \text{Round}(\text{Lot}_{\text{master}} \times \text{Ratio}, 2)$$
- **Live Staging Application:**
  - Master Balance: $\approx \$111,221,862.00$
  - Follower Balance (`ctf1`): $\approx \$12,233,121.00$
  - Calculated Ratio: $\frac{12.233\text{M}}{111.221\text{M}} \approx 0.10998$
  - Master $1.00$ lot order $\implies \text{Round}(1.00 \times 0.10998, 2) = \mathbf{0.11\text{ lots}}$.
- **Boundary Handling:** If calculated lot is $< 0.01$, engine must either round up to the broker minimum (`0.01`) or reject placement with `Lot below minimum threshold`.

---

### Rule BR-LOT-03: Equity-Based Proportional Sizing Logic
- **Definition:** Follower lot size scales dynamically according to the live floating equity ratio between Follower and Master.
- **Formula:**
  $$\text{Ratio}_{\text{equity}} = \frac{\text{Follower Equity}}{\text{Master Equity}}$$
  $$\text{Lot}_{\text{follower}} = \text{Round}(\text{Lot}_{\text{master}} \times \text{Ratio}_{\text{equity}}, 2)$$
- **Business Purpose:** Protects followers if Master is holding significant floating drawdown (Master Equity $<$ Master Balance), ensuring follower does not take oversized risk relative to Master's true liquidation value.
- **Staging Defect ([BUG-04]):** Because Staging statically reports `equity == balance` during open trades, the equity ratio is currently identical to the balance ratio ($0.11$ lots).

---

## 2. Order Placement & Spread Bridge Rules

### Rule BR-ORD-01: Master Sizing Wholeness
- **Specification:** Placements by Master in automated test scenarios must use **1.00 whole lots** (no decimals on placement) to prevent rounding anomalies on the master side.

### Rule BR-ORD-02: Spread Markup & Pricing Offset
- **Specification:** Master order executes at broker base CMP. Follower order executes with a configured broker markup of **5.4 to 5.6 points** on `X:BTCUSD`.
- **Impact on TP/SL Configuration:**
  - When setting tight TP/SL on Master, the price offset **must be at least 8.0 to 10.0 points** away from CMP.
  - Setting offsets $\le 5.0$ points causes immediate rejection or instant fill on the follower due to the 5.5-point spread markup bridge.

### Rule BR-ORD-03: Stop HFT BOTH Protocol Requirement
- **Specification:** When placing a Stop HFT BOTH bracket (`stop_hft_type=2`), the query parameter `bs` **must strictly be set to `buy`** (`bs=buy`). The backend server parses this into dual linked legs returning comma-separated IDs (e.g. `orderId: "58777,58778"`).

---

## 3. Order Replication & Fanout Service Level Agreements (SLAs)

### Rule BR-REP-01: Fanout Replication SLA
- **Specification:** When Master places an order, all active followers must replicate the order in their respective books within **$\le 2.0$ seconds** under standard conditions, and $\le 5.0$ seconds under market volatility.
- **Validation:** Master order ID and Follower cloned order IDs must be independently verified.

### Rule BR-REP-02: Stop Loss & Take Profit Propagation
- **Specification:** Cloned follower orders must inherit exact numerical Stop Loss (`sl`) and Take Profit (`tp`) price levels configured on the Master order.

---

## 4. Position Closure & Auto Square-Off Rules

### Rule BR-EXIT-01: Take Profit Auto-Closure
- **Specification:** When live CMP ticks and touches the Take Profit level, the brokerage matching engine must trigger auto square-off.
- **Master Action:** Master position is closed automatically by the broker.
- **Follower Action:** All 5 follower cloned positions must close automatically and synchronously without manual square-off requests.

### Rule BR-EXIT-02: Stop Loss Auto-Closure
- **Specification:** When live CMP ticks and touches the Stop Loss level, the brokerage matching engine must execute auto square-off within $\le 2.5$ seconds across Master and all followers.

### Rule BR-EXIT-03: Master Manual Square-Off Fanout
- **Specification:** When Master manually calls `/book/squareoff.php`, the server fanout queue must execute synchronous square-off on all connected followers.
- **Latency SLA:** All follower cloned orders must be closed within **$\le 3.0$ seconds** of Master square-off.

### Rule BR-EXIT-04: Partial Square-Off Proportional Reduction
- **Specification:** When Master closes a partial position lot (e.g. 0.50 of 1.00 lot, a 50% reduction), each follower's active position must reduce proportionally by the same percentage (e.g. 3.00 lots reduces to 1.50 lots).

### Rule BR-EXIT-05: Follower Early Manual Square-Off (Peer Isolation)
- **Specification:** If an individual follower manually closes their cloned position via their own terminal:
  1. Only that follower's position is closed.
  2. Master position **must remain open and completely unaffected**.
  3. Peer followers (`ctf2`–`ctf5`) **must remain open and completely unaffected**.
  4. When Master eventually squares off, the already-closed follower must not receive duplicate close errors.

### Rule BR-EXIT-06: Pending Order Cancellation Propagation
- **Specification:** When Master cancels a pending Limit or Stop order via `/book/cancel.php`, cloned pending orders on all followers must be cancelled and disappear from `/book/orders.php` within $\le 2.0$ seconds.

---

## 5. Account Lifecycle & Subscription Protection Rules

### Rule BR-SUB-01: Unfollow During Open Position
- **Expected Specification:** When a follower unfollows a Master while holding an open copied position:
  - The open position must transition to an independent position under follower management, OR the UI must warn the user to close open trades before unfollowing.
- **Platform Bug ([BUG-02]):** On Staging, the follower position currently remains in the book, but when the Master later squares off, the engine still executes a square-off on the unfollowed user.

### Rule BR-SUB-02: Teardown & Account Integrity Guarantee
- **Specification:** At the completion of any test scenario or automated suite:
  - Total open positions across all 6 accounts must equal **0**.
  - Total pending orders across all 6 accounts must equal **0**.
  - Follower subscriptions must be verified restored to `method="multiplier"`, `value="3.0"` following Master `1060`.

