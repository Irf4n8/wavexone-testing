"""
WavexOne REST API & Social Trading Client.
Handles multi-user authentication, fingerprint generation, order execution,
real-time order book queries, and position squareoff.
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

    def __init__(self, email: str, password: str = WavexSettings.DEFAULT_PASSWORD, name: str = ""):
        self.email = email
        self.password = password
        self.name = name or email.split("@")[0]
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

    def authenticate(self) -> bool:
        """Authenticate with WavexOne check.php and load account details."""
        try:
            resp = self.session.post(
                WavexSettings.LOGIN_CHECK_ENDPOINT,
                data={"email": self.email, "password": self.password},
                timeout=12
            )
            data = resp.json()
            if data.get("status") == "success":
                self.token = data.get("token")
                self.user_id = data.get("userID")
                self.is_authenticated = True

                # Discover active account_id
                acc_resp = self.session.get(
                    f"{WavexSettings.ACCOUNT_LIST_ENDPOINT}?token={self.token}",
                    timeout=10
                )
                try:
                    acc_list = acc_resp.json()
                    if isinstance(acc_list, list) and len(acc_list) > 0:
                        self.account_id = str(acc_list[0].get("account_id"))
                except Exception:
                    self.account_id = None

                # Generate authoritative fingerprint
                self.generate_fingerprint()
                return True
            else:
                logger.error(f"[{self.name}] Auth failed: {data.get('message', resp.text)}")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] Login exception: {e}")
            return False

    def generate_fingerprint(self) -> Optional[str]:
        """Fetch authoritative execution fingerprint from create_fingerprint.php."""
        if not self.token or not self.account_id:
            return None
        try:
            url = f"{WavexSettings.CREATE_FINGERPRINT_ENDPOINT}?token={self.token}&account_id={self.account_id}"
            res = self.session.get(url, timeout=10)
            data = res.json()
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
        try:
            res = self.session.get(f"{WavexSettings.BALANCE_ENDPOINT}?token={self.token}", timeout=10)
            return res.json()
        except Exception as e:
            logger.error(f"[{self.name}] Balance query error: {e}")
            return {}

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get live open and pending orders snapshot."""
        if not self.token:
            return []
        try:
            url = f"{WavexSettings.ORDERS_SNAPSHOT_ENDPOINT}?token={self.token}&snapshot=1&_={int(time.time()*1000)}"
            res = self.session.get(url, timeout=10)
            data = res.json()
            if data.get("status") == "success":
                return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"[{self.name}] Orders query error: {e}")
            return []

    def place_order(
        self,
        symbol: str,
        side: str,
        lot: float = 0.01,
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
        """Place an order via trade/placeorder.php supporting Market, Limit, and Stop HFT."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        # Refresh fingerprint before placement
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
            duration_ms = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = duration_ms
            data["_request_url"] = url
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Place order exception: {e}")
            return {"status": "error", "message": str(e), "_request_url": url}

    def squareoff_position(self, order_id: str) -> Dict[str, Any]:
        """Squareoff / Close an open position via book/squareoff.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        # Refresh fingerprint before squareoff
        self.generate_fingerprint()

        url = f"{WavexSettings.SQUAREOFF_ENDPOINT}?token={self.token}&id={order_id}&fingerprint={self.fingerprint or ''}"
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            duration_ms = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = duration_ms
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Squareoff exception for {order_id}: {e}")
            return {"status": "error", "message": str(e)}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending limit or stop HFT order via book/cancel.php."""
        if not self.token:
            return {"status": "fail", "message": "Not authenticated"}

        self.generate_fingerprint()
        url = f"{WavexSettings.CANCEL_ORDER_ENDPOINT}?token={self.token}&id={order_id}&fingerprint={self.fingerprint or ''}"
        start_t = time.time()
        try:
            res = self.session.get(url, timeout=15)
            duration_ms = round((time.time() - start_t) * 1000, 2)
            try:
                data = res.json()
            except Exception:
                data = {"status": "raw", "text": res.text}
            data["_duration_ms"] = duration_ms
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Cancel order exception for {order_id}: {e}")
            return {"status": "error", "message": str(e)}

    def close_or_cancel(self, order_id: str, order_type: str = "market") -> Dict[str, Any]:
        """Intelligently squareoff market positions or cancel pending limit/stop orders."""
        if order_type.lower() in ["limit", "stop", "pending"]:
            return self.cancel_order(order_id)
        return self.squareoff_position(order_id)

    def get_live_price(self, symbol: str = "C:EURUSD") -> float:
        """Query live execution price from trading engine."""
        if not self.token:
            return 1.1260
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
        return 1.1260

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

