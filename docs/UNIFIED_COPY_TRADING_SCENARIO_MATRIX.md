# WavexOne Unified Copy Trading QA Scenario Matrix

**Document Version:** 1.0.0  
**Effective Date:** 2026-11-06  
**Scope:** Consolidated Master Test Scenario Inventory  

---

## 1. Scenario Catalog Overview

The Unified Copy Trading QA Framework consolidates 271 legacy test items into a deduplicated, rigorous matrix of **65 Unique Enterprise Scenarios** organized across 8 functional modules:

| Module Code | Module Description | Unique Scenarios | Legacy Overlap Removed |
| :--- | :--- | :---: | :---: |
| **MOD-ENV** | Environment, Authentication & Subscription | 4 | 12 |
| **MOD-MUL** | Multiplier Mode Order Type Matrix (3.0x) | 14 | 28 |
| **MOD-BAL** | Balance-Based Mode Order Type Matrix | 14 | 28 |
| **MOD-EQU** | Equity-Based Mode Order Type Matrix | 14 | 28 |
| **MOD-INF** | In-Flight Modifications, Partial Close & Burst Concurrency | 4 | 8 |
| **MOD-ISO** | Tenant Isolation, Follower Early Close & Unfollow/Re-Follow | 3 | 6 |
| **MOD-RSK** | Margin Level 50% Stop-Out, Boundary & Purging | 10 | 90 |
| **MOD-REC** | Commissions, Withdrawal Locks & Final Reconciliation | 2 | 6 |
| **TOTAL** | **Consolidated Unified QA Matrix** | **65** | **206 Duplicates Purged** |

---

## 2. Complete Scenario Inventory

### Module 1: Environment, Authentication & Subscription (MOD-ENV)
- `ENV-01`: Target environment validation (`stage.wavexone.com`, credentials scrubbed, production safeguards).
- `ENV-02`: Account inventory & readiness verification (Master `11060`, Followers `11041`-`11050`, leverage 1:500, USD currency).
- `ENV-03`: Follower subscription status audit (`/social/getFollowers.php`, active following links).
- `ENV-04`: Copy configuration baseline verification (Multiplier 3.0x on Master 1060).

### Module 2: Multiplier Mode Order Types (MOD-MUL)
*Master Lot = 0.50 $\implies$ Follower Lot = 1.50 ($0.50 \times 3.0$)*
- `MUL-MKT-BUY-NO`: Market BUY without TP/SL.
- `MUL-MKT-BUY-TP`: Market BUY with TP and SL.
- `MUL-MKT-SEL-NO`: Market SELL without TP/SL.
- `MUL-MKT-SEL-TP`: Market SELL with TP and SL.
- `MUL-LMT-BUY-NO`: Limit BUY without TP/SL.
- `MUL-LMT-BUY-TP`: Limit BUY with TP and SL.
- `MUL-LMT-SEL-NO`: Limit SELL without TP/SL.
- `MUL-LMT-SEL-TP`: Limit SELL with TP and SL.
- `MUL-STP-BUY-NO`: Stop HFT BUY without TP/SL.
- `MUL-STP-BUY-TP`: Stop HFT BUY with TP and SL.
- `MUL-STP-SEL-NO`: Stop HFT SELL without TP/SL.
- `MUL-STP-SEL-TP`: Stop HFT SELL with TP and SL.
- `MUL-STP-BTH-NO`: Stop HFT BOTH dual-leg without TP/SL.
- `MUL-STP-BTH-TP`: Stop HFT BOTH dual-leg with TP and SL.

### Module 3: Balance-Based Mode Order Types (MOD-BAL)
*Master Lot = 0.50 $\implies$ Follower Lot = 0.05 ($0.50 \times \text{Balance Ratio} \approx 0.109$)*
- `BAL-MKT-BUY-NO`: Market BUY without TP/SL.
- `BAL-MKT-BUY-TP`: Market BUY with TP and SL.
- `BAL-MKT-SEL-NO`: Market SELL without TP/SL.
- `BAL-MKT-SEL-TP`: Market SELL with TP and SL.
- `BAL-LMT-BUY-NO`: Limit BUY without TP/SL.
- `BAL-LMT-BUY-TP`: Limit BUY with TP and SL.
- `BAL-LMT-SEL-NO`: Limit SELL without TP/SL.
- `BAL-LMT-SEL-TP`: Limit SELL with TP and SL.
- `BAL-STP-BUY-NO`: Stop HFT BUY without TP/SL.
- `BAL-STP-BUY-TP`: Stop HFT BUY with TP and SL.
- `BAL-STP-SEL-NO`: Stop HFT SELL without TP/SL.
- `BAL-STP-SEL-TP`: Stop HFT SELL with TP and SL.
- `BAL-STP-BTH-NO`: Stop HFT BOTH dual-leg without TP/SL.
- `BAL-STP-BTH-TP`: Stop HFT BOTH dual-leg with TP and SL.

### Module 4: Equity-Based Mode Order Types (MOD-EQU)
*Master Lot = 0.50 $\implies$ Follower Lot = 0.05 ($0.50 \times \text{Equity Ratio} \approx 0.109$)*
- `EQU-MKT-BUY-NO`: Market BUY without TP/SL.
- `EQU-MKT-BUY-TP`: Market BUY with TP and SL.
- `EQU-MKT-SEL-NO`: Market SELL without TP/SL.
- `EQU-MKT-SEL-TP`: Market SELL with TP and SL.
- `EQU-LMT-BUY-NO`: Limit BUY without TP/SL.
- `EQU-LMT-BUY-TP`: Limit BUY with TP and SL.
- `EQU-LMT-SEL-NO`: Limit SELL without TP/SL.
- `EQU-LMT-SEL-TP`: Limit SELL with TP and SL.
- `EQU-STP-BUY-NO`: Stop HFT BUY without TP/SL.
- `EQU-STP-BUY-TP`: Stop HFT BUY with TP and SL.
- `EQU-STP-SEL-NO`: Stop HFT SELL without TP/SL.
- `EQU-STP-SEL-TP`: Stop HFT SELL with TP and SL.
- `EQU-STP-BTH-NO`: Stop HFT BOTH dual-leg without TP/SL.
- `EQU-STP-BTH-TP`: Stop HFT BOTH dual-leg with TP and SL.

### Module 5: In-Flight Lifecycle & Concurrency (MOD-INF)
- `INF-01`: Mid-trade StopLoss and Target price modification fanout across all 5 followers.
- `INF-02`: Partial position close fanout under Multiplier mode (0.50 $\to$ 0.30 lot $\implies$ Follower 1.50 $\to$ 0.90 lot).
- `INF-03`: Partial position close fanout under Balance mode (0.50 $\to$ 0.30 lot $\implies$ Follower 0.05 $\to$ 0.03 lot).
- `INF-04`: Rapid-fire burst concurrency stress test (4 orders in $< 2\text{s}$, queue depth and mass exit).

### Module 6: Tenant Isolation & Subscription Dynamics (MOD-ISO)
- `ISO-01`: Follower manual early exit (closes child ticket; Master and peers remain intact).
- `ISO-02`: Follower independent trade placement (does NOT copy to Master or peers).
- `ISO-03`: Unfollow and re-follow subscription cycle (`/social/unfollowMaster.php` and `/social/followMaster.php`).

### Module 7: Margin Stop-Out & Broker Risk Rules (MOD-RSK)
- `RSK-01`: Margin Level at 60% (Safe Boundary / No Premature Liquidation).
- `RSK-02`: Margin Level at Exactly 50% (Stop-Out Trigger Threshold) — *Classified BLOCKED due to staging capital*.
- `RSK-03`: Margin Level at 45% (Critical Stop-Out Zone) — *Classified BLOCKED due to staging capital*.
- `RSK-04`: Individual follower stop-out (Account isolation and peer protection).
- `RSK-05`: Master stop-out liquidation fanout to all replicated child tickets.
- `RSK-06`: Multiple open positions Used Margin additive aggregation and closure.
- `RSK-07`: Pending orders purging during stop-out via cancellation.
- `RSK-08`: Simultaneous stop-out across multiple followers (parallel race condition immunity).
- `RSK-09`: Duplicate trigger prevention (OMS idempotency guard against double-close).
- `RSK-10`: Post-liquidation account terminal state audit (Used Margin = \$0.00, Free Margin = Equity).

### Module 8: Commissions, Withdrawal Locks & Final Reconciliation (MOD-REC)
- `REC-01`: Commissions, overnight swaps, and profit-sharing high-water mark discovery.
- `REC-02`: Withdrawal limits and open order margin reservation audit.
- `REC-03`: End-to-end cross-account ticket reconciliation & final clean-slate audit.
