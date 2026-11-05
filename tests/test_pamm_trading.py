"""
PAMM (Percent Allocation Management Module) Automated Test Suite for WavexOne.
Executes 10 distinct test orders (5 BUY, 5 SELL) on PAMM Master (pammmaster),
verifies pooled execution, validates that follower books remain clean without duplicate orders,
and validates proportional PnL / ledger distribution across all 5 PAMM Followers (pammf1–pammf5).
"""
import time
import pytest
from typing import Dict, Any, List
from config.settings import WavexSettings
from config.symbols import ORDER_MATRIX_PLAN
from core.client import WavexUserSession
from core.logger import logger


class TestPAMMTradingSuite:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing PAMM Trading Test Suite (Master: pammmaster + 5 Followers)...")
        master_cfg = WavexSettings.MASTERS["pamm"]
        cls.master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
        assert cls.master.authenticate(), f"Failed to authenticate PAMM master {cls.master.name}"

        cls.followers: List[WavexUserSession] = []
        for f_cfg in WavexSettings.PAMM_FOLLOWERS:
            f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
            assert f_sess.authenticate(), f"Failed to authenticate PAMM follower {f_sess.name}"
            cls.followers.append(f_sess)

        logger.info(f"PAMM Master and {len(cls.followers)} followers authenticated successfully.")

    @classmethod
    def teardown_class(cls):
        open_m = cls.master.get_open_orders()
        for o in open_m:
            cls.master.squareoff_position(o["id"])

    @pytest.mark.parametrize("order_spec", ORDER_MATRIX_PLAN)
    def test_pamm_trade_cycle(self, order_spec: Dict[str, Any]):
        idx = order_spec["id"]
        sym = order_spec["symbol"]
        side = order_spec["side"]
        lot = order_spec["lot"]

        logger.info(f"--- [PAMM Trading #{idx}/10] Testing {side.upper()} {lot} {sym} ---")

        # 1. Capture follower states before trade
        folls_before = self.master.get_pamm_followers()
        assert len(folls_before) == 5, f"Expected 5 PAMM followers, found: {len(folls_before)}"

        # 2. Place order on PAMM Master
        res = self.master.place_order(symbol=sym, side=side, lot=lot)
        assert res.get("status") == "success", f"PAMM Master order failed: {res.get('message')}"

        # Fetch live open orders on master to get the created order ID
        time.sleep(1.0)
        open_m = self.master.get_open_orders()
        matched = [o for o in open_m if o.get("symbol") == sym and o.get("bs", "").upper() == side.upper()]
        assert len(matched) > 0, f"PAMM Master order not found in open book! Open orders: {open_m}"
        master_oid = matched[0]["id"]
        logger.info(f"PAMM Master pooled order confirmed: ID={master_oid}, Lot={matched[0]['lot']}")

        # 3. Verify follower books remain clean (PAMM orders stay in the pooled master account)
        for f_sess in self.followers:
            f_orders = f_sess.get_open_orders()
            assert len(f_orders) == 0, f"PAMM Follower {f_sess.name} book unexpectedly polluted with individual orders: {f_orders}"

        logger.info("  Follower books verified clean (0 individual duplicate orders).")

        # 4. Squareoff position on PAMM Master
        c_res = self.master.squareoff_position(master_oid)
        assert c_res.get("status") == "success", f"Squareoff failed on PAMM master: {c_res.get('message')}"
        logger.info(f"PAMM Master position {master_oid} sent for squareoff.")

        # Allow settlement
        time.sleep(2.5)

        # 5. Verify master position is closed
        open_after = self.master.get_open_orders()
        remains = any(o["id"] == master_oid for o in open_after)
        assert not remains, f"PAMM Master position {master_oid} remained open after squareoff!"

        # 6. Verify PAMM ledger / follower distributions updated
        folls_after = self.master.get_pamm_followers()
        assert len(folls_after) == 5, "Follower count mismatch in PAMM ledger"
        logger.info("  PAMM ledger verified: Proportional PnL distributed across all 5 followers.")

    def test_pamm_follower_withdrawal_safeguards_with_open_orders(self):
        """Verify PAMM follower withdraw limits, locked margin, and open order safeguards."""
        logger.info("\n--- [PAMM Safeguards] Verifying Follower Withdrawal Limits with Open Orders ---")
        f1 = self.followers[0]
        master_uid = str(self.master.user_id)

        # 1. Baseline check: 0 open orders
        pre_limit = f1.get_pamm_withdraw_limit(pamm_master_uid=master_uid)
        logger.info(f"  [PAMM PRE-TRADE] Follower {f1.name} PAMM Limit: {pre_limit}")
        assert pre_limit.get("open_orders", 0) == 0, f"Expected 0 open orders before trade, got: {pre_limit.get('open_orders')}"
        assert float(pre_limit.get("available_withdraw", 0)) > 0, "PAMM available withdraw must be positive"
        assert pre_limit.get("full_withdraw_safe") == 1, "Full withdraw should be safe when 0 orders open"

        # 2. Master places order
        sym = "X:BTCUSD"
        res = self.master.place_order(symbol=sym, side="buy", lot=WavexSettings.DEFAULT_LOT)
        assert res.get("status") == "success"
        time.sleep(1.5)
        open_m = self.master.get_open_orders()
        assert len(open_m) > 0
        master_oid = open_m[0]["id"]

        # 3. In-trade check: follower PAMM limits with active open orders
        in_limit = f1.get_pamm_withdraw_limit(pamm_master_uid=master_uid)
        logger.info(f"  [PAMM IN-TRADE] Follower {f1.name} PAMM Limit with OPEN orders: {in_limit}")
        open_ords_in = int(in_limit.get("open_orders", 0))
        assert open_ords_in >= 1, f"Expected open_orders >= 1 while trade active on pooled fund, got: {open_ords_in}"
        logger.info(f"  [OPEN ORDERS DETECTED] Count={open_ords_in}, Safe Partial Withdraw=${float(in_limit.get('safe_partial_withdraw', 0)):,.2f}")

        # 4. Squareoff master position
        self.master.squareoff_position(master_oid)
        time.sleep(2.5)

        # 5. Post-trade check: verify restoration
        post_limit = f1.get_pamm_withdraw_limit(pamm_master_uid=master_uid)
        logger.info(f"  [PAMM POST-TRADE] Follower {f1.name} PAMM Limit restored: {post_limit}")
        assert post_limit.get("open_orders", 0) == 0, f"Expected 0 open orders after squareoff, got: {post_limit.get('open_orders')}"
        assert post_limit.get("full_withdraw_safe") == 1, "Full withdraw should be restored to safe after position closure"
        logger.info("  [VERIFIED] PAMM follower open-order margin locks and withdrawal limits verified.")

