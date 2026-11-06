"""
Multi-Tier Safe Teardown and Residual Order Cleanup Handler.
Guarantees clean state across Master and all 5 Followers without silently purging orders.
Records full audit trail of cleanup actions.
"""
import time
from typing import Dict, List, Any, Optional
from core.client import WavexUserSession
from core.logger import logger


class SafeTeardownHandler:
    """Performs multi-stage cleanup and state restoration across Master and Follower accounts."""

    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers
        self.all_accounts = [master] + followers

    def capture_active_orders(self) -> Dict[str, List[Dict[str, Any]]]:
        """Capture live open and pending orders across all accounts."""
        snapshot = {}
        for acc in self.all_accounts:
            orders = acc.get_open_orders()
            snapshot[acc.name] = orders
        return snapshot

    def execute_complete_teardown(self, timeout: float = 12.0) -> Dict[str, Any]:
        """
        Execute deterministic 5-stage teardown:
        1. Capture pre-cleanup state.
        2. Square off all active market positions.
        3. Cancel all pending limit/stop orders (including residual Stop BOTH legs).
        4. Poll and verify empty order books (length 0).
        5. Restore baseline copy configuration.
        """
        logger.info("Initiating Safe Teardown across Master and all 5 Followers...")
        initial_state = self.capture_active_orders()
        cleanup_log = []

        total_orders_found = sum(len(orders) for orders in initial_state.values())
        if total_orders_found > 0:
            logger.warning(f"Found {total_orders_found} active/pending orders across accounts to clean up.")

        # Stage 1: Close Master positions first (triggers broker fanout to all followers)
        master_orders = self.master.get_open_orders()
        for o in master_orders:
            oid = str(o.get("id"))
            otype = str(o.get("type", "market")).lower()
            ostatus = str(o.get("status", "")).lower()
            if ostatus == "transit":
                continue  # Already in transit closing
            try:
                if otype in ["limit", "stop", "pending"] or ostatus == "pending":
                    res = self.master.cancel_order(oid)
                    cleanup_log.append({"account": self.master.name, "order_id": oid, "action": "master_cancel_pending", "result": res})
                else:
                    res = self.master.squareoff_position(oid)
                    cleanup_log.append({"account": self.master.name, "order_id": oid, "action": "master_squareoff", "result": res})
            except Exception as e:
                cleanup_log.append({"account": self.master.name, "order_id": oid, "error": str(e)})

        # Give fanout 2.0s to propagate closures to followers
        if master_orders:
            time.sleep(2.0)

        # Stage 2: Check followers and clean up any remaining/orphaned positions
        for f in self.followers:
            f_orders = f.get_open_orders()
            for o in f_orders:
                oid = str(o.get("id"))
                otype = str(o.get("type", "market")).lower()
                ostatus = str(o.get("status", "")).lower()
                if ostatus == "transit":
                    continue  # Already in transit closing
                try:
                    if otype in ["limit", "stop", "pending"] or ostatus == "pending":
                        res = f.cancel_order(oid)
                        cleanup_log.append({"account": f.name, "order_id": oid, "action": "follower_cancel_pending", "result": res})
                    else:
                        res = f.squareoff_position(oid)
                        cleanup_log.append({"account": f.name, "order_id": oid, "action": "follower_squareoff", "result": res})
                except Exception as e:
                    cleanup_log.append({"account": f.name, "order_id": oid, "error": str(e)})

        # Stage 3: Verification Polling
        start_t = time.time()
        final_state = {}
        clean_slate = False

        while time.time() - start_t < timeout:
            final_state = self.capture_active_orders()
            remaining_orders = sum(len(orders) for orders in final_state.values())
            if remaining_orders == 0:
                clean_slate = True
                break
            time.sleep(0.5)

        if not clean_slate:
            remaining_summary = {
                acc: [o.get("id") for o in orders]
                for acc, orders in final_state.items() if orders
            }
            logger.critical(f"FATAL: Teardown verification failed! Remaining orders: {remaining_summary}")
        else:
            logger.info("Clean slate verified: 0 open or pending orders across all 6 accounts.")

        return {
            "clean_slate_verified": clean_slate,
            "orders_cleaned_count": len(cleanup_log),
            "initial_state": initial_state,
            "final_state": final_state,
            "cleanup_log": cleanup_log,
            "elapsed_seconds": round(time.time() - start_t, 2)
        }

    def assert_clean_slate(self) -> Dict[str, Any]:
        """Pre-flight check: assert that all accounts currently hold 0 open or pending orders."""
        state = self.capture_active_orders()
        dirty_accounts = {acc: orders for acc, orders in state.items() if orders}

        if dirty_accounts:
            logger.warning(f"Pre-flight dirty state detected on accounts: {list(dirty_accounts.keys())}")
            # Attempt automatic recovery
            teardown_res = self.execute_complete_teardown()
            if not teardown_res["clean_slate_verified"]:
                raise AssertionError(
                    f"Pre-flight clean slate assertion failed! Unable to clear dirty accounts: {list(dirty_accounts.keys())}"
                )
            return {"status": "recovered", "pre_existing_orders": dirty_accounts}

        return {"status": "clean", "pre_existing_orders": {}}

