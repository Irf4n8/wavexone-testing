"""
Concurrent Separate Read Verification and Order Book Poller.
Independently queries open orders and balances across Master and 5 Followers.
Never relies on HTTP status codes or assumption of immediate execution.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Union
from core.client import WavexUserSession
from core.logger import logger


class BookPoller:
    """Provides concurrent separate read polling and verification across accounts."""

    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers
        self.all_accounts = [master] + followers

    def poll_single_account_orders(self, session: WavexUserSession) -> List[Dict[str, Any]]:
        """Query /book/orders.php for a single account."""
        return session.get_open_orders()

    def poll_all_accounts_orders(self) -> Dict[str, List[Dict[str, Any]]]:
        """Concurrently query /book/orders.php across Master and all 5 Followers."""
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_acc = {executor.submit(acc.get_open_orders): acc.name for acc in self.all_accounts}
            for future in as_completed(future_to_acc):
                acc_name = future_to_acc[future]
                try:
                    orders = future.result()
                    results[acc_name] = orders
                except Exception as e:
                    logger.error(f"Error querying orders for {acc_name}: {e}")
                    results[acc_name] = []
        return results

    def poll_all_accounts_balance(self) -> Dict[str, Dict[str, Any]]:
        """Concurrently query /book/balance.php across all accounts."""
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_acc = {executor.submit(acc.get_balance): acc.name for acc in self.all_accounts}
            for future in as_completed(future_to_acc):
                acc_name = future_to_acc[future]
                try:
                    bal_data = future.result()
                    results[acc_name] = bal_data
                except Exception as e:
                    logger.error(f"Error querying balance for {acc_name}: {e}")
                    results[acc_name] = {}
        return results

    def wait_for_follower_replication(
        self,
        symbol: str,
        side: str,
        expected_lot: Optional[Union[float, Dict[str, float]]] = None,
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> Dict[str, Any]:
        """
        Poll all 5 follower order books concurrently until each follower has replicated the trade.
        Records exact discovery timestamp and latency per follower.
        """
        start_time = time.time()
        pending_followers = {f.name: f for f in self.followers}
        replicated_orders = {}

        while time.time() - start_time < timeout and pending_followers:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_name = {
                    executor.submit(f.get_open_orders): name
                    for name, f in pending_followers.items()
                }

                for future in as_completed(future_to_name):
                    name = future_to_name[future]
                    try:
                        orders = future.result()
                        for o in orders:
                            if o.get("symbol") != symbol:
                                continue
                            if side and str(o.get("bs", "")).upper() != side.upper():
                                continue
                            if expected_lot is not None:
                                actual_lot = float(o.get("lot", 0.0))
                                if isinstance(expected_lot, dict):
                                    exp = expected_lot.get(name)
                                    if exp is not None and abs(actual_lot - exp) > 0.001:
                                        continue
                                else:
                                    if abs(actual_lot - float(expected_lot)) > 0.001:
                                        continue

                            raw_p = o.get("avg") or o.get("open_price") or o.get("price") or "0"
                            try:
                                p_val = float(raw_p)
                            except (ValueError, TypeError):
                                p_val = 0.0

                            # For market orders, ensure matching engine has filled the price
                            if str(o.get("type", "")).lower() == "market" and p_val <= 0.0:
                                continue

                            # Match found
                            latency_ms = round((time.time() - start_time) * 1000, 2)
                            replicated_orders[name] = {
                                "order_id": str(o.get("id")),
                                "symbol": o.get("symbol"),
                                "side": o.get("bs"),
                                "lot": float(o.get("lot", 0.0)),
                                "open_price": p_val,
                                "sl": o.get("sl"),
                                "target": o.get("target"),
                                "latency_ms": latency_ms,
                                "raw_order": o
                            }
                            pending_followers.pop(name, None)
                            break
                    except Exception as e:
                        logger.error(f"Error polling follower {name}: {e}")

            if pending_followers:
                time.sleep(poll_interval)

        all_replicated = (len(replicated_orders) == len(self.followers))
        return {
            "all_replicated": all_replicated,
            "replicated_count": len(replicated_orders),
            "expected_count": len(self.followers),
            "replicated_orders": replicated_orders,
            "missing_followers": list(pending_followers.keys()),
            "total_wait_sec": round(time.time() - start_time, 2)
        }

    def wait_for_all_positions_closed(
        self,
        target_accounts: Optional[List[WavexUserSession]] = None,
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> Dict[str, Any]:
        """Poll order books until 0 open/pending orders remain for targeted accounts."""
        accounts = target_accounts or self.all_accounts
        start_time = time.time()
        pending_accounts = {acc.name: acc for acc in accounts}
        closed_timestamps = {}

        while time.time() - start_time < timeout and pending_accounts:
            with ThreadPoolExecutor(max_workers=len(pending_accounts)) as executor:
                future_to_name = {
                    executor.submit(acc.get_open_orders): name
                    for name, acc in pending_accounts.items()
                }

                for future in as_completed(future_to_name):
                    name = future_to_name[future]
                    try:
                        orders = future.result()
                        if len(orders) == 0:
                            closed_timestamps[name] = round((time.time() - start_time) * 1000, 2)
                            pending_accounts.pop(name, None)
                    except Exception as e:
                        logger.error(f"Error checking closure for {name}: {e}")

            if pending_accounts:
                time.sleep(poll_interval)

        all_closed = (len(pending_accounts) == 0)
        return {
            "all_closed": all_closed,
            "closed_latencies_ms": closed_timestamps,
            "unclosed_accounts": list(pending_accounts.keys()),
            "total_wait_sec": round(time.time() - start_time, 2)
        }

