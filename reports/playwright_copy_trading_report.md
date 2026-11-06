# WavexOne Copy Trading: Playwright Browser Automation Test Report

**Execution Date:** 2026-11-06  
**Environment:** Staging (`https://stage.wavexone.com`)  
**Browser Engine:** Chromium (Playwright Browser Contexts)  
**Execution Tool:** `pytest tests/test_copy_trading_playwright.py -v -s`  
**Overall Status:** **100% PASS (4 Passed / 0 Failed)**  
**Execution Duration:** 71.87 seconds  

---

## 1. Executive Summary

As requested by engineering leadership (**"use playwright"**), an end-to-end browser automation suite was implemented and executed using Playwright. This suite validates full UI authentication, account badge binding, dynamic copy configuration switching, real-time position replication, and full square-off cleanup across isolated browser contexts for the Master Trader (`ctmaster` / `11060`) and Follower Accounts (`ctf1` / `11041`).

All scenarios were executed with a strict Master lot size of **0.50** (per instructions).

| Scenario ID | Test Name | Copy Method | Master Lot | Expected Follower Lot | Observed UI Value | UI Status | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PW-ACC-01** | Multi-Account UI Login & Badge Validation | N/A | N/A | N/A | Master: `11060`<br>Follower: `11041` | Verified in DOM | **PASS** |
| **PW-MUL-01** | Multiplier Mode UI Replication (3.0x) | `multiplier` (3.0x) | 0.50 | 1.50 | `1.50` lots (Order #74604) | Live DOM Table | **PASS** |
| **PW-BAL-01** | Balance-Based Copy Trading UI Replication | `balance` | 0.50 | 0.05 | `0.05` lots (Order #74610) | Live UI Toast | **PASS** |
| **PW-EQU-01** | Equity-Based Copy Trading UI Replication | `equity` | 0.50 | 0.05 | `0.05` lots (Order #74616) | Live UI Toast | **PASS** |

---

## 2. Test Execution Details

### 2.1 PW-ACC-01: Multi-Account UI Login & Staging Account ID Badge Validation
- **Objective:** Ensure Master and Follower sessions can concurrently authenticate to the Web UI in isolated browser contexts without cross-session contamination or credential pollution.
- **Master UI:**
  - Login URL: `https://stage.wavexone.com/login/`
  - User: `ctmaster@mailinator.com` (UID: `1060`)
  - Target Account Badge: `#xnAccountCurrent` -> `11060` (Verified attached & rendered).
  - Screenshot: `reports/screenshots/pw_master_login_11060.png`
- **Follower UI:**
  - Login URL: `https://stage.wavexone.com/login/`
  - User: `ctf1@mailinator.com` (UID: `1041`)
  - Target Account Badge: `#xnAccountCurrent` -> `11041` (Verified attached & rendered).
  - Screenshot: `reports/screenshots/pw_follower_login_11041.png`

### 2.2 PW-MUL-01: Multiplier 3.0x Proportional UI Replication
- **Objective:** Verify that placing a 0.50 lot BUY order on Master dynamically generates a 1.50 lot position on the Follower's browser window.
- **Master Placement:** BUY `0.50` lot on `X:BTCUSD` (Order `#74599`).
- **Follower Replication:**
  - Method: `multiplier` (3.0x)
  - Formula: $\text{Lot}_{\text{follower}} = 0.50 \times 3.0 = 1.50$
  - Observed UI Notification / Table Row: `#74604 · BTCUSD · BUY · 1.5 lots @ 75377.20`
  - Position Closure: Master square-off cleared positions on both accounts to 0.
  - Screenshots:
    - Master Open Position: `reports/screenshots/pw_mul_master_open_position.png`
    - Follower Replicated Position: `reports/screenshots/pw_mul_follower_replicated_position.png`
    - Follower Cleared State: `reports/screenshots/pw_mul_follower_cleared.png`

### 2.3 PW-BAL-01: Balance-Based Copy Trading UI Replication
- **Objective:** Dynamically switch copy mode to `balance` and verify dynamic sizing based on balance ratios.
- **Ratio Calculation:**
  $$\text{Ratio} = \frac{\text{Follower Balance}}{\text{Master Balance}} = \frac{\$10,000.00}{\$100,000.00} = 0.10$$
  $$\text{Follower Lot} = 0.50 \times 0.10 = 0.05 \text{ lots}$$
- **Execution & UI Verification:**
  - Method: `balance`
  - Master Order: BUY `0.50` lot on `X:BTCUSD`.
  - Follower UI Captured Toast: `#74610 · BTCUSD · BUY · 0.05 lots @ 75358.99`
  - Screenshot Evidence: `reports/screenshots/pw_bal_follower_replicated_005_lot.png`
  - Cleared State: `reports/screenshots/pw_bal_follower_cleared.png`

### 2.4 PW-EQU-01: Equity-Based Copy Trading UI Replication
- **Objective:** Dynamically switch copy mode to `equity` and verify dynamic sizing based on equity ratios.
- **Ratio Calculation:**
  $$\text{Ratio} = \frac{\text{Follower Equity}}{\text{Master Equity}} = \frac{\$10,000.00}{\$100,000.00} = 0.10$$
  $$\text{Follower Lot} = 0.50 \times 0.10 = 0.05 \text{ lots}$$
- **Execution & UI Verification:**
  - Method: `equity`
  - Master Order: BUY `0.50` lot on `X:BTCUSD`.
  - Follower UI Captured Toast: `#74616 · BTCUSD · BUY · 0.05 lots @ 75384.13`
  - Screenshot Evidence: `reports/screenshots/pw_equ_follower_replicated_005_lot.png`
  - Cleared State: `reports/screenshots/pw_equ_follower_cleared.png`

---

## 3. Playwright Architecture & Implementation Artifacts

1. **Page Object Model (`core/playwright/wavex_page.py`):**
   - Encapsulates multi-session browser contexts with isolated cookies, local storage, and rendering viewports.
   - Implements robust DOM polling handling both instantaneous toast banners (`.toast-message`) and dynamic open positions tables (`table.openpending`).
   - Filters out stale DOM nodes, cancelled orders, and closed trades to ensure zero false positives.
2. **Deterministic Teardown & Baseline Recovery (`core/copy_trading/safe_teardown.py`):**
   - Automatically cancels pending orders and squares off active positions across all 6 staging accounts after each scenario.
   - Restores all follower copy modes back to baseline (`multiplier` 3.0x).
3. **Screenshot Repository (`reports/screenshots/`):**
   - Stores visual proof of each step for QA audit and management review.

