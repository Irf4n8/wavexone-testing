# WavexOne Social Trading Automated QA Framework
### Enterprise Multi-Account Automation: Copy Trading, MAM, and PAMM

This repository provides an automated testing framework dedicated to **WavexOne** (`https://stage.wavexone.com`). It covers end-to-end verification of social trading workflows across 18 accounts:
- **Copy Trading**: Master (`ctmaster`) and 5 Followers (`ctf1` – `ctf5`) with custom lot multipliers.
- **MAM (Multi-Account Manager)**: Master (`mammaster`) and 5 Followers (`mamf1` – `mamf5`) with percentage lot allocation.
- **PAMM (Percent Allocation Management Module)**: Master (`pammmaster`) and 5 Followers (`pammf1` – `pammf5`) with pooled capital and proportional PnL distribution.

---

## Repository Structure

```text
├── config/
│   ├── __init__.py
│   ├── settings.py         # Endpoints, credentials, account mappings, and matrix constraints
│   └── symbols.py          # Tested symbols catalog (Forex, Commodities, Crypto) and 10-order plan
├── core/
│   ├── __init__.py
│   ├── client.py           # WavexOne REST API Session client (Auth, Orders, Fingerprint, Squareoff)
│   ├── evidence.py         # Per-test Markdown & JSON evidence generator
│   ├── logger.py           # Formatted colorized console & file logging
│   └── reporter.py         # Structured Markdown and JSON report generator
├── tests/
│   ├── __init__.py
│   ├── test_copy_trading.py# Copy Trading suite (15 end-to-end tests: Phase 0, multiplier, balance, margin, withdrawal, TP/SL, limits, etc.)
│   ├── test_mam_trading.py # MAM suite (Master -> 5 Followers with proportional share allocation)
│   └── test_pamm_trading.py# PAMM suite (Master -> 5 Followers with pooled capital and ledger sync)
├── reports/
│   ├── copy_trading_qa_report.md   # Comprehensive Copy Trading audit report
│   ├── copy_trading_qa_report.json # Telemetry, order IDs, latencies, sync metrics
│   └── evidence/                   # Separate JSON and MD evidence files per test
├── logs/
│   └── wavexone_qa.log     # Detailed runtime execution logs
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Pinned dependencies
├── .gitignore              # Clean gitignore configuration (ignoring .env and secrets)
└── README.md               # Framework documentation and run instructions
```

---

## Test Accounts Architecture & Security

All account credentials (usernames, emails, passwords, tokens) are strictly isolated in a local `.env` file that is excluded from version control (`.gitignore`).

To configure test accounts, copy `.env.example` to `.env` and fill in your staging credentials:
```bash
cp .env.example .env
```

| Module | Role | Identifier Key in `.env` | Verified Account ID | Configured Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Copy Trading** | Master | `CT_MASTER_EMAIL` | `11060` (UID: 1060) | Master Order Placement (1.00 Lot) |
| | Followers (5) | `CT_FOLLOWER_1_EMAIL` .. `5` | `11061`, `11063`, `11065`, `11089`, `11067` | Multiplier (3x), Proportional Balance, Proportional Equity |
| **MAM** | Master | `MAM_MASTER_EMAIL` | `11056` (UID: 1056) | Master Order Placement |
| | Followers (5) | `MAM_FOLLOWER_1_EMAIL` .. `5` | `11058`, `11062`, `11064`, `11088`, `11066` | Proportional Lot Allocation (`mam_share = 50.00%`) |
| **PAMM** | Master | `PAMM_MASTER_EMAIL` | `11054` (UID: 1054) | Pooled Fund Execution |
| | Followers (5) | `PAMM_FOLLOWER_1_EMAIL` .. `5` | `11078`, `11080`, `11082`, `11084`, `11086` | Proportional Capital Allocation |

---

## Copy Trading Test Suite Scope & Coverage

The `TestCopyTradingSuite` in `tests/test_copy_trading.py` executes 15 distinct verification routines:

1. **Phase 0 Runtime Account Verification:** Validates live account IDs against expected IDs from `.env`/config.
2. **Test 1: Multiplier Mode BUY:** Master 1.00 lot BUY BTCUSD replicates as 3.00 lots to all 5 followers; simultaneous clean squareoff.
3. **Test 2: Balance-Based Mode & Rounding Probe:** Follower 1 switches to balance proportional copying. Includes two mathematical probes (`0.11009` and `0.10459`) to verify the engine uses standard `round(x, 2)`.
4. **Test 3: Equity Mode & Floating P&L Guard:** Large master position generates floating P&L. Computes expected lot from live equity vs balance. If equity equals balance, marks test `INCONCLUSIVE` per specification.
5. **Test 4: Unfollow & Re-Follow Lifecycle:** Verifies unfollow halts replication to that follower while peers continue copying, and re-follow restores replication.
6. **Test 5: Dynamic Margin Verification:** Formula $\text{Margin} = \frac{\text{lot} \times \text{price}}{\text{leverage}}$ verified within 2% tolerance; follower margin verified at ~3x master margin; 100% margin release verified after squareoff.
7. **Test 6A: Withdrawal Ratio Safeguard:** Verifies `apiRedeemConfig` dynamically caps withdrawable ratio to 0.8 with open orders, restoring to 1.0 upon closure.
8. **Test 6B: Gateway Rejection Safeguard:** Tests excessive withdrawal OTP rejection tagged with KYC verification status. Critical safety guard aborts immediately if gateway returns success.
9. **Test 7: Unfollow While Position is Open:** Observes platform behavior when a follower unfollows master during an active position (stayed open, closed with master; tagged `UNVERIFIED vs spec`).
10. **Test 8: Multiplier Mode SELL:** Master 1.00 lot SELL BTCUSD replicates as 3.00 lots across all 5 followers.
11. **Test 9: 10-Order Batch Concurrency:** Rapid batch execution of 5 BUY and 5 SELL orders (50 replicated orders across 5 followers) with zero drops and bulk squareoff.
12. **Test 10: TP/SL Propagation & Trigger Hits:** Verifies TP/SL propagation to followers, modification via `modify.php` (`name=StopLoss` and `name=Target`), and auto-execution on SL hit.
13. **Test 11: Limit & Stop Orders:** Pending limit replication, cancellation propagation, and marketable limit fill replication.
14. **Test 12: Order Reconciliation & Slippage Audit:** Compares price, side, symbol, and lot across master vs followers; measures slippage against configured tolerance.
15. **Test 13: Edge Cases & Safeguards:** Partial close probe (`squareoff.php?lot=0.50`), follower pause/resume, and ghost position prevention.
16. **Test 14: Final Settings Restoration Audit:** Confirms all 5 followers are restored to `multiplier = 3.0` following Master `1060`, and zero lingering open orders exist across all accounts.

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Copy Trading Test Suite
```bash
pytest tests/test_copy_trading.py -v
```

---

## Reports & Telemetry
Individual JSON and Markdown evidence files are exported per test to:
- `reports/evidence/evidence_*.json`
- `reports/evidence/evidence_*.md`

Executive summaries and reconciliation reports:
- `reports/copy_trading_qa_report.md`
- `reports/copy_trading_qa_report.json`
