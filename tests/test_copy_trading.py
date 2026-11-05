"""
Copy Trading Automated Test Suite for WavexOne.
Executes 10 distinct test orders (5 BUY, 5 SELL) on Copy Trading Master (ctmaster),
verifies real-time copy trade fanout to 5 Followers (ctf1–ctf5) with 3x multiplier,
and validates simultaneous automated position squareoff on all followers.
"""
import time
import pytest
from typing import Dict, Any, List
from config.settings import WavexSettings
from config.symbols import ORDER_MATRIX_PLAN
from core.client import WavexUserSession
from core.logger import logger


class TestCopyTradingSuite:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing Copy Trading Test Suite (Master: ctmaster + 5 Followers)...")
        master_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
        assert cls.master.authenticate(), f"Failed to authenticate master {cls.master.name}"

        cls.followers: List[WavexUserSession] = []
        for f_cfg in WavexSettings.COPY_FOLLOWERS:
            f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
            assert f_sess.authenticate(), f"Failed to authenticate follower {f_sess.name}"
            cls.followers.append(f_sess)

        logger.info(f"Master and {len(cls.followers)} followers authenticated successfully.")

    @classmethod
    def teardown_class(cls):
        # Cleanup any remaining positions
        open_m = cls.master.get_open_orders()
        for o in open_m:
            cls.master.squareoff_position(o["id"])

    @pytest.mark.parametrize("order_spec", ORDER_MATRIX_PLAN)
    def test_copy_trade_cycle(self, order_spec: Dict[str, Any]):
        idx = order_spec["id"]
        sym = order_spec["symbol"]
        side = order_spec["side"]
        lot = order_spec["lot"]

        logger.info(f"--- [Copy Trading #{idx}/10] Testing {side.upper()} {lot} {sym} ---")

        # 1. Place order on Master
        res = self.master.place_order(symbol=sym, side=side, lot=lot)
        assert res.get("status") == "success", f"Master order failed: {res.get('message')}"

        data = res.get("data", {})
        master_oid = str(data.get("orderId"))
        assert master_oid and master_oid != "None", f"Master did not receive orderId: {res}"
        logger.info(f"Master order accepted: ID={master_oid} (Latency: {res.get('_duration_ms')}ms)")

        # Allow async fanout to followers
        time.sleep(2.5)

        # 2. Verify all 5 followers received the copied order with 3x multiplier
        expected_follower_lot = round(lot * 3.0, 2)
        synced_count = 0
        follower_order_ids = {}

        for f_sess in self.followers:
            f_orders = f_sess.get_open_orders()
            # Match by symbol, side, and lot
            matched = [
                o for o in f_orders
                if o.get("symbol") == sym
                and o.get("bs", "").upper() == side.upper()
                and abs(float(o.get("lot", 0)) - expected_follower_lot) < 0.001
            ]
            assert len(matched) > 0, f"Follower {f_sess.name} did not receive copied order for {sym} {side} {expected_follower_lot} lot! Orders: {f_orders}"
            follower_order_ids[f_sess.name] = matched[0]["id"]
            synced_count += 1
            logger.info(f"  Follower {f_sess.name}: Copied Order ID={matched[0]['id']}, Lot={matched[0]['lot']} (3x Verified)")

        assert synced_count == len(self.followers), f"Expected 5 followers synced, got {synced_count}"

        # 3. Squareoff position on Master
        c_res = self.master.squareoff_position(master_oid)
        assert c_res.get("status") == "success", f"Squareoff failed on master: {c_res.get('message')}"
        logger.info(f"Master position {master_oid} sent for squareoff.")

        # Allow async close settlement across followers
        time.sleep(3.0)

        # 4. Verify all followers have closed their copied positions
        for f_sess in self.followers:
            f_orders_after = f_sess.get_open_orders()
            remains = any(o["id"] == follower_order_ids[f_sess.name] for o in f_orders_after)
            assert not remains, f"Follower {f_sess.name} position {follower_order_ids[f_sess.name]} was not closed after master squareoff!"
            logger.info(f"  Follower {f_sess.name}: Closed successfully (0 remaining open orders)")

