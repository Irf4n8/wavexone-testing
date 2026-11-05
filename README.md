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
│   ├── test_copy_trading.py       # Core Copy Trading suite (15 end-to-end tests: Phase 0, margin math, withdrawal safeguards, batch, slippage audit)
│   ├── test_copy_trading_matrix.py# Complete 21-scenario matrix suite (Multiplier, Balance, Equity x Market, Limit, Stop HFT Buy/Sell/Both with TP/SL)
│   ├── test_mam_trading.py        # MAM suite (Master -> 5 Followers with proportional share allocation)
│   └── test_pamm_trading.py       # PAMM suite (Master -> 5 Followers with pooled capital and ledger sync)
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
| | Followers (5) | `CT_FOLLOWER_1_EMAIL` .. `5` | `11041`, `11043`, `11045`, `11048`, `11050` | Multiplier (3x), Proportional Balance, Proportional Equity |
| **MAM** | Master | `MAM_MASTER_EMAIL` | `11056` (UID: 1056) | Master Order Placement |
| | Followers (5) | `MAM_FOLLOWER_1_EMAIL` .. `5` | `11058`, `11062`, `11064`, `11088`, `11066` | Proportional Lot Allocation (`mam_share = 50.00%`) |
| **PAMM** | Master | `PAMM_MASTER_EMAIL` | `11054` (UID: 1054) | Pooled Fund Execution |
| | Followers (5) | `PAMM_FOLLOWER_1_EMAIL` .. `5` | `11078`, `11080`, `11082`, `11084`, `11086` | Proportional Capital Allocation |

---

## Copy Trading 21-Scenario Complete Matrix Suite

The `TestCopyTradingMatrixSuite` in `tests/test_copy_trading_matrix.py` validates **every combination of Mode, Order Type, and Side with mandatory Take Profit (TP) and Stop Loss (SL) verification**:

1. **Multiplier Mode (3.0x Multiplier):**
   - Market BUY with TP/SL
   - Market SELL with TP/SL
   - Limit BUY with Trigger/TP/SL
   - Limit SELL with Trigger/TP/SL
   - Stop HFT BUY (`stop_hft_type=1`) with Trigger/TP/SL
   - Stop HFT SELL (`stop_hft_type=0`) with Trigger/TP/SL
   - Stop HFT BOTH (`stop_hft_type=2`, dual pending orders) with Trigger/TP/SL
2. **Balance-Based Proportional Mode:**
   - Market BUY with TP/SL
   - Market SELL with TP/SL
   - Limit BUY with Trigger/TP/SL
   - Limit SELL with Trigger/TP/SL
   - Stop HFT BUY with Trigger/TP/SL
   - Stop HFT SELL with Trigger/TP/SL
   - Stop HFT BOTH with Trigger/TP/SL
3. **Equity-Based Proportional Mode:**
   - Market BUY with TP/SL
   - Market SELL with TP/SL
   - Limit BUY with Trigger/TP/SL
   - Limit SELL with Trigger/TP/SL
   - Stop HFT BUY with Trigger/TP/SL
   - Stop HFT SELL with Trigger/TP/SL
   - Stop HFT BOTH with Trigger/TP/SL

---

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Copy Trading Matrix (21 Tests with TP/SL)
```bash
pytest tests/test_copy_trading_matrix.py -v
```

### 3. Run Core Copy Trading Suite (15 Tests)
```bash
pytest tests/test_copy_trading.py -v
```

---

## Reports & Telemetry
Individual JSON and Markdown evidence files are exported per test to:
- `reports/evidence/evidence_matrix_*.json`
- `reports/evidence/evidence_matrix_*.md`

Executive summaries and reconciliation reports:
- `reports/copy_trading_qa_report.md`
- `reports/copy_trading_qa_report.json`
