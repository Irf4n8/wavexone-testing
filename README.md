# 🌐 WavexOne Social Trading Automated QA Framework
### Enterprise Multi-Account Automation: Copy Trading, MAM, and PAMM

This repository provides an automated testing framework dedicated to **WavexOne** (`https://stage.wavexone.com`). It covers end-to-end verification of social trading workflows across 18 accounts:
- **Copy Trading**: Master (`ctmaster`) and 5 Followers (`ctf1` – `ctf5`) with custom lot multipliers.
- **MAM (Multi-Account Manager)**: Master (`mammaster`) and 5 Followers (`mamf1` – `mamf5`) with percentage lot allocation.
- **PAMM (Percent Allocation Management Module)**: Master (`pammmaster`) and 5 Followers (`pammf1` – `pammf5`) with pooled capital and proportional PnL distribution.

---

## 📁 Repository Structure

```text
├── config/
│   ├── __init__.py
│   ├── settings.py         # Endpoints, credentials, account mappings, and matrix constraints
│   └── symbols.py          # Tested symbols catalog (Forex, Commodities, Crypto) and 10-order plan
├── core/
│   ├── __init__.py
│   ├── client.py           # WavexOne REST API Session client (Auth, Orders, Fingerprint, Squareoff)
│   ├── logger.py           # Formatted colorized console & file logging
│   └── reporter.py         # Structured Markdown and JSON report generator
├── tests/
│   ├── __init__.py
│   ├── test_copy_trading.py# Copy Trading suite (Master -> 5 Followers with 3x multiplier)
│   ├── test_mam_trading.py # MAM suite (Master -> 5 Followers with proportional share allocation)
│   └── test_pamm_trading.py# PAMM suite (Master -> 5 Followers with pooled capital and ledger sync)
├── reports/
│   ├── social_trading_qa_report.json # Telemetry, order IDs, latencies, sync metrics
│   └── social_trading_qa_report.md   # Human-readable markdown audit report
├── logs/
│   └── wavexone_qa.log     # Detailed runtime execution logs
├── run_qa_suite.py         # Unified test runner (30 orders total: 10 CT, 10 MAM, 10 PAMM)
├── conftest.py             # Pytest fixtures and hooks
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Pinned dependencies
├── .gitignore              # Clean gitignore configuration
└── README.md               # Framework documentation and run instructions
```

---

## 👥 Test Accounts Architecture & Security

All account credentials (usernames, emails, passwords, tokens) are strictly isolated in a local `.env` file that is excluded from version control (`.gitignore`). 

To configure test accounts, copy `.env.example` to `.env` and fill in your staging credentials:
```bash
cp .env.example .env
```

| Module | Role | Identifier Key in `.env` | Verified Account ID | Configured Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Copy Trading** | Master | `CT_MASTER_EMAIL` | `11060` (UID: 1060) | Master Order Placement (1.00 Lot) |
| | Followers (5) | `CT_FOLLOWER_1_EMAIL` .. `5` | `11041` – `11050` | Multiplier (3x), Proportional Balance, Proportional Equity |
| **MAM** | Master | `MAM_MASTER_EMAIL` | `11056` (UID: 1056) | Master Order Placement |
| | Followers (5) | `MAM_FOLLOWER_1_EMAIL` .. `5` | `11058` – `11088` | Proportional Lot Allocation (`mam_share = 50.00%`) |
| **PAMM** | Master | `PAMM_MASTER_EMAIL` | `11054` (UID: 1054) | Pooled Fund Execution ($5,000,000 pool) |
| | Followers (5) | `PAMM_FOLLOWER_1_EMAIL` .. `5` | `11078` – `11086` | Proportional Capital Allocation ($1,000,000 each) |

---

## 🧪 Test Execution Constraints & Scope

- **Order Count Policy:** The suite places **exactly 30 orders** (strictly within the specified constraint of **20 to 50 orders**):
  - **10 Orders on Copy Trading** (`ctmaster`): 5 Market BUYs and 5 Market SELLs across `C:EURUSD`, `C:GBPUSD`, `C:USDJPY`, `C:XAUUSD`, `X:BTCUSD`.
  - **10 Orders on MAM** (`mammaster`): 5 Market BUYs and 5 Market SELLs.
  - **10 Orders on PAMM** (`pammmaster`): 5 Market BUYs and 5 Market SELLs.
- **Verification Assertions:**
  - **Copy Trading:** Asserts that after master places `lot`, each follower receives an order with lot = `lot * 3.0`, and that master squareoff simultaneously closes all 5 follower positions.
  - **MAM:** Asserts that after master places `lot`, each follower receives an allocated position based on their MAM share, and that master squareoff simultaneously closes all 5 follower positions.
  - **PAMM:** Asserts that master orders execute in the pooled fund without polluting individual follower books, and that squareoff triggers proportional PnL and ledger distribution.

---

## ⚡ How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Unified Test Suite (30 Orders)
```bash
python run_qa_suite.py
```

### 3. Run via Pytest
```bash
# Run all suites with verbose output
pytest

# Run Copy Trading suite only
pytest tests/test_copy_trading.py

# Run MAM suite only
pytest tests/test_mam_trading.py

# Run PAMM suite only
pytest tests/test_pamm_trading.py
```

---

## 📈 Reports & Telemetry
After running `run_qa_suite.py`, comprehensive reports are generated:
- `reports/social_trading_qa_report.md`
- `reports/social_trading_qa_report.json`
- `logs/wavexone_qa.log`

