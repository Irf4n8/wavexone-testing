# 📈 WavexOne Copy Trading End-to-End QA Automation Report

**Target Environment:** Staging (`https://stage.wavexone.com`)  
**Execution Timestamp:** 2026-11-05  
**Test Suites:**
1. `tests/test_copy_trading.py::TestCopyTradingSuite` (15 Core Tests)
2. `tests/test_copy_trading_matrix.py::TestCopyTradingMatrixSuite` (21 Exhaustive Matrix Tests with TP/SL)
**Master Account:** `ctmaster` (UID: `1060`, Account ID: `11060`)  
**Follower Accounts (5 Verified):**
- Follower 1: `ctf1` (UID: `1041`, Account ID: `11041`)
- Follower 2: `ctf2` (UID: `1043`, Account ID: `11043`)
- Follower 3: `ctf3` (UID: `1045`, Account ID: `11045`)
- Follower 4: `ctf4` (UID: `1048`, Account ID: `11048`)
- Follower 5: `ctf5` (UID: `1050`, Account ID: `11050`)

---

## 🏆 Complete 21-Scenario Execution Matrix (Multiplier, Balance, Equity with Mandatory TP/SL)

Every scenario explicitly placed orders with **Stop Loss (SL)** and **Take Profit (TP)** (or `slb`/`targetb` and `sls`/`targets`), asserting that the Master stored them and the Follower book received and replicated them identically.

| # | Copy Mode | Order Type | Side | Sub-Type | Master Parameters | Follower Lot Scaling | TP/SL Replicated | Status | Evidence File |
| :-: | :--- | :--- | :---: | :---: | :--- | :--- | :-: | :-: | :--- |
| **01** | Multiplier (3x) | **Market** | BUY | Direct Fill | 1.00 Lot, SL, TP | 3.00 Lots (3.0x) | ✅ Matched | **✅ PASS** | [`evidence_matrix_01`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_01_multiplier_market_buy_tpsl.md) |
| **02** | Multiplier (3x) | **Market** | SELL | Direct Fill | 1.00 Lot, SL, TP | 3.00 Lots (3.0x) | ✅ Matched | **✅ PASS** | [`evidence_matrix_02`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_02_multiplier_market_sell_tpsl.md) |
| **03** | Multiplier (3x) | **Limit** | BUY | Pending | 1.00 Lot, Trig, SL, TP | 3.00 Lots (3.0x Pending) | ✅ Matched | **✅ PASS** | [`evidence_matrix_03`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_03_multiplier_limit_buy_tpsl.md) |
| **04** | Multiplier (3x) | **Limit** | SELL | Pending | 1.00 Lot, Trig, SL, TP | 3.00 Lots (3.0x Pending) | ✅ Matched | **✅ PASS** | [`evidence_matrix_04`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_04_multiplier_limit_sell_tpsl.md) |
| **05** | Multiplier (3x) | **Stop HFT** | BUY | `type=1` (BUY) | 0.01 Lot, Trig, SL, TP | 0.03 Lots (3.0x Pending) | ✅ Matched | **✅ PASS** | [`evidence_matrix_05`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_05_multiplier_stop_hft_buy_tpsl.md) |
| **06** | Multiplier (3x) | **Stop HFT** | SELL | `type=0` (SELL) | 0.01 Lot, Trig, SL, TP | 0.03 Lots (3.0x Pending) | ✅ Matched | **✅ PASS** | [`evidence_matrix_06`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_06_multiplier_stop_hft_sell_tpsl.md) |
| **07** | Multiplier (3x) | **Stop HFT** | BOTH | `type=2` (BOTH) | Dual 0.01 Lot, Buy+Sell | Dual 0.03 Lots (3.0x) | ✅ Dual Matched | **✅ PASS** | [`evidence_matrix_07`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_07_multiplier_stop_hft_both_tpsl.md) |
| **08** | Balance-Based | **Market** | BUY | Direct Fill | 1.00 Lot, SL, TP | 0.11 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_08`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_08_balance_market_buy_tpsl.md) |
| **09** | Balance-Based | **Market** | SELL | Direct Fill | 1.00 Lot, SL, TP | 0.11 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_09`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_09_balance_market_sell_tpsl.md) |
| **10** | Balance-Based | **Limit** | BUY | Pending | 1.00 Lot, Trig, SL, TP | 0.11 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_10`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_10_balance_limit_buy_tpsl.md) |
| **11** | Balance-Based | **Limit** | SELL | Pending | 1.00 Lot, Trig, SL, TP | 0.11 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_11`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_11_balance_limit_sell_tpsl.md) |
| **12** | Balance-Based | **Stop HFT** | BUY | `type=1` (BUY) | 0.10 Lot, Trig, SL, TP | 0.01 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_12`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_12_balance_stop_hft_buy_tpsl.md) |
| **13** | Balance-Based | **Stop HFT** | SELL | `type=0` (SELL) | 0.10 Lot, Trig, SL, TP | 0.01 Lot (Balance Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_13`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_13_balance_stop_hft_sell_tpsl.md) |
| **14** | Balance-Based | **Stop HFT** | BOTH | `type=2` (BOTH) | Dual 0.10 Lot, Buy+Sell | Dual 0.01 Lot (Balance) | ✅ Dual Matched | **✅ PASS** | [`evidence_matrix_14`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_14_balance_stop_hft_both_tpsl.md) |
| **15** | Equity-Based | **Market** | BUY | Direct Fill | 1.00 Lot, SL, TP | 0.11 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_15`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_15_equity_market_buy_tpsl.md) |
| **16** | Equity-Based | **Market** | SELL | Direct Fill | 1.00 Lot, SL, TP | 0.11 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_16`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_16_equity_market_sell_tpsl.md) |
| **17** | Equity-Based | **Limit** | BUY | Pending | 1.00 Lot, Trig, SL, TP | 0.11 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_17`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_17_equity_limit_buy_tpsl.md) |
| **18** | Equity-Based | **Limit** | SELL | Pending | 1.00 Lot, Trig, SL, TP | 0.11 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_18`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_18_equity_limit_sell_tpsl.md) |
| **19** | Equity-Based | **Stop HFT** | BUY | `type=1` (BUY) | 0.10 Lot, Trig, SL, TP | 0.01 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_19`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_19_equity_stop_hft_buy_tpsl.md) |
| **20** | Equity-Based | **Stop HFT** | SELL | `type=0` (SELL) | 0.10 Lot, Trig, SL, TP | 0.01 Lot (Equity Ratio) | ✅ Matched | **✅ PASS** | [`evidence_matrix_20`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_20_equity_stop_hft_sell_tpsl.md) |
| **21** | Equity-Based | **Stop HFT** | BOTH | `type=2` (BOTH) | Dual 0.10 Lot, Buy+Sell | Dual 0.01 Lot (Equity) | ✅ Dual Matched | **✅ PASS** | [`evidence_matrix_21`](file:///c:/testing%20wavexone/reports/evidence/evidence_matrix_21_equity_stop_hft_both_tpsl.md) |

---

## 🏆 Core Copy Trading Suite Summary Matrix (15 Baseline Tests)

| # | Test Name | Target Module / Verification | Expected | Actual | Latency | Status | Evidence File |
| :-: | :--- | :--- | :--- | :--- | :-: | :---: | :--- |
| **00** | Phase 0 ID Validation | Live `accountList` API verification | Real IDs match `.env` | All 6 IDs match 100% | < 250ms | **✅ PASS** | Suite Setup |
| **01** | Multiplier Mode BUY | 1.00 Lot Master -> 3.00 Lots Follower | 3.00 lots on all 5 | 3.00 lots on 5/5 | 1.4s – 3.3s | **✅ PASS** | [`evidence_01`](file:///c:/testing%20wavexone/reports/evidence/evidence_01_multiplier_copy_trade.md) |
| **02** | Balance Mode & Rounding | Proportional lot & probe `round` vs `ceil` | `round(x, 2)` (0.11 & 0.10) | Matches `round(x, 2)` | ~1.6s | **✅ PASS** | [`evidence_02`](file:///c:/testing%20wavexone/reports/evidence/evidence_02_balance_based_copy_trade.md) |
| **03** | Equity Mode | Floating P&L divergence check ($\ge 0.01$ lot) | Lot diff $\ge 0.01$ step | Diff $< 0.01$ (equity $\approx$ bal) | N/A | **⚠️ INCONCLUSIVE** | [`evidence_03`](file:///c:/testing%20wavexone/reports/evidence/evidence_03_equity_based_copy_trade.md) |
| **04** | Unfollow / Re-follow | Unfollow stops copying, Re-follow resumes | Immediate stop & resume | Verified on ctf1 | ~1.5s | **✅ PASS** | [`evidence_04`](file:///c:/testing%20wavexone/reports/evidence/evidence_04_unfollow_refollow_lifecycle.md) |
| **05** | Dynamic Margin Audit | $\text{Margin} = \frac{\text{lot} \times \text{price}}{\text{leverage}}$, 3x ratio | Follower $\approx 3\times$ Master ($\pm 2\%$) | Margin: $481.62 vs $160.54 (3.0x) | N/A | **✅ PASS** | [`evidence_05`](file:///c:/testing%20wavexone/reports/evidence/evidence_05_balance_funds_dynamic_audit.md) |
| **06A** | Withdrawal Ratio Cap | `apiRedeemConfig` open orders ratio cap | Ratio drops from 1.0 to 0.8 | 0 open $\rightarrow 1.0$, open $\rightarrow 0.8$ | < 300ms | **✅ PASS** | [`evidence_06a`](file:///c:/testing%20wavexone/reports/evidence/evidence_06a_withdrawal_redeem_config.md) |
| **06B** | Gateway Rejection (KYC) | Reject excessive amount, abort if success | Over-limit rejected | Rejected ("Max withdraw 0.00") | < 250ms | **✅ PASS** | [`evidence_06b`](file:///c:/testing%20wavexone/reports/evidence/evidence_06b_withdrawal_gateway_rejection_kyc.md) |
| **07** | Unfollow with Open Position | Observe trade lifecycle on unfollow | Record observed behavior | Stayed open; closed with master | N/A | **⚠️ UNVERIFIED vs spec** | [`evidence_07`](file:///c:/testing%20wavexone/reports/evidence/evidence_07_unfollow_with_open_position.md) |
| **08** | Multiplier Mode SELL | 1.00 Lot SELL -> 3.00 Lots Follower | 3.00 lots on all 5 | 3.00 lots on 5/5 | 1.3s – 2.9s | **✅ PASS** | [`evidence_08`](file:///c:/testing%20wavexone/reports/evidence/evidence_08_sell_orders_replication.md) |
| **09** | 10-Order Batch Concurrency | 5 BUY, 5 SELL rapid batch execution | All 10 replicated to all 5 | 50/50 orders copied, 0 drops | 1.2s – 3.8s | **✅ PASS** | [`evidence_09`](file:///c:/testing%20wavexone/reports/evidence/evidence_09_ten_order_batch_concurrency.md) |
| **10** | TP/SL Propagation & Trigger | TP/SL values match, modify via `modify.php` | Propagation & SL auto-close | Auto-closed on tight SL hit | < 2.0s | **✅ PASS** | [`evidence_10`](file:///c:/testing%20wavexone/reports/evidence/evidence_10_tp_sl_propagation_and_trigger_hits.md) |
| **11** | Limit & Stop Orders | Pending limit replication & marketable fill | Pending replicates to followers | Pending replicated, fill copied | ~1.4s | **✅ PASS** | [`evidence_11`](file:///c:/testing%20wavexone/reports/evidence/evidence_11_limit_and_stop_hft_replication.md) |
| **12** | Reconciliation & Slippage | Symbol, side, lot match; slippage $\le 10$ pts | Zero mismatch, slippage $\le 10$ | Slippage: 5.4 – 5.6 pts | < 1.8s | **✅ PASS** | [`evidence_12`](file:///c:/testing%20wavexone/reports/evidence/evidence_12_reconciliation_and_slippage_audit.md) |
| **13** | Edge Cases & Safeguards | Partial close probe, pause/resume, ghosting | Zero ghost positions | Full close on partial; 0 ghosts | N/A | **✅ PASS** | [`evidence_13`](file:///c:/testing%20wavexone/reports/evidence/evidence_13_edge_cases_and_safeguards.md) |
| **14** | Final Settings Audit | Multiplier=3.0, Master=1060, 0 open orders | All 5 followers restored | 100% restored, 0 lingering | N/A | **✅ PASS** | [`evidence_14`](file:///c:/testing%20wavexone/reports/evidence/evidence_14_final_settings_audit.md) |

---

## 🔍 Key Findings Across All 21 Matrix Scenarios

1. **Stop HFT Dual Breakout (`stop_hft_type=2` - BOTH):**
   - When the Master places Stop HFT BOTH with BUY trigger/TP/SL and SELL trigger/TP/SL, the engine generates **dual pending orders** on the Master (`orderId: "id1,id2"`).
   - In Copy Trading, the fanout queue cleanly generates **dual pending orders on the Follower**, scaling the lot size per the active method (3.0x on Multiplier, balance ratio on Balance, equity ratio on Equity) and replicating individual TP/SL thresholds on both legs.
2. **TP/SL Propagation Across All Order Types:**
   - Both Market orders and pending Limit/Stop orders propagate the exact `sl` and `tp` values to follower orders upon placement.
   - The book API `/book/orders.php` stores both values in the `'sl'` and `'tp'` fields for all copied positions.
3. **Cancellation Behavior:**
   - Cancelling a pending Limit or Stop order on Master removes the Master order immediately. Replicated follower pending orders can be independently cancelled via `cancel.php?id={follower_order_id}` with instantaneous removal.
4. **Lot Scaling Consistency:**
   - **Multiplier Mode:** Master lot $L \rightarrow$ Follower lot $3.0 \times L$.
   - **Balance Mode:** Master lot $L \rightarrow$ Follower lot $L \times (\text{follower\_balance} / \text{master\_balance})$ rounded via `round(x, 2)`.
   - **Equity Mode:** Master lot $L \rightarrow$ Follower lot $L \times (\text{follower\_equity} / \text{master\_equity})$ rounded via `round(x, 2)`.

---

## 🔒 Security & Verification Audit
- **Zero Credentials Exposed:** All sensitive emails, passwords, and tokens are isolated in local `.env` (ignored by `.gitignore`).
- **Pristine State Restoration:** In `teardown_class`, all 5 follower accounts are restored to `multiplier = 3.0` following Master `1060`.
- **Zero Lingering Orders:** Master and all 5 follower accounts verified with **0 open orders** and **0 pending orders**.
