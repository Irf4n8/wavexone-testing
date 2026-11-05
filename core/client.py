"""
WavexOne REST API & Social Trading Client.
Handles multi-user authentication, fingerprint generation, order execution,
real-time order book queries, position squareoff, order modification, and social trading lifecycles.
"""
import requests
import json
import time
import re
from typing import Dict, Any, List, Optional
from config.settings import WavexSettings
from core.logger import logger


class WavexUserSession:
    """Represents an isolated authenticated session for a master or follower user."""

    def __init__(self, email: str, password: str = WavexSettings.DEFAULT_PASSWORD, name: str = "", expected_account_id: str = ""):
        self.email = email
        self.password = password
        self.name = name or email.split("@")[0]
        self.expected_account_id = expected_account_id
        self.session = requests.Session()
        self.session.headers.update({
            "Origin": WavexSettings.BASE_URL,
            "Referer": f"{WavexSettings.BASE_URL}/dashboard/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.user_id: Optional[str] = None
        self.token: Optional[str] = None
        self.account_id: Optional[str] = None
        self.fingerprint: Optional[str] = None
        self.is_authenticated: bool = False
        self.call_logs: List[Dict[str, Any]] = []

    def _log_call(self, endpoint: str, method: str, duration_ms: float, status: int, request_data: Any, response_data: Any):
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user": self.name,
            "endpoint": endpoint,
            "method": method,
            "duration_ms": duration_ms,
            "status_code": status,
            "request": request_data,
            "response": response_data
        }
        self.call_logs.append(record)

    def authenticate(self) -> bool:
        """Authenticate with WavexOne check.php and load/validate live account details."""
        start_t = time.time()
        try:
            resp = self.session.post(
                WavexSettings.LOGIN_CHECK_ENDPOINT,
                data={"email": self.email, "password": self.password},
                timeout=12
            )
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            self._log_call(WavexSettings.LOGIN_CHECK_ENDPOINT, "POST", dur, resp.status_code, {"email": self.email}, data)

            if data.get("status") == "success":
                self.token = data.get("token")
                self.user_id = str(data.get("userID"))

                # Fetch real live trading account_id
                t_acc = time.time()
                acc_resp = self.session.get(
                    f"{WavexSettings.ACCOUNT_LIST_ENDPOINT}?token={self.token}",
                    timeout=10
                )
                dur_acc = round((time.time() - t_acc) * 1000, 2)
                try:
                    acc_list = acc_resp.json()
                except Exception:
                    acc_list = []
                self._log_call(WavexSettings.ACCOUNT_LIST_ENDPOINT, "GET", dur_acc, acc_resp.status_code, {}, acc_list)

                live_acc = None
                if isinstance(acc_list, list):
                    # Filter for live account (book == 'a')
                    live_accounts = [a for a in acc_list if str(a.get("book", "")).lower() == "a"]
                    live_acc = live_accounts[0] if live_accounts else (acc_list[0] if acc_list else None)

                if live_acc:
                    self.account_id = str(live_acc.get("account_id"))
                else:
                    self.account_id = None

                # Security & ID Validation Guard: Fail immediately on account mismatch
                if self.expected_account_id:
                    if str(self.account_id) != str(self.expected_account_id):
                        err_msg = (
                            f"FATAL: Account ID mismatch for {self.name}! "
                            f"Expected: {self.expected_account_id}, Live Fetched: {self.account_id}"
                        )
                        logger.error(err_msg)
                        self.is_authenticated = False
                        raise AssertionError(err_msg)

                self.is_authenticated = True
                self.generate_fingerprint()
                logger.info(f"[{self.name}] Authenticated (UID={self.user_id}, Account={self.account_id})")
                return True
            else:
                logger.error(f"[{self.name}] Auth failed: {data.get('message', resp.text)}")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] Login exception: {e}")
            raise e

    def generate_fingerprint(self) -> Optional[str]:
        """Fetch authoritative execution fingerprint from create_fingerprint.php."""
        if not self.token or not self.account_id:
            return None
        start_t = time.time()
        try:
            url = f"{WavexSettings.CREATE_FINGERPRINT_ENDPOINT}?token={self.token}&account_id={self.account_id}"
            res = self.session.get(url, timeout=10)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(WavexSettings.CREATE_FINGERPRINT_ENDPOINT, "GET", dur, res.status_code, {}, data)
            if data.get("status") == "success":
                self.fingerprint = data.get("fingerprint")
                return self.fingerprint
            return None
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to generate fingerprint: {e}")
            return None

    def get_balance(self) -> Dict[str, Any]:
        """Get account fund, balance, and equity."""
        if not self.token:
            return {}
        start_t = time.time()
        try:
            url = f"{WavexSettings.BALANCE_ENDPOINT}?token={self.token}"
            res = self.session.get(url, timeout=10)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(WavexSettings.BALANCE_ENDPOINT, "GET", dur, res.status_code, {}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Balance query error: {e}")
            return {}

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get live open and pending orders snapshot."""
        if not self.token:
            return []
        start_t = time.time()
        try:
            url = f"{WavexSettings.ORDERS_SNAPSHOT_ENDPOINT}?token={self.token}&snapshot=1&_={int(time.time()*1000)}"
            res = self.session.get(url, timeout=10)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(WavexSettings.ORDERS_SNAPSHOT_ENDPOINT, "GET", dur, res.status_code, {}, data)
            if data.get("status") == "success":
                return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"[{self.name}] Orders query error: {e}")
            return []

    # -------------------------------------------------------------------------
    # Strict Separate Read Verification Polling (500ms intervals, 10s timeout)
    # -------------------------------------------------------------------------

    def wait_for_order_in_book(
        self,
        symbol: str,
        side: Optional[str] = None,
        expected_lot: Optional[float] = None,
        order_type: Optional[str] = None,
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> Optional[Dict[str, Any]]:
        """Poll /book/orders.php every 500ms until order is verified in book."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            orders = self.get_open_orders()
            for o in orders:
                if o.get("symbol") != symbol:
                    continue
                if side and o.get("bs", "").upper() != side.upper():
                    continue
                if order_type and o.get("type", "").lower() != order_type.lower():
                    continue
                if expected_lot is not None:
                    actual_lot = float(o.get("lot", 0))
                    if abs(actual_lot - expected_lot) > 0.001:
                        continue
                return o
            time.sleep(poll_interval)
        return None

    def wait_for_order_closure(self, order_id: str, timeout: float = 10.0, poll_interval: float = 0.5) -> bool:
        """Poll /book/orders.php every 500ms until order is completely gone."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            orders = self.get_open_orders()
            if not any(str(o.get("id")) == str(order_id) for o in orders):
                return True
            time.sleep(poll_interval)
        return False

    def wait_for_all_closed(self, timeout: float = 10.0, poll_interval: float = 0.5) -> bool:
        """Poll /book/orders.php until 0 open or pending orders remain."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            orders = self.get_open_orders()
            if len(orders) == 0:
                return True
            time.sleep(poll_interval)
        return False

    # -------------------------------------------------------------------------
    # Execution & Management Endpoints
    # -------------------------------------------------------------------------

    def place_order(
        self,
        symbol: str,
        side: str,
        lot: float = 1.00,
        order_type: str = "market",
        sl: str = "",
        target: str = "",
        trigger: str = "",
        stop_hft_type: str = "",
        lotb: str = "",
        triggerb: str = "",
        slb: str = "",
        targetb: str = "",
        lots: str = "",
        triggers: str = "",
        sls: str = "",
        targets: str = ""
    ) -> Dict[str, Any]:
        """Place an order via trade/placeorder.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        self.generate_fingerprint()
        lot_str = f"{lot:.2f}"
        if order_type == "stop":
            query = (
                f"type=stop&bs={side.lower()}&lotb={lotb or lot_str}&slb={slb}&targetb={targetb}&triggerb={triggerb}"
                f"&lots={lots or lot_str}&sls={sls}&targets={targets}&triggers={triggers}"
                f"&symbol={symbol}&stop_hft_type={stop_hft_type}"
                f"&token={self.token}&clicked=yes&fingerprint={self.fingerprint or ''}"
            )
        elif order_type == "limit":
            query = (
                f"type=limit&bs={side.lower()}&lot={lot_str}&sl={sl}&target={target}&trigger={trigger}"
                f"&symbol={symbol}&token={self.token}&clicked=yes&fingerprint={self.fingerprint or ''}"
            )
        else:
            query = (
                f"type={order_type}&bs={side.lower()}&lot={lot_str}&sl={sl}&target={target}"
                f"&symbol={symbol}&token={self.token}&clicked=yes&fingerprint={self.fingerprint or ''}"
            )

        url = f"{WavexSettings.PLACE_ORDER_ENDPOINT}?{query}"
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = dur
            data["_request_url"] = url
            self._log_call(WavexSettings.PLACE_ORDER_ENDPOINT, "GET", dur, res.status_code, query, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Place order exception: {e}")
            return {"status": "error", "message": str(e), "_request_url": url}

    def squareoff_position(self, order_id: str) -> Dict[str, Any]:
        """Squareoff / Close an open position via book/squareoff.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        self.generate_fingerprint()
        url = f"{WavexSettings.SQUAREOFF_ENDPOINT}?token={self.token}&id={order_id}&fingerprint={self.fingerprint or ''}"
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = dur
            self._log_call(WavexSettings.SQUAREOFF_ENDPOINT, "GET", dur, res.status_code, {"id": order_id}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Squareoff exception for {order_id}: {e}")
            return {"status": "error", "message": str(e)}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending limit or stop order via book/cancel.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        self.generate_fingerprint()
        url = f"{WavexSettings.CANCEL_ORDER_ENDPOINT}?token={self.token}&id={order_id}&fingerprint={self.fingerprint or ''}"
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = dur
            self._log_call(WavexSettings.CANCEL_ORDER_ENDPOINT, "GET", dur, res.status_code, {"id": order_id}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Cancel order exception for {order_id}: {e}")
            return {"status": "error", "message": str(e)}

    def modify_order(self, order_id: str, name: str, val: str) -> Dict[str, Any]:
        """Modify an open order's StopLoss or TargetPoint via book/modify.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        self.generate_fingerprint()
        url = (
            f"{WavexSettings.MODIFY_ORDER_ENDPOINT}?token={self.token}&id={order_id}"
            f"&name={name}&val={val}&fingerprint={self.fingerprint or ''}"
        )
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = dur
            self._log_call(WavexSettings.MODIFY_ORDER_ENDPOINT, "GET", dur, res.status_code, {"id": order_id, "name": name, "val": val}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Modify order exception for {order_id}: {e}")
            return {"status": "error", "message": str(e)}

    def close_or_cancel(self, order_id: str, order_type: str = "market") -> Dict[str, Any]:
        """Intelligently squareoff market positions or cancel pending limit/stop orders."""
        if str(order_type).lower() in ["limit", "stop", "pending"]:
            return self.cancel_order(order_id)
        return self.squareoff_position(order_id)

    def get_live_price(self, symbol: str = "X:BTCUSD") -> float:
        """Query live execution price from trading engine using dynamic probe."""
        if not self.token:
            return 80450.0
        self.generate_fingerprint()
        url = (
            f"{WavexSettings.PLACE_ORDER_ENDPOINT}?type=market&bs=buy&lot=0.01"
            f"&sl=999999&target=0&symbol={symbol}&token={self.token}&clicked=yes&fingerprint={self.fingerprint or ''}"
        )
        try:
            res = self.session.get(url, timeout=10)
            msg = res.json().get("message", "")
            match = re.search(r"last price\s+([0-9.]+)", msg)
            if match:
                return float(match.group(1))
        except Exception as e:
            logger.warning(f"Could not parse live price from probe: {e}")
        return 80450.0

    # -------------------------------------------------------------------------
    # Social Trading Follow / Unfollow / Method Management
    # -------------------------------------------------------------------------

    def follow_copy_master(self, master_uid: str, method: str = "multiplier", value: str = "3.0") -> Dict[str, Any]:
        """Follow a Copy Trading master using GET user/follow.php."""
        if not self.token:
            return {}
        start_t = time.time()
        val_str = str(value) if method == "multiplier" else ""
        url = (
            f"{WavexSettings.COPY_FOLLOW_ENDPOINT}?token={self.token}"
            f"&follow={master_uid}&type=follow&method={method}&value={val_str}"
        )
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"raw": res.text}
            self._log_call(WavexSettings.COPY_FOLLOW_ENDPOINT, "GET", dur, res.status_code, {"follow": master_uid, "type": "follow", "method": method, "value": val_str}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] follow_copy_master exception: {e}")
            return {"status": "error", "message": str(e)}

    def unfollow_copy_master(self, master_uid: str) -> Dict[str, Any]:
        """Unfollow a Copy Trading master using GET user/follow.php."""
        if not self.token:
            return {}
        start_t = time.time()
        url = (
            f"{WavexSettings.COPY_FOLLOW_ENDPOINT}?token={self.token}"
            f"&follow={master_uid}&type=unfollow"
        )
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"raw": res.text}
            self._log_call(WavexSettings.COPY_FOLLOW_ENDPOINT, "GET", dur, res.status_code, {"follow": master_uid, "type": "unfollow"}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] unfollow_copy_master exception: {e}")
            return {"status": "error", "message": str(e)}

    def update_copy_trading_method(self, master_uid: str, method: str = "multiplier", value: str = "3.0") -> Dict[str, Any]:
        """Update Copy Trading method (multiplier, balance, equity) via GET updateCopyTradingMethod.php."""
        if not self.token:
            return {}
        # Resolve subscription uid from copy list if available
        sub_uid = master_uid
        subs = self.get_copy_following()
        for s in subs:
            if str(s.get("manager_id")) == str(master_uid) or str(s.get("account_id")) == str(master_uid):
                sub_uid = str(s.get("uid", master_uid))
                break

        start_t = time.time()
        val_param = str(value) if method == "multiplier" else ""
        url = (
            f"{WavexSettings.UPDATE_COPY_METHOD_ENDPOINT}?token={self.token}"
            f"&uid={sub_uid}&method={method}&value={val_param}"
        )
        try:
            res = self.session.get(url, timeout=15)
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"raw": res.text}
            self._log_call(WavexSettings.UPDATE_COPY_METHOD_ENDPOINT, "GET", dur, res.status_code, {"uid": sub_uid, "method": method, "value": val_param}, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] update_copy_trading_method exception: {e}")
            return {"status": "error", "message": str(e)}

    def get_copy_followers(self) -> List[Dict[str, Any]]:
        """Get Copy Trading followers subscribed to this master."""
        try:
            res = self.session.get(f"{WavexSettings.COPY_MASTER_FOLLOWERS_ENDPOINT}?token={self.token}", timeout=10)
            data = res.json()
            followers_raw = data.get("data", {}).get("copyFollowersList", "[]")
            return json.loads(followers_raw) if isinstance(followers_raw, str) else followers_raw
        except Exception as e:
            logger.error(f"[{self.name}] get_copy_followers error: {e}")
            return []

    def get_copy_following(self) -> List[Dict[str, Any]]:
        """Get masters followed by this follower via userCopyFollowers.php."""
        if not self.token:
            return []
        try:
            res = self.session.get(f"{WavexSettings.BASE_URL}/user/userCopyFollowers.php?token={self.token}", timeout=10)
            data = res.json()
            f_list = data.get("data", {}).get("copyTradingList", "[]")
            return json.loads(f_list) if isinstance(f_list, str) else (f_list if isinstance(f_list, list) else [])
        except Exception as e:
            logger.error(f"[{self.name}] get_copy_following error: {e}")
            return []

    def get_mam_followers(self) -> List[Dict[str, Any]]:
        """Get MAM followers subscribed to this master."""
        try:
            res = self.session.get(f"{WavexSettings.MAM_MASTER_FOLLOWERS_ENDPOINT}?token={self.token}", timeout=10)
            data = res.json()
            mam_raw = data.get("data", {}).get("mamList", "[]")
            return json.loads(mam_raw) if isinstance(mam_raw, str) else mam_raw
        except Exception as e:
            logger.error(f"[{self.name}] get_mam_followers error: {e}")
            return []

    def get_pamm_followers(self) -> List[Dict[str, Any]]:
        """Get PAMM followers/investors subscribed to this master."""
        try:
            res = self.session.get(f"{WavexSettings.PAMM_MASTER_FOLLOWERS_ENDPOINT}?token={self.token}", timeout=10)
            data = res.json()
            pamm_raw = data.get("data", {}).get("pamList", "[]")
            return json.loads(pamm_raw) if isinstance(pamm_raw, str) else pamm_raw
        except Exception as e:
            logger.error(f"[{self.name}] get_pamm_followers error: {e}")
            return []

    # -------------------------------------------------------------------------
    # Client Portal, Balances & Withdrawal Limits
    # -------------------------------------------------------------------------

    def init_portal_session(self) -> bool:
        """Initialize ClientPortal session cookies using /ClientPortal/setPortalSession."""
        if not self.token:
            return False
        start_t = time.time()
        url = WavexSettings.PORTAL_SESSION_ENDPOINT
        try:
            res = self.session.post(
                url,
                data={"token": self.token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=12
            )
            dur = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"raw": res.text}
            self._log_call(url, "POST", dur, res.status_code, {"token": "***"}, data)
            return data.get("status") == "success"
        except Exception as e:
            logger.error(f"[{self.name}] init_portal_session exception: {e}")
            return False

    def get_portal_bootstrap(self) -> Dict[str, Any]:
        """Fetch portal bootstrap metrics (summary, accounts, wallets, funds) via apiBootstrap."""
        if not self.token:
            return {}
        self.init_portal_session()
        start_t = time.time()
        url = f"{WavexSettings.PORTAL_BOOTSTRAP_ENDPOINT}?token={self.token}"
        try:
            res = self.session.get(url, timeout=12)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(url, "GET", dur, res.status_code, {}, data)
            return data.get("data", {}) if data.get("status") == "success" else {}
        except Exception as e:
            logger.error(f"[{self.name}] get_portal_bootstrap error: {e}")
            return {}

    def get_redeem_config(self) -> Dict[str, Any]:
        """Fetch full redeem config payload via apiRedeemConfig."""
        if not self.token:
            return {}
        self.init_portal_session()
        start_t = time.time()
        url = f"{WavexSettings.PORTAL_REDEEM_CONFIG_ENDPOINT}?token={self.token}"
        try:
            res = self.session.get(url, timeout=12)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(url, "GET", dur, res.status_code, {}, data)
            return data.get("data", {}) if data.get("status") == "success" else {}
        except Exception as e:
            logger.error(f"[{self.name}] get_redeem_config error: {e}")
            return {}

    def get_leverage(self) -> int:
        """Read live account leverage from portal bootstrap API, fallback to settings."""
        try:
            boot = self.get_portal_bootstrap()
            accounts = boot.get("accounts", [])
            for a in accounts:
                if str(a.get("code")) == str(self.account_id) or str(a.get("token")) == str(self.token):
                    lev = a.get("leverage") or a.get("subgroup_value")
                    if lev:
                        return int(lev)
            if accounts and accounts[0].get("leverage"):
                return int(accounts[0]["leverage"])
        except Exception as e:
            logger.warning(f"[{self.name}] Error reading leverage from API: {e}")
        return WavexSettings.DEFAULT_LEVERAGE

    def is_account_verified(self) -> bool:
        """Check whether user is verified / KYC approved in client portal."""
        try:
            boot = self.get_portal_bootstrap()
            user = boot.get("user", {})
            return int(user.get("accountVerified", 0)) == 1 or int(user.get("verified", 0)) == 1
        except Exception as e:
            logger.warning(f"[{self.name}] Error reading verification status: {e}")
            return False

    def get_withdraw_limit(self) -> Dict[str, Any]:
        """Fetch withdraw limit details (available, open_orders, ratio, pending) via apiRedeemConfig."""
        cfg = self.get_redeem_config()
        return cfg.get("withdrawLimit", {})

    def get_pamm_withdraw_limit(self, pamm_master_uid: str) -> Dict[str, Any]:
        """Fetch PAMM follower withdraw limit, locked margin, and open order safeguards via withdrawPammAmount.php."""
        if not self.token or not self.user_id:
            return {}
        start_t = time.time()
        url = (
            f"{WavexSettings.PAMM_WITHDRAW_ENDPOINT}?token={self.token}"
            f"&pamm={pamm_master_uid}&user={self.user_id}&type=limit&amount=0"
        )
        try:
            res = self.session.get(url, timeout=12)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(url, "GET", dur, res.status_code, {}, data)
            if data.get("status") == "success":
                return data.get("data", {})
            return data
        except Exception as e:
            logger.error(f"[{self.name}] get_pamm_withdraw_limit error: {e}")
            return {}

    def request_withdraw_otp(self, method: str, amount: float, withdraw_address: str, source_id: str) -> Dict[str, Any]:
        """Request OTP for withdrawal via apiSendWithdrawOtp."""
        if not self.token:
            return {}
        self.init_portal_session()
        start_t = time.time()
        url = WavexSettings.PORTAL_SEND_OTP_ENDPOINT
        payload = {
            "token": self.token,
            "method": method,
            "amount": amount,
            "withdrawAddress": withdraw_address,
            "sourceId": source_id
        }
        try:
            res = self.session.post(url, json=payload, timeout=12)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(url, "POST", dur, res.status_code, payload, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] request_withdraw_otp error: {e}")
            return {"status": "error", "message": str(e)}

    def submit_withdraw(self, method: str, amount: float, withdraw_address: str, otp: str, source_id: str) -> Dict[str, Any]:
        """Submit withdrawal request via apiSubmitWithdraw."""
        if not self.token:
            return {}
        self.init_portal_session()
        start_t = time.time()
        url = WavexSettings.PORTAL_SUBMIT_WITHDRAW_ENDPOINT
        payload = {
            "token": self.token,
            "method": method,
            "amount": amount,
            "withdrawAddress": withdraw_address,
            "otp": otp,
            "sourceId": source_id
        }
        try:
            res = self.session.post(url, json=payload, timeout=12)
            dur = round((time.time() - start_t) * 1000, 2)
            data = res.json()
            self._log_call(url, "POST", dur, res.status_code, payload, data)
            return data
        except Exception as e:
            logger.error(f"[{self.name}] submit_withdraw error: {e}")
            return {"status": "error", "message": str(e)}
