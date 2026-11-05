# 🚀 WavexOne Social Trading QA Automation Report

**Environment:** https://stage.wavexone.com  
**Total Orders Placed on Master Accounts:** 26 (Order Constraint: **20 to 50 orders**)  
**Overall Pass Rate:** **100.0%**  
**Total Accounts Tested:** 18 (3 Masters, 15 Followers)  

---

## 📊 Executive Summary Matrix

| Social Trading Module | Master Account | Orders Placed | Passed Checks | Failed Checks | Follower Fanout / Allocation | Result |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Copy Trading** | ctmaster@mailinator.com | 10 | 10 | 0 | 50/50 Copied (3x multiplier verified & closed) | **✅ PASS** |
| **MAM Trading** | mammaster@mailinator.com | 10 | 10 | 0 | 50/50 Allocated (50% share verified & closed) | **✅ PASS** |
| **PAMM Trading** | pammmaster@mailinator.com | 6 | 6 | 0 | 100% Pooled Fund Execution & Clean Books | **✅ PASS** |
| **TOTAL** | **3 Masters** | **26** | **26** | **0** | **100% Sync Across All 15 Followers** | **✅ PASS** |

---

## 1. 📈 Copy Trading Module Results
- **Master Account:** ctmaster@mailinator.com (UID: 1060, Account: 11060)
- **Follower Accounts (5):** ctf1 to ctf5 (ctf1@mailinator.com - ctf5@mailinator.com)
- **Configuration:** Multiplier = 3x, Profit Share = 10%
- **Verification:** For every master order of lot L, each follower receives an order with lot 3.0 * L. Master squareoff triggers simultaneous close on all 5 followers.

| # | Symbol | Type | Side | Master Lot | Master Order ID | Followers Synced | Sync Status | Squareoff Status |
| :-: | :--- | :---: | :---: | :-: | :-: | :-: | :-: | :-: |
| 1 | C:EURUSD | MARKET | BUY | 0.01 | 52590 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 2 | C:GBPUSD | MARKET | BUY | 0.01 | 52596 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 3 | C:USDJPY | MARKET | BUY | 0.01 | 52602 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 4 | C:XAUUSD | MARKET | BUY | 0.01 | 52608 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 5 | X:BTCUSD | MARKET | BUY | 0.01 | 52614 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 6 | C:EURUSD | MARKET | SELL | 0.01 | 52620 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 7 | C:GBPUSD | MARKET | SELL | 0.01 | 52626 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 8 | C:USDJPY | MARKET | SELL | 0.01 | 52632 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 9 | C:XAUUSD | MARKET | SELL | 0.01 | 52638 | 5/5 | ✅ 3x Copied | ✅ CLOSED |
| 10 | X:BTCUSD | MARKET | SELL | 0.01 | 52644 | 5/5 | ✅ 3x Copied | ✅ CLOSED |

---

## 2. 👥 MAM (Multi-Account Manager) Module Results
- **Master Account:** mammaster@mailinator.com (UID: 1056, Account: 11056)
- **Follower Accounts (5):** mamf1 to mamf5 (mamf1@mailinator.com - mamf5@mailinator.com)
- **Configuration:** MAM Share = 50.00%
- **Verification:** Master orders distribute allocated lots to each follower according to MAM share. Master squareoff triggers instantaneous closing across all 5 followers.

| # | Symbol | Type | Side | Master Lot | Master Order ID | Followers Synced | Sync Status | Squareoff Status |
| :-: | :--- | :---: | :---: | :-: | :-: | :-: | :-: | :-: |
| 1 | C:EURUSD | MARKET | BUY | 0.02 | 52650 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 2 | C:GBPUSD | MARKET | BUY | 0.02 | 52656 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 3 | C:USDJPY | MARKET | BUY | 0.02 | 52662 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 4 | C:XAUUSD | MARKET | BUY | 0.02 | 52668 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 5 | X:BTCUSD | MARKET | BUY | 0.02 | 52674 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 6 | C:EURUSD | MARKET | SELL | 0.02 | 52680 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 7 | C:GBPUSD | MARKET | SELL | 0.02 | 52686 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 8 | C:USDJPY | MARKET | SELL | 0.02 | 52692 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 9 | C:XAUUSD | MARKET | SELL | 0.02 | 52698 | 5/5 | ✅ Allocated | ✅ CLOSED |
| 10 | X:BTCUSD | MARKET | SELL | 0.02 | 52704 | 5/5 | ✅ Allocated | ✅ CLOSED |

---

## 3. 💼 PAMM (Percent Allocation Management Module) Results
- **Master Account:** pammmaster@mailinator.com (UID: 1054, Account: 11054)
- **Follower Accounts (5):** pammf1 to pammf5 (,000,000 investment each into ,000,000 pooled fund)
- **Verification:** Orders execute strictly at the pooled master level; follower open books remain clean with 0 individual order pollution. Proportional PnL distributes into investment ledger upon closing.

| # | Symbol | Type | Side | Master Lot | Master Order ID | Clean Books | Sync Status | Squareoff Status |
| :-: | :--- | :---: | :---: | :-: | :-: | :-: | :-: | :-: |
| 1 | C:EURUSD | MARKET | BUY | 0.01 | 52710 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |
| 2 | C:GBPUSD | MARKET | BUY | 0.01 | 52711 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |
| 3 | C:USDJPY | MARKET | BUY | 0.01 | 52712 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |
| 4 | C:XAUUSD | MARKET | BUY | 0.01 | 52713 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |
| 5 | X:BTCUSD | MARKET | BUY | 0.01 | 52714 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |
| 6 | C:EURUSD | MARKET | SELL | 0.01 | 52715 | 5/5 Verified | ✅ Pooled OK | ✅ CLOSED |

---

## 🛡️ Live Account Book Reconciliation
A post-test verification across all 18 accounts confirmed that **every account has 0 lingering open orders**:
- ctmaster + ctf1 – ctf5: 0 Open Orders
- mammaster + mamf1 – mamf5: 0 Open Orders
- pammmaster + pammf1 – pammf5: 0 Open Orders