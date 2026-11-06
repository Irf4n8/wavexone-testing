# WavexOne Staging - Auto Square-Off Bug Report

**Date:** 2026-11-05 19:08:31
**Environment:** Staging (`https://stage.wavexone.com`)

## 1. Discovered Architectural Bugs & API Discrepancies

### [ARCH-01] Missing Balance-Based Auto Square-Off Configuration Endpoint
- **Scenario IDs:** BS01-BS10, BS70-BS80
- **Description:** The platform has no endpoint or UI panel to configure account-level or copy-trading balance thresholds. Probed `/user/risk.php`, `/user/auto_squareoff.php`, `/user/settings.php`, `/client-portal/apiAutoSquareOff` all return HTTP 404.
- **Impact:** Dependent threshold-based square-off scenarios cannot be triggered via platform configuration; marked INCONCLUSIVE per instructions.

### [BUG-01] Staging Orders API Returns Static Equity Equal to Balance
- **Scenario IDs:** BS21-BS27
- **Description:** `/book/balance.php` statically returns `'equity' == 'balance'` regardless of active floating P&L during live market positions.
- **Impact:** Prevents floating equity from diverging from balance until positions are closed and realized.

## 2. Assertion Failures & Functional Failures

### [BUG-BS48] Assertion Failure in BS48: BUY and SELL positions open simultaneously
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS49] Assertion Failure in BS49: Multiple symbols are open
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS52] Assertion Failure in BS52: Position has TP configured
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS54] Assertion Failure in BS54: Position has both TP and SL
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS58] Assertion Failure in BS58: Pending SELL limit order exists
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS59] Assertion Failure in BS59: Pending BUY stop order exists
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS60] Assertion Failure in BS60: Pending SELL stop order exists
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS66] Assertion Failure in BS66: Multiple positions close simultaneously
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS86] Assertion Failure in BS86: Account has no trading activity
- **Expected:** Assertion to pass per business specification
- **Actual:** 
- **Severity:** HIGH

### [BUG-BS93] Assertion Failure in BS93: Verify used margin after square-off
- **Expected:** Assertion to pass per business specification
- **Actual:** Expected 0 open orders after squareoff
- **Severity:** HIGH

