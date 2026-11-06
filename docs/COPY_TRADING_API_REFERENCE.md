# WavexOne Copy Trading: Complete API Reference & Endpoint Mapping

**Document Version:** 1.0.0  
**Environment:** WavexOne Staging (`https://stage.wavexone.com`)  
**Scope:** Strict Copy Trading REST APIs & Request/Response Contracts  
**Author:** Senior QA Automation Architect (Financial Trading & Brokerage Platforms)

---

## 1. Authentication & Session Prerequisite APIs

### 1.1 Login & Token Generation
- **Frontend Action:** User logs in via `/login/` web page or Client Portal sign-in.
- **Backend Endpoint:** `/login/check.php`
- **HTTP Method:** `POST`
- **Headers:** `Content-Type: application/x-www-form-urlencoded`
- **Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `email` | string | Yes | Registered user email (e.g. `ctmaster@mailinator.com`) |
  | `password` | string | Yes | User password |
- **Database Tables Involved:** `users`, `user_auth_tokens`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Login successful",
    "token": "UHZIKS5BXD",
    "userID": "1060"
  }
  ```
- **Failure Scenarios:**
  - `401 Unauthorized` / `{"status": "fail", "message": "Invalid credentials"}`

---

### 1.2 Trading Account Resolution
- **Frontend Action:** Dashboard boots and fetches trading accounts assigned to this user.
- **Backend Endpoint:** `/dashboard/api/accountList.php`
- **HTTP Method:** `GET`
- **Parameters:** `token` (string, required)
- **Database Tables Involved:** `trading_accounts`
- **Expected Success Response:**
  ```json
  [
    {
      "account_id": "11060",
      "user_id": "1060",
      "book": "a",
      "leverage": "500",
      "status": "active"
    }
  ]
  ```

---

### 1.3 Cryptographic Session Fingerprint
- **Frontend Action:** Required before any trading action (anti-replay/session binding).
- **Backend Endpoint:** `/dashboard/api/create_fingerprint.php`
- **HTTP Method:** `GET`
- **Parameters:** `token` (string, required)
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "fingerprint": "060d191b0e0707726a777e74726273641f45415621_1594"
  }
  ```

---

## 2. Copy Trading Subscription Management APIs

### 2.1 Follow Manager / Subscribe
- **Frontend Action:** Follower clicks "Confirm Follow" in Client Portal modal.
- **Backend Endpoint:** `/user/follow.php`
- **HTTP Method:** `POST` or `GET`
- **Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `token` | string | Yes | Follower authentication token |
  | `follow` | string/int | Yes | Master UID (`1060`) |
  | `type` | string | Yes | `"follow"` |
  | `method` | string | Yes | `"multiplier"`, `"balance"`, or `"equity"` |
  | `value` | string | Conditional | Numeric multiplier string (e.g. `"3.0"`). Required if method is multiplier. |
- **Database Tables Involved:** `copy_trading_subscriptions`, `users`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Manager followed successfully"
  }
  ```

---

### 2.2 Unfollow Manager / Terminate Subscription
- **Frontend Action:** Follower clicks "Unfollow" button in Client Portal.
- **Backend Endpoint:** `/user/follow.php`
- **HTTP Method:** `POST` or `GET`
- **Parameters:** `token`, `follow=1060`, `type=unfollow`
- **Database Tables Involved:** `copy_trading_subscriptions`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Manager unfollowed successfully"
  }
  ```
- **Observed Platform Bug:** If follower has an open position when unfollowing, subsequent Master square-offs still close the follower's position erroneously ([BUG-02]).

---

### 2.3 Update Copy Trading Method
- **Frontend Action:** Follower edits active copy settings (e.g. changing from multiplier to balance mode).
- **Backend Endpoint:** `/user/updateCopyTradingMethod.php`
- **HTTP Method:** `GET`
- **Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `token` | string | Yes | Follower authentication token |
  | `uid` | string | Yes | Unique subscription record UID (e.g. `"3355549"`) |
  | `method` | string | Yes | `"multiplier"`, `"balance"`, or `"equity"` |
  | `value` | string | Optional | `"3.0"` if multiplier; empty string if balance or equity |
- **Database Tables Involved:** `copy_trading_subscriptions`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Copy Trading Method Updated"
  }
  ```

---

### 2.4 Query Follower Subscriptions List
- **Frontend Action:** Client Portal loads "My Subscriptions" table.
- **Backend Endpoint:** `/user/userCopyFollowers.php`
- **HTTP Method:** `GET`
- **Parameters:** `token` (string, required)
- **Database Tables Involved:** `copy_trading_subscriptions`, `users`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "data": {
      "copyTradingList": "[{\"manager_id\":\"1060\",\"name\":\"ctmaster\",\"account_id\":\"11060\",\"trade_method\":\"multiplier\",\"multiplier_value\":\"3.0\",\"uid\":\"3355549\"}]"
    }
  }
  ```

---

## 3. Order Execution & Matching Engine APIs

### 3.1 Place Order (Market / Limit / Stop)
- **Frontend Action:** Master clicks BUY / SELL / Limit / Stop order buttons in Web Trader.
- **Backend Endpoint:** `/trade/placeorder.php`
- **HTTP Method:** `GET` (Platform query-string contract)
- **Parameters:**
  | Parameter | Type | Required | Description |
  | :--- | :--- | :--- | :--- |
  | `token` | string | Yes | Master auth token |
  | `symbol` | string | Yes | Instrument code (e.g. `X:BTCUSD`) |
  | `type` | string | Yes | `market`, `limit`, or `stop` |
  | `bs` | string | Yes | `buy` or `sell` (Must be `buy` for `stop_hft_type=2`) |
  | `lot` | float/string | Yes | Order lot size (Strictly `1.00`) |
  | `sl` | string | Optional | Stop Loss target price |
  | `target` | string | Optional | Take Profit target price |
  | `trigger` | string | Conditional | Trigger price for Limit or single Stop order |
  | `stop_hft_type` | string | Conditional | `"1"` (Stop BUY), `"0"` (Stop SELL), `"2"` (Stop BOTH) |
  | `lotb`, `slb`, `targetb`, `triggerb` | string | Conditional | Stop BOTH buy-bracket parameters |
  | `lots`, `sls`, `targets`, `triggers` | string | Conditional | Stop BOTH sell-bracket parameters |
  | `fingerprint` | string | Yes | Cryptographic session fingerprint |
  | `clicked` | string | Yes | `"yes"` (UI trigger confirmation flag) |
- **Database Tables Involved:** `active_orders`, `order_intents`, `fanout_queue`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Order accepted for processing",
    "data": {
      "orderId": "64067",
      "intentId": "7e4f57f44f8aba8117c84cb59bdeb86a",
      "executionStatus": "queued",
      "fanoutJobId": 7352,
      "fanoutStatus": "queued"
    }
  }
  ```

---

### 3.2 Query Live Order Book & Positions
- **Frontend Action:** Continuous DOM refresh polling every 500ms–1.0s.
- **Backend Endpoint:** `/book/orders.php`
- **HTTP Method:** `GET`
- **Parameters:** `token` (string, required)
- **Database Tables Involved:** `active_orders`
- **Expected Success Response:**
  ```json
  [
    {
      "id": "64067",
      "symbol": "X:BTCUSD",
      "formated_symbol": "BTCUSD",
      "type": "market",
      "bs": "BUY",
      "lot": "1",
      "sl": "75520.00",
      "tp": "75550.00",
      "avg": "75533.10",
      "status": "open",
      "time": "2026-11-06 04:32:03"
    }
  ]
  ```

---

### 3.3 Position Full Square-Off
- **Frontend Action:** Trader clicks "Close Position" (X) icon in Web Trader DOM.
- **Backend Endpoint:** `/book/squareoff.php`
- **HTTP Method:** `GET`
- **Parameters:** `token`, `id={order_id}`, `fingerprint={fingerprint}`
- **Database Tables Involved:** `active_orders`, `trade_history`, `trading_accounts`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Position closed successfully"
  }
  ```
- **Social Fanout Behavior:** When executed on Master, server background worker creates squareoff intents for all 5 followers, closing all cloned positions in parallel.

---

### 3.4 Position Partial Square-Off
- **Frontend Action:** Trader enters partial lot (e.g. 0.50) in Edit Position modal.
- **Backend Endpoint:** `/book/squareoff.php`
- **HTTP Method:** `GET`
- **Parameters:** `token`, `id={order_id}`, `fingerprint={fingerprint}`, `close_mode=partial`, `partial_lot=0.50`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Position partially closed"
  }
  ```
- **Replication Behavior:** Master position lot is reduced from 1.00 to 0.50; Follower position lot is reduced proportionally from 3.00 to 1.50.

---

### 3.5 Cancel Pending Limit / Stop Order
- **Frontend Action:** Trader cancels a pending limit or stop order before it is filled.
- **Backend Endpoint:** `/book/cancel.php`
- **HTTP Method:** `GET`
- **Parameters:** `token`, `id={order_id}`, `fingerprint={fingerprint}`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "message": "Pending order cancelled"
  }
  ```
- **Replication Behavior:** Master pending order is removed; follower cloned pending orders vanish within 1.0s–2.0s.

---

### 3.6 Query Account Balance, Equity & Margin
- **Frontend Action:** Dashboard balance ribbon refresh.
- **Backend Endpoint:** `/book/balance.php`
- **HTTP Method:** `GET`
- **Parameters:** `token` (string, required)
- **Database Tables Involved:** `trading_accounts`
- **Expected Success Response:**
  ```json
  {
    "status": "success",
    "fund": "12233121.38",
    "balance": "12233121.38",
    "equity": "12233121.38"
  }
  ```
- **Staging Platform Discrepancy:** On Staging, `equity` is statically mapped to `balance` while positions are open, failing to reflect live floating P&L ([BUG-04]).

