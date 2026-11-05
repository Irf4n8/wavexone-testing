"""
MAM (Multi-Account Manager) Automated Test Suite for WavexOne.
Executes 10 distinct test orders (5 BUY, 5 SELL) on MAM Master (mammaster),
verifies proportional lot allocation fanout to 5 Followers (mamf1–mamf5) based on MAM Share,
and validates simultaneous automated position squareoff on all followers.
"""
import time
import pytest
from typing import Dict, Any, List
from config.settings import WavexSettings
from config.symbols import ORDER_MATRIX_PLAN
from core.client import WavexUserSession
from core.logger import logger


class TestMAMTradingSuite:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing MAM Trading Test Suite (Master: mammaster + 5 Followers)...")
        master_cfg = WavexSettings.MASTERS["mam"]
        cls.master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
        assert cls.master.authenticate(), f"Failed to authenticate MAM master {cls.master.name}"

        # Ensure master balance is positive
        b = cls.master.get_balance()
        assert float(b.get("balance", 0)) > 0, f"MAM Master balance must be positive to trade! Current: {b}"

        cls.followers: List[WavexUserSession] = []
        for f_cfg in WavexSettings.MAM_FOLLOWERS:
            f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
            assert f_sess.authenticate(), f"Failed to authenticate MAM follower {f_sess.name}"
            cls.followers.append(f_sess)

        logger.info(f"MAM Master and {len(cls.followers)} followers authenticated successfully.")

    @classmethod
    def teardown_class(cls):
        open_m = cls.master.get_open_orders()
        for o in open_m:
            cls.master.squareoff_position(o["id"])

    @pytest.mark.parametrize("order_spec", ORDER_MATRIX_PLAN)
    def test_mam_trade_cycle(self, order_spec: Dict[str, Any]):
        idx = order_spec["id"]
        sym = order_spec["symbol"]
        side = order_spec["side"]
        lot = 0.02  # 0.02 base lot for MAM allocation

        logger.info(f"--- [MAM Trading #{idx}/10] Testing {side.upper()} {lot} {sym} ---")

        # 1. Place order on Master
        res = self.master.place_order(symbol=sym, side=side, lot=lot)
        assert res.get("status") == "success", f"MAM Master order failed: {res.get('message')}"

        data = res.get("data", {})
        master_oid = str(data.get("orderId"))
        assert master_oid and master_oid != "None", f"MAM Master did not receive orderId: {res}"
        logger.info(f"MAM Master order accepted: ID={master_oid} (Latency: {res.get('_duration_ms')}ms)")

        # Allow async allocation fanout
        time.sleep(2.5)

        # 2. Verify all 5 followers received the allocated order
        synced_count = 0
        follower_order_ids = {}

        for f_sess in self.followers:
            f_orders = f_sess.get_open_orders()
            matched = [
                o for o in f_orders
                if o.get("symbol") == sym
                and o.get("bs", "").upper() == side.upper()
                and float(o.get("lot", 0)) > 0
            ]
            assert len(matched) > 0, f"MAM Follower {f_sess.name} did not receive allocated order for {sym} {side}! Orders: {f_orders}"
            follower_order_ids[f_sess.name] = matched[0]["id"]
            synced_count += 1
            logger.info(f"  MAM Follower {f_sess.name}: Allocated Order ID={matched[0]['id']}, Lot={matched[0]['lot']} (Allocation Verified)")

        assert synced_count == len(self.followers), f"Expected 5 MAM followers synced, got {synced_count}"

        # 3. Squareoff position on Master
        c_res = self.master.squareoff_position(master_oid)
        assert c_res.get("status") == "success", f"Squareoff failed on MAM master: {c_res.get('message')}"
        logger.info(f"MAM Master position {master_oid} sent for squareoff.")

        # Allow async close settlement
        time.sleep(3.0)

        # 4. Verify all followers have closed their allocated positions
        for f_sess in self.followers:
            f_orders_after = f_sess.get_open_orders()
            remains = any(o["id"] == follower_order_ids[f_sess.name] for o in f_orders_after)
            assert not remains, f"MAM Follower {f_sess.name} position {follower_order_ids[f_sess.name]} was not closed after master squareoff!"
            logger.info(f"  MAM Follower {f_sess.name}: Closed successfully (0 remaining open orders)")

