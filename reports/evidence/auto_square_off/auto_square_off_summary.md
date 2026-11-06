# WavexOne Staging - 100-Scenario Balance-Based Auto Square-Off Test Report

**Execution Date:** 2026-11-05 19:08:31
**Platform:** `https://stage.wavexone.com`
**Scope:** Copy Trading ONLY (MAM and PAMM excluded)

## 1. Executive Summary

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Scenarios** | 100 | 100% |
| **PASS** | 36 | 36.0% |
| **FAIL** | 12 | 12.0% |
| **INCONCLUSIVE** | 51 | 51.0% |
| **BLOCKED** | 1 | 1.0% |
| **Execution Duration** | 603.96s | - |

## 2. Discovery Section: Auto Square-Off Architecture

Per Section 3 discovery requirements:
1. **Configuration Endpoint:** No user-facing or API endpoints exist on Staging for setting a custom balance threshold. All candidate routes (`/user/risk.php`, `/user/auto_squareoff.php`, `/user/settings.php`, `/client-portal/apiAutoSquareOff`) return HTTP 404.
2. **Execution Endpoints:**
   - `/book/squareoff.php?id={id}&token={token}&fingerprint={fingerprint}` (Full Squareoff)
   - `/book/squareoff.php?id={id}&close_mode=partial&partial_lot={lot}` (Partial Squareoff)
   - `/book/cancel.php?id={id}` (Pending Order Cancellation)
   - `/trade/placeorder.php` with `sl` (Stop Loss) and `target` (Take Profit) for automatic price-hit auto-squareoff by the matching engine.
3. **Threshold Basis:** Price-based (CMP reaches SL or TP level) for orders; broker margin stop-out is based on margin level, but staging accounts have ~$12M to ~$111M balance.
4. **Trigger Evaluation:** Continuously on every live tick by the broker matching engine.
5. **Scope:** Master manual/auto square-off fans out to **all 5 followers** synchronously. Follower early close does not affect Master or peers.
6. **Pending Orders:** Cancelled via `/book/cancel.php`. Terminal and irreversible.

## 3. Results Breakdown by Category

| Category | Description | Total | PASS | FAIL | INCONCLUSIVE / BLOCKED |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Basic Balance Threshold Tests (BS01-BS10) | 10 | 0 | 0 | 10 |
| **B** | Balance Reduction Tests (BS11-BS20) | 10 | 6 | 0 | 4 |
| **C** | Balance vs Equity Tests (BS21-BS27) | 7 | 3 | 0 | 4 |
| **D** | Master Account Tests (BS28-BS35) | 8 | 4 | 0 | 4 |
| **E** | Follower Account Tests (BS36-BS45) | 10 | 3 | 1 | 6 |
| **F** | Position-Type Tests (BS46-BS56) | 11 | 6 | 4 | 1 |
| **G** | Order and Execution Tests (BS57-BS69) | 13 | 3 | 5 | 5 |
| **H** | Configuration and Validation Tests (BS70-BS80) | 11 | 0 | 0 | 11 |
| **I** | Recovery and Edge Cases (BS81-BS90) | 10 | 2 | 1 | 7 |
| **J** | Data Integrity and Audit Tests (BS91-BS100) | 10 | 9 | 1 | 0 |

## 4. Execution Latency Metrics

| Operation | Min Latency | Avg Latency | Max Latency |
| :--- | :--- | :--- | :--- |
| **Passed Operations** | 0.00s | 3.12s | 21.84s |

## 5. Account Teardown Audit

- **Master Account (11060):** 0 open orders, 0 pending orders verified.
- **Followers 1 - 5 (11041, 11043, 11045, 11048, 11050):** 0 open orders, 0 pending orders verified.
- **Follower Configurations:** All 5 restored to multiplier `3.0` following Master `1060`.
