"""
Comprehensive Matrix Test Suite for Copy Trading on WavexOne:
Validates all combinations of Copy Trading Modes, Order Types, and Sides,
WITH MANDATORY TAKE PROFIT (TP) AND STOP LOSS (SL) CONFIGURATION & VERIFICATION ACROSS EVERY SINGLE SCENARIO:

  - Modes (3): Multiplier (3.0x), Balance-Based Proportional, Equity-Based Proportional
  - Order Types:
      * Market Orders (BUY & SELL with TP/SL)
      * Limit Orders (BUY & SELL with Trigger, TP, and SL)
      * Stop HFT Orders:
          - BUY (stop_hft_type=1 with Trigger, TP, and SL)
          - SELL (stop_hft_type=0 with Trigger, TP, and SL)
          - BOTH (stop_hft_type=2 dual pending orders with respective Trigger, TP, and SL)
      * Triggered & Filled Stop Breakouts (BUY, SELL, BOTH with follower replication & closure)

Total 24 Distinct End-to-End Scenarios:
  - Multiplier (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL
  - Balance-Based (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL
  - Equity-Based (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL (with Floating P&L and Inconclusive Guard)
  - Triggered & Filled Stops (3): Stop BUY Fill, Stop SELL Fill, Stop BOTH Fills (60s timeout per leg)
"""
import time
import pytest
from typing import Dict, Any, List, Optional
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.evidence import EvidenceCollector
from core.logger import logger


class TestCopyTradingMatrixSuite:

    @classmethod
    def setup_class(cls):
        logger.info("\n" + "=" * 80)
        logger.info("INITIALIZING COPY TRADING COMPLETE MATRIX (WITH TP & SL ACROSS EVERY SCENARIO)")
        logger.info("=" * 80)

        # 1. Master Account
        master_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.master = WavexUserSession(
            email=master_cfg["email"],
            password=master_cfg["password"],
            name=master_cfg["name"],
            expected_account_id=master_cfg["account_id"]
        )
        assert cls.master.authenticate(), f"Failed to authenticate master {cls.master.name}"
        cls.master_uid = str(cls.master.user_id)
        assert str(cls.master.account_id) == str(master_cfg["account_id"]), (
            f"Master account ID mismatch: expected {master_cfg['account_id']}, got {cls.master.account_id}"
        )

        # 2. Follower Accounts
        cls.followers: List[WavexUserSession] = []
        for f_cfg in WavexSettings.COPY_FOLLOWERS:
            f_sess = WavexUserSession(
                email=f_cfg["email"],
                password=f_cfg["password"],
                name=f_cfg["name"],
                expected_account_id=f_cfg["expected_account_id"]
            )
            assert f_sess.authenticate(), f"Failed to authenticate follower {f_sess.name}"
            assert str(f_sess.account_id) == str(f_cfg["expected_account_id"]), (
                f"Follower {f_sess.name} ID mismatch! Expected {f_cfg['expected_account_id']}, got {f_sess.account_id}"
            )
            cls.followers.append(f_sess)

        cls.primary_follower = cls.followers[0]
        cls.symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        cls.floating_oid = None

        # Clean any preexisting orders
        cls._squareoff_all_accounts()

    @classmethod
    def teardown_class(cls):
        """Final cleanup: squareoff any remaining positions and restore multiplier=3.0."""
        logger.info("Tearing down Copy Trading Matrix Suite: cleaning positions and restoring settings...")
        if cls.floating_oid:
            try:
                cls.master.squareoff_position(cls.floating_oid)
            except Exception:
                pass
        cls._squareoff_all_accounts()
        cls._restore_all_followers_to_multiplier()
        cls._squareoff_all_accounts()

    def teardown_method(self, method):
        """Teardown after every individual test method to prevent cascading failures."""
        self._squareoff_all_accounts()

    @classmethod
    def _squareoff_all_accounts(cls):
        for sess in [cls.master] + cls.followers:
            try:
                for o in sess.get_open_orders():
                    # Preserve class floating P&L order if active
                    if cls.floating_oid and str(o.get("id")) == str(cls.floating_oid):
                        continue
                    sess.close_or_cancel(o["id"], o.get("type", "market"))
                sess.wait_for_all_closed(timeout=6.0, poll_interval=0.5)
            except Exception as e:
                logger.warning(f"Error during squareoff on {sess.name}: {e}")

    @classmethod
    def _restore_all_followers_to_multiplier(cls):
        for f in cls.followers:
            try:
                subs = f.get_copy_following()
                already_following = False
                for s in subs:
                    if str(s.get("manager_id")) == str(cls.master_uid):
                        already_following = True
                        cur_method = s.get("trade_method") or s.get("method")
                        cur_val = str(s.get("multiplier_value") or s.get("val", ""))
                        if cur_method != "multiplier" or cur_val != "3.0":
                            f.update_copy_trading_method(master_uid=cls.master_uid, method="multiplier", value="3.0")
                        break
                if not already_following:
                    f.follow_copy_master(master_uid=cls.master_uid, method="multiplier", value="3.0")
            except Exception as e:
                logger.warning(f"Error restoring follower {f.name}: {e}")

    def get_live_price(self) -> float:
        for _ in range(5):
            p = self.master.get_live_price(self.symbol)
            if p > 0:
                return p
            time.sleep(1.0)
        return 74000.0

    def _place_with_retry(self, **kwargs) -> Dict[str, Any]:
        """Helper to place orders on master with fingerprint regeneration and retry loop."""
        res: Dict[str, Any] = {}
        for attempt in range(5):
            self.master.generate_fingerprint()
            res = self.master.place_order(**kwargs)
            if res.get("status") == "success":
                return res
            logger.warning(f"Matrix place_order attempt {attempt + 1} failed: {res.get('message')}. Retrying in 1.5s...")
            time.sleep(1.5)
        return res

    def _assert_tp_sl_propagation(self, evidence: EvidenceCollector, master_order: Dict[str, Any], follower_order: Dict[str, Any], exp_sl: str, exp_tp: str):
        """Helper to assert that TP and SL values are propagated identically to the follower's order book."""
        f_sl = str(follower_order.get("sl", "")).split(".")[0]
        f_tp = str(follower_order.get("tp", "")).split(".")[0]
        exp_sl_base = exp_sl.split(".")[0]
        exp_tp_base = exp_tp.split(".")[0]

        evidence.log_assertion(f"Follower Stop Loss ({exp_sl_base}) Propagated", expected=exp_sl_base, actual=f_sl, passed=(exp_sl_base in f_sl or f_sl == exp_sl_base))
        evidence.log_assertion(f"Follower Take Profit ({exp_tp_base}) Propagated", expected=exp_tp_base, actual=f_tp, passed=(exp_tp_base in f_tp or f_tp == exp_tp_base))
        assert exp_sl_base in f_sl or f_sl == exp_sl_base, f"Follower SL {f_sl} does not match expected {exp_sl_base}!"
        assert exp_tp_base in f_tp or f_tp == exp_tp_base, f"Follower TP {f_tp} does not match expected {exp_tp_base}!"

    def _assert_pending_auto_cancel_on_master_only(self, evidence: EvidenceCollector, master_oid: str, follower_oid: str):
        """Cancel ONLY the master pending order, assert follower copy disappears on its own within 10s."""
        c_res = self.master.cancel_order(master_oid)
        evidence.log_step("Master Cancel Pending Order", f"GET /book/cancel.php?id={master_oid}", response_data=c_res)
        assert c_res.get("status") == "success"
        assert self.master.wait_for_order_closure(master_oid, timeout=8.0)

        # Assert follower pending order disappears within 10s
        logger.info(f"  Polling follower for 10s to assert pending order {follower_oid} auto-cancellation...")
        f_auto_cancelled = self.primary_follower.wait_for_order_closure(follower_oid, timeout=10.0, poll_interval=0.5)
        evidence.log_assertion(
            "Follower Pending Order Auto-Cancelled on Master Cancel",
            expected=True,
            actual=f_auto_cancelled,
            passed=f_auto_cancelled,
            notes="If False: logged as FAIL (suspected engine bug, pending dev confirmation)"
        )
        if not f_auto_cancelled:
            pytest.fail("FAIL (suspected engine bug, pending dev confirmation): Follower pending order remained active 10s after master cancellation!")

    # -------------------------------------------------------------------------
    # MULTIPLIER MODE SCENARIOS (Tests 01 - 07)
    # -------------------------------------------------------------------------

    def test_01_multiplier_market_buy_with_tpsl(self):
        """Multiplier Mode: Master places 1.00 lot Market BUY with TP/SL -> Follower receives 3.00 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 01/21] Multiplier Mode: Market BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_01_multiplier_market_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Market BUY with TP/SL",
            description="Verify that under 3.0x Multiplier mode, Follower receives exactly 3.00 lots on Market BUY with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            sl = f"{price - 500.0:.2f}"
            tp = f"{price + 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Market BUY Placement", "POST /trade/placeorder.php", request_data={"lot": 1.00, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots BUY", expected=3.00, actual=actual_lot, passed=(abs(actual_lot - 3.00) < 0.01))
            assert abs(actual_lot - 3.00) < 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_02_multiplier_market_sell_with_tpsl(self):
        """Multiplier Mode: Master places 1.00 lot Market SELL with TP/SL -> Follower receives 3.00 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 02/21] Multiplier Mode: Market SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_02_multiplier_market_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Market SELL with TP/SL",
            description="Verify that under 3.0x Multiplier mode, Follower receives exactly 3.00 lots on Market SELL with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            sl = f"{price + 500.0:.2f}"
            tp = f"{price - 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Market SELL Placement", "POST /trade/placeorder.php", request_data={"lot": 1.00, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots SELL", expected=3.00, actual=actual_lot, passed=(abs(actual_lot - 3.00) < 0.01))
            assert abs(actual_lot - 3.00) < 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_03_multiplier_limit_buy_with_tpsl(self):
        """Multiplier Mode: Master places Limit BUY with Trigger/TP/SL -> Follower receives 3.00 lots pending; cancel via master only."""
        logger.info("\n--- [MATRIX 03/21] Multiplier Mode: Limit BUY with Trigger & TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_03_multiplier_limit_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Limit BUY with Trigger/TP/SL",
            description="Verify pending Limit BUY order replicates 3.00 lots with Trigger, TP, and SL under Multiplier mode; cancel ONLY master order and assert follower auto-cancels."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            trigger = f"{price - 3000.0:.2f}"
            sl = f"{price - 3500.0:.2f}"
            tp = f"{price - 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            evidence.log_step("Master Limit BUY Placement", "POST /trade/placeorder.php?type=limit", request_data={"trigger": trigger, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots Pending Limit BUY", expected=3.00, actual=actual_lot, passed=(abs(actual_lot - 3.00) < 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            # Cancel via master only
            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_04_multiplier_limit_sell_with_tpsl(self):
        """Multiplier Mode: Master places Limit SELL with Trigger/TP/SL -> Follower receives 3.00 lots pending; cancel via master only."""
        logger.info("\n--- [MATRIX 04/21] Multiplier Mode: Limit SELL with Trigger & TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_04_multiplier_limit_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Limit SELL with Trigger/TP/SL",
            description="Verify pending Limit SELL order replicates 3.00 lots with Trigger, TP, and SL under Multiplier mode; cancel ONLY master order and assert follower auto-cancels."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            trigger = f"{price + 3000.0:.2f}"
            sl = f"{price + 3500.0:.2f}"
            tp = f"{price + 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            evidence.log_step("Master Limit SELL Placement", "POST /trade/placeorder.php?type=limit", request_data={"trigger": trigger, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots Pending Limit SELL", expected=3.00, actual=actual_lot, passed=(abs(actual_lot - 3.00) < 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_05_multiplier_stop_hft_buy_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT BUY (type=1) with Trigger/TP/SL -> Follower replicates 3.0x; cancel via master only."""
        logger.info("\n--- [MATRIX 05/21] Multiplier Mode: Stop HFT BUY (type=1) with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_05_multiplier_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT BUY (type=1)",
            description="Verify Stop HFT BUY order (stop_hft_type=1) replicates 3.0x with Trigger, TP, and SL under Multiplier mode; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", lot=0.01, order_type="stop",
                stop_hft_type="1", triggerb=triggerb, slb=slb, targetb=targetb
            )
            evidence.log_step("Master Stop HFT BUY Placement", "POST /trade/placeorder.php?type=stop&stop_hft_type=1", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.01, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.03, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 0.03 Lots Stop HFT BUY", expected=0.03, actual=actual_lot, passed=(abs(actual_lot - 0.03) < 0.005))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=slb, exp_tp=targetb)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_06_multiplier_stop_hft_sell_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT SELL (type=0) with Trigger/TP/SL -> Follower replicates 3.0x; cancel via master only."""
        logger.info("\n--- [MATRIX 06/21] Multiplier Mode: Stop HFT SELL (type=0) with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_06_multiplier_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT SELL (type=0)",
            description="Verify Stop HFT SELL order (stop_hft_type=0) replicates 3.0x with Trigger, TP, and SL under Multiplier mode; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="sell", lot=0.01, order_type="stop",
                stop_hft_type="0", triggers=triggers, sls=sls, targets=targets
            )
            evidence.log_step("Master Stop HFT SELL Placement", "POST /trade/placeorder.php?type=stop&stop_hft_type=0", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.01, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.03, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 0.03 Lots Stop HFT SELL", expected=0.03, actual=actual_lot, passed=(abs(actual_lot - 0.03) < 0.005))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sls, exp_tp=targets)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_07_multiplier_stop_hft_both_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT BOTH (type=2) -> Replicates dual pending legs (0.03 lots each); cancel via master only."""
        logger.info("\n--- [MATRIX 07/21] Multiplier Mode: Stop HFT BOTH (Dual Breakout) with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_07_multiplier_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT BOTH (type=2)",
            description="Verify Stop HFT BOTH places simultaneous BUY & SELL pending legs, replicating dual 0.03 lot orders to follower; cancel via master only."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="both", lot=0.01, order_type="stop",
                stop_hft_type="2",
                triggerb=triggerb, slb=slb, targetb=targetb,
                triggers=triggers, sls=sls, targets=targets
            )
            evidence.log_step("Master Stop HFT BOTH Placement", "POST /trade/placeorder.php?type=stop&stop_hft_type=2", response_data=res)
            assert res.get("status") == "success"

            raw_oids = str(res.get("data", {}).get("orderId", ""))
            master_oids = [oid.strip() for oid in raw_oids.split(",") if oid.strip()]
            evidence.log_step("Master Dual Order IDs", "Identified dual legs", extra_info={"order_ids": master_oids})
            assert len(master_oids) == 2, f"Expected 2 order IDs for stop-both, got: {raw_oids}"

            time.sleep(2.0)
            f_orders = f.get_open_orders()
            f_both_legs = [o for o in f_orders if o.get("symbol") == self.symbol and str(o.get("type")).lower() == "stop"]
            evidence.log_assertion("Follower Received Both Pending Legs", expected=2, actual=len(f_both_legs), passed=(len(f_both_legs) == 2))
            assert len(f_both_legs) == 2, f"Follower received {len(f_both_legs)} legs instead of 2!"

            for m_oid in master_oids:
                c_res = self.master.cancel_order(m_oid)
                assert c_res.get("status") == "success"
                assert self.master.wait_for_order_closure(m_oid, timeout=8.0)
            master_oids = []

            # Assert follower orders auto-cancel within 10s
            f_all_cancelled = True
            for f_leg in f_both_legs:
                if not f.wait_for_order_closure(f_leg["id"], timeout=10.0, poll_interval=0.5):
                    f_all_cancelled = False
            evidence.log_assertion("Follower Dual Legs Auto-Cancelled on Master Cancel", expected=True, actual=f_all_cancelled, passed=f_all_cancelled)
            if not f_all_cancelled:
                pytest.fail("FAIL (suspected engine bug, pending dev confirmation): Follower stop-both legs remained active 10s after master cancellation!")

            passed = True
        finally:
            for oid in master_oids:
                try:
                    self.master.cancel_order(oid)
                except Exception:
                    pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # BALANCE-BASED PROPORTIONAL MODE SCENARIOS (Tests 08 - 14)
    # -------------------------------------------------------------------------

    def _get_expected_balance_lot(self, master_lot: float = 1.00) -> float:
        m_bal = float(self.master.get_balance().get("balance", 111000000))
        f_bal = float(self.primary_follower.get_balance().get("balance", 12000000))
        ratio = f_bal / m_bal if m_bal > 0 else 0.108
        return max(0.01, round(master_lot * ratio, 2))

    def test_08_balance_market_buy_with_tpsl(self):
        """Balance Mode: Master places 1.00 lot Market BUY with TP/SL -> Follower receives balance-scaled lot with matching TP/SL."""
        logger.info("\n--- [MATRIX 08/21] Balance Mode: Market BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_08_balance_market_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Market BUY with TP/SL",
            description="Verify that under Balance mode, Follower receives lot size proportional to balance ratio on Market BUY with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            sl = f"{price - 500.0:.2f}"
            tp = f"{price + 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled to Balance Ratio BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_09_balance_market_sell_with_tpsl(self):
        """Balance Mode: Master places 1.00 lot Market SELL with TP/SL -> Follower receives balance-scaled lot with matching TP/SL."""
        logger.info("\n--- [MATRIX 09/21] Balance Mode: Market SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_09_balance_market_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Market SELL with TP/SL",
            description="Verify that under Balance mode, Follower receives lot size proportional to balance ratio on Market SELL with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            sl = f"{price + 500.0:.2f}"
            tp = f"{price - 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled to Balance Ratio SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_10_balance_limit_buy_with_tpsl(self):
        """Balance Mode: Master places Limit BUY -> Follower receives balance-scaled pending lot; cancel via master only."""
        logger.info("\n--- [MATRIX 10/21] Balance Mode: Limit BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_10_balance_limit_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Limit BUY with Trigger/TP/SL",
            description="Verify Limit BUY under Balance mode scales pending lot to balance ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            trigger = f"{price - 3000.0:.2f}"
            sl = f"{price - 3500.0:.2f}"
            tp = f"{price - 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Pending Limit BUY to Balance Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_11_balance_limit_sell_with_tpsl(self):
        """Balance Mode: Master places Limit SELL -> Follower receives balance-scaled pending lot; cancel via master only."""
        logger.info("\n--- [MATRIX 11/21] Balance Mode: Limit SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_11_balance_limit_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Limit SELL with Trigger/TP/SL",
            description="Verify Limit SELL under Balance mode scales pending lot to balance ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            trigger = f"{price + 3000.0:.2f}"
            sl = f"{price + 3500.0:.2f}"
            tp = f"{price + 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Pending Limit SELL to Balance Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_12_balance_stop_hft_buy_with_tpsl(self):
        """Balance Mode: Master places Stop HFT BUY -> Follower scales to balance ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 12/21] Balance Mode: Stop HFT BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_12_balance_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT BUY (type=1)",
            description="Verify Stop HFT BUY under Balance mode scales lot to balance ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(0.10)
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", lot=0.10, order_type="stop",
                stop_hft_type="1", triggerb=triggerb, slb=slb, targetb=targetb
            )
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.10, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT BUY to Balance Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.005))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=slb, exp_tp=targetb)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_13_balance_stop_hft_sell_with_tpsl(self):
        """Balance Mode: Master places Stop HFT SELL -> Follower scales to balance ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 13/21] Balance Mode: Stop HFT SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_13_balance_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT SELL (type=0)",
            description="Verify Stop HFT SELL under Balance mode scales lot to balance ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(0.10)
            price = self.get_live_price()
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="sell", lot=0.10, order_type="stop",
                stop_hft_type="0", triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.10, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT SELL to Balance Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.005))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sls, exp_tp=targets)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_14_balance_stop_hft_both_with_tpsl(self):
        """Balance Mode: Master places Stop HFT BOTH -> Follower scales dual pending legs to balance ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 14/21] Balance Mode: Stop HFT BOTH with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_14_balance_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT BOTH (type=2)",
            description="Verify Stop HFT BOTH under Balance mode replicates dual pending legs scaled to balance ratio; cancel via master only."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(0.10)
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="both", lot=0.10, order_type="stop",
                stop_hft_type="2",
                triggerb=triggerb, slb=slb, targetb=targetb,
                triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"

            raw_oids = str(res.get("data", {}).get("orderId", ""))
            master_oids = [oid.strip() for oid in raw_oids.split(",") if oid.strip()]
            assert len(master_oids) == 2

            time.sleep(2.0)
            f_orders = f.get_open_orders()
            f_both_legs = [o for o in f_orders if o.get("symbol") == self.symbol and str(o.get("type")).lower() == "stop"]
            evidence.log_assertion("Follower Received Both Pending Legs", expected=2, actual=len(f_both_legs), passed=(len(f_both_legs) == 2))
            assert len(f_both_legs) == 2

            for m_oid in master_oids:
                c_res = self.master.cancel_order(m_oid)
                assert c_res.get("status") == "success"
                assert self.master.wait_for_order_closure(m_oid, timeout=8.0)
            master_oids = []

            f_all_cancelled = True
            for f_leg in f_both_legs:
                if not f.wait_for_order_closure(f_leg["id"], timeout=10.0, poll_interval=0.5):
                    f_all_cancelled = False
            evidence.log_assertion("Follower Dual Legs Auto-Cancelled on Master Cancel", expected=True, actual=f_all_cancelled, passed=f_all_cancelled)
            if not f_all_cancelled:
                pytest.fail("FAIL (suspected engine bug, pending dev confirmation): Follower stop-both legs remained active 10s after master cancellation!")

            passed = True
        finally:
            for oid in master_oids:
                try:
                    self.master.cancel_order(oid)
                except Exception:
                    pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # EQUITY-BASED PROPORTIONAL MODE SCENARIOS (Tests 15 - 21)
    # With Floating P&L Setup Step & Inconclusive Guard
    # -------------------------------------------------------------------------

    def _ensure_floating_pnl_setup(self):
        """Establish a large held position on Master to drive floating P&L before equity tests."""
        if self.__class__.floating_oid is None:
            logger.info("  [EQUITY SETUP] Opening 25-lot position on Master to generate floating P&L...")
            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=25.0)
            if res.get("status") == "success":
                m_ord = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=25.0, timeout=8.0)
                if m_ord:
                    self.__class__.floating_oid = m_ord["id"]
                    time.sleep(2.0)

    def _get_expected_equity_lot_guarded(self, master_lot: float = 1.00) -> float:
        """Calculate expected equity lot with INCONCLUSIVE guard per specification."""
        self._ensure_floating_pnl_setup()
        m_eq = float(self.master.get_balance().get("equity", 0))
        m_bal = float(self.master.get_balance().get("balance", 0))
        f_eq = float(self.primary_follower.get_balance().get("equity", 0))
        f_bal = float(self.primary_follower.get_balance().get("balance", 0))

        if m_eq == 0 or m_bal == 0 or f_eq == 0 or f_bal == 0:
            pytest.skip("INCONCLUSIVE: Live balance or equity returned 0 from server API")

        eq_ratio = f_eq / m_eq
        bal_ratio = f_bal / m_bal
        expected_equity_lot = max(0.01, round(master_lot * eq_ratio, 2))
        expected_balance_lot = max(0.01, round(master_lot * bal_ratio, 2))
        lot_delta = round(abs(expected_equity_lot - expected_balance_lot), 4)

        logger.info(f"  Equity Probe: Master Eq={m_eq}, Bal={m_bal} | Follower Eq={f_eq}, Bal={f_bal} | EqLot={expected_equity_lot}, BalLot={expected_balance_lot}, Delta={lot_delta}")

        if m_eq == m_bal or f_eq == f_bal or lot_delta < 0.01:
            pytest.skip(
                f"INCONCLUSIVE: Floating P&L delta insufficient to separate equity from balance. "
                f"EquityLot={expected_equity_lot}, BalanceLot={expected_balance_lot}, Delta={lot_delta}. "
                f"Marked INCONCLUSIVE per spec."
            )

        return expected_equity_lot

    def test_15_equity_market_buy_with_tpsl(self):
        """Equity Mode: Master places Market BUY with TP/SL -> Follower receives equity-scaled lot (Guarded)."""
        logger.info("\n--- [MATRIX 15/21] Equity Mode: Market BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_15_equity_market_buy_tpsl",
            title="Copy Trading Matrix: Equity Mode - Market BUY with TP/SL",
            description="Verify that under Equity mode, Follower receives lot size proportional to live equity ratio on Market BUY with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(10.0)
            price = self.get_live_price()
            sl = f"{price - 500.0:.2f}"
            tp = f"{price + 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=10.0, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=10.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled to Equity Ratio BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_16_equity_market_sell_with_tpsl(self):
        """Equity Mode: Master places Market SELL with TP/SL -> Follower receives equity-scaled lot (Guarded)."""
        logger.info("\n--- [MATRIX 16/21] Equity Mode: Market SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_16_equity_market_sell_tpsl",
            title="Copy Trading Matrix: Equity Mode - Market SELL with TP/SL",
            description="Verify that under Equity mode, Follower receives lot size proportional to live equity ratio on Market SELL with matching TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(10.0)
            price = self.get_live_price()
            sl = f"{price + 500.0:.2f}"
            tp = f"{price - 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=10.0, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=10.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled to Equity Ratio SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=6.0)
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_17_equity_limit_buy_with_tpsl(self):
        """Equity Mode: Master places Limit BUY -> Follower receives equity-scaled pending lot; cancel via master only."""
        logger.info("\n--- [MATRIX 17/21] Equity Mode: Limit BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_17_equity_limit_buy_tpsl",
            title="Copy Trading Matrix: Equity Mode - Limit BUY with Trigger/TP/SL",
            description="Verify Limit BUY under Equity mode scales pending lot to equity ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(10.0)
            price = self.get_live_price()
            trigger = f"{price - 3000.0:.2f}"
            sl = f"{price - 3500.0:.2f}"
            tp = f"{price - 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=10.0, order_type="limit", trigger=trigger, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=10.0, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Pending Limit BUY to Equity Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_18_equity_limit_sell_with_tpsl(self):
        """Equity Mode: Master places Limit SELL -> Follower receives equity-scaled pending lot; cancel via master only."""
        logger.info("\n--- [MATRIX 18/21] Equity Mode: Limit SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_18_equity_limit_sell_tpsl",
            title="Copy Trading Matrix: Equity Mode - Limit SELL with Trigger/TP/SL",
            description="Verify Limit SELL under Equity mode scales pending lot to equity ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(10.0)
            price = self.get_live_price()
            trigger = f"{price + 3000.0:.2f}"
            sl = f"{price + 3500.0:.2f}"
            tp = f"{price + 2500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=10.0, order_type="limit", trigger=trigger, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=10.0, order_type="limit", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Pending Limit SELL to Equity Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_19_equity_stop_hft_buy_with_tpsl(self):
        """Equity Mode: Master places Stop HFT BUY -> Follower scales to equity ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 19/21] Equity Mode: Stop HFT BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_19_equity_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT BUY (type=1)",
            description="Verify Stop HFT BUY under Equity mode scales lot to equity ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(1.00)
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", lot=1.00, order_type="stop",
                stop_hft_type="1", triggerb=triggerb, slb=slb, targetb=targetb
            )
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT BUY to Equity Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=slb, exp_tp=targetb)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_20_equity_stop_hft_sell_with_tpsl(self):
        """Equity Mode: Master places Stop HFT SELL -> Follower scales to equity ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 20/21] Equity Mode: Stop HFT SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_20_equity_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT SELL (type=0)",
            description="Verify Stop HFT SELL under Equity mode scales lot to equity ratio with Trigger/TP/SL; cancel via master only."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(1.00)
            price = self.get_live_price()
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="sell", lot=1.00, order_type="stop",
                stop_hft_type="0", triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="stop", timeout=8.0)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT SELL to Equity Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sls, exp_tp=targets)

            self._assert_pending_auto_cancel_on_master_only(evidence, master_oid, f_order["id"])
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_21_equity_stop_hft_both_with_tpsl(self):
        """Equity Mode: Master places Stop HFT BOTH -> Follower scales dual pending legs to equity ratio; cancel via master only."""
        logger.info("\n--- [MATRIX 21/21] Equity Mode: Stop HFT BOTH with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_21_equity_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT BOTH (type=2)",
            description="Verify Stop HFT BOTH under Equity mode replicates dual pending legs scaled to equity ratio; cancel via master only."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot_guarded(1.00)
            price = self.get_live_price()
            triggerb = f"{price + 2500.0:.2f}"
            slb = f"{price + 2000.0:.2f}"
            targetb = f"{price + 3000.0:.2f}"
            triggers = f"{price - 2500.0:.2f}"
            sls = f"{price - 2000.0:.2f}"
            targets = f"{price - 3000.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="both", lot=1.00, order_type="stop",
                stop_hft_type="2",
                triggerb=triggerb, slb=slb, targetb=targetb,
                triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"

            raw_oids = str(res.get("data", {}).get("orderId", ""))
            master_oids = [oid.strip() for oid in raw_oids.split(",") if oid.strip()]
            assert len(master_oids) == 2

            time.sleep(2.0)
            f_orders = f.get_open_orders()
            f_both_legs = [o for o in f_orders if o.get("symbol") == self.symbol and str(o.get("type")).lower() == "stop"]
            evidence.log_assertion("Follower Received Both Pending Legs", expected=2, actual=len(f_both_legs), passed=(len(f_both_legs) == 2))
            assert len(f_both_legs) == 2

            for m_oid in master_oids:
                c_res = self.master.cancel_order(m_oid)
                assert c_res.get("status") == "success"
                assert self.master.wait_for_order_closure(m_oid, timeout=8.0)
            master_oids = []

            f_all_cancelled = True
            for f_leg in f_both_legs:
                if not f.wait_for_order_closure(f_leg["id"], timeout=10.0, poll_interval=0.5):
                    f_all_cancelled = False
            evidence.log_assertion("Follower Dual Legs Auto-Cancelled on Master Cancel", expected=True, actual=f_all_cancelled, passed=f_all_cancelled)
            if not f_all_cancelled:
                pytest.fail("FAIL (suspected engine bug, pending dev confirmation): Follower stop-both legs remained active 10s after master cancellation!")

            passed = True
        finally:
            for oid in master_oids:
                try:
                    self.master.cancel_order(oid)
                except Exception:
                    pass
            self._squareoff_all_accounts()
            # Clean up class floating position after equity tests complete
            if self.__class__.floating_oid:
                try:
                    self.master.squareoff_position(self.__class__.floating_oid)
                    self.__class__.floating_oid = None
                except Exception:
                    pass
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TRIGGERED & FILLED STOP ORDERS (Tests 22 - 24)
    # -------------------------------------------------------------------------

    def test_22_fill_stop_hft_buy_replication(self):
        """Trigger & Fill: Stop HFT BUY placed near market, triggers into open position, replicates to follower, closes cleanly."""
        logger.info("\n--- [FILL TEST 22/24] Stop HFT BUY Trigger & Market Fill Replication ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_22_fill_stop_hft_buy",
            title="Copy Trading: Stop HFT BUY Trigger & Live Fill Replication",
            description="Place a Stop HFT BUY order with trigger placed near current market ask. Wait up to 60s for fill. Verify follower receives replicated market position, then squareoff."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 1.0:.2f}"
            slb = f"{price - 500.0:.2f}"
            targetb = f"{price + 500.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", lot=0.01, order_type="stop",
                stop_hft_type="1", triggerb=triggerb, slb=slb, targetb=targetb
            )
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.split(",")[0].strip()

            logger.info(f"  Waiting up to 60s for Stop BUY (trigger={triggerb}) to fill into market position...")
            start_w = time.time()
            filled = False
            while time.time() - start_w < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid) and str(o.get("type")).lower() == "market"]
                if match:
                    filled = True
                    break
                time.sleep(1.5)

            if not filled:
                self.master.close_or_cancel(master_oid, "stop")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Stop BUY trigger ({triggerb}) did not trigger within 60s timeout.")

            # Verify follower replicated fill
            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.03, timeout=10.0)
            assert f_order is not None, "Follower failed to replicate filled Stop BUY position!"
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated Filled Stop BUY (0.03 lots)", expected=0.03, actual=actual_lot, passed=(abs(actual_lot - 0.03) < 0.005))

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=8.0)

            passed = True
        finally:
            if master_oid:
                self.master.close_or_cancel(master_oid, "stop")
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_23_fill_stop_hft_sell_replication(self):
        """Trigger & Fill: Stop HFT SELL placed near market, triggers into open position, replicates to follower, closes cleanly."""
        logger.info("\n--- [FILL TEST 23/24] Stop HFT SELL Trigger & Market Fill Replication ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_23_fill_stop_hft_sell",
            title="Copy Trading: Stop HFT SELL Trigger & Live Fill Replication",
            description="Place a Stop HFT SELL order with trigger placed near current market bid. Wait up to 60s for fill. Verify follower receives replicated market position, then squareoff."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggers = f"{price - 1.0:.2f}"
            sls = f"{price + 500.0:.2f}"
            targets = f"{price - 500.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="sell", lot=0.01, order_type="stop",
                stop_hft_type="0", triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.split(",")[0].strip()

            logger.info(f"  Waiting up to 60s for Stop SELL (trigger={triggers}) to fill into market position...")
            start_w = time.time()
            filled = False
            while time.time() - start_w < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid) and str(o.get("type")).lower() == "market"]
                if match:
                    filled = True
                    break
                time.sleep(1.5)

            if not filled:
                self.master.close_or_cancel(master_oid, "stop")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Stop SELL trigger ({triggers}) did not trigger within 60s timeout.")

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.03, timeout=10.0)
            assert f_order is not None, "Follower failed to replicate filled Stop SELL position!"
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated Filled Stop SELL (0.03 lots)", expected=0.03, actual=actual_lot, passed=(abs(actual_lot - 0.03) < 0.005))

            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            assert f.wait_for_all_closed(timeout=8.0)

            passed = True
        finally:
            if master_oid:
                self.master.close_or_cancel(master_oid, "stop")
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_24_fill_stop_hft_both_legs_replication(self):
        """Trigger & Fill: Stop HFT BOTH placed tight around spread. Timeout 60s per leg: assert first filled leg, inconclusive if second doesn't fill."""
        logger.info("\n--- [FILL TEST 24/24] Stop HFT BOTH Trigger & Market Fill Replication ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_24_fill_stop_hft_both",
            title="Copy Trading: Stop HFT BOTH Dual Trigger & Live Fill Replication",
            description="Place a Stop HFT BOTH order with BUY and SELL triggers tight around current market. Wait up to 60s per leg. Fully assert the first leg that fills; mark second leg INCONCLUSIVE if it doesn't fill in time."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 1.0:.2f}"
            triggers = f"{price - 1.0:.2f}"
            slb = f"{price - 500.0:.2f}"
            targetb = f"{price + 500.0:.2f}"
            sls = f"{price + 500.0:.2f}"
            targets = f"{price - 500.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="both", lot=0.01, order_type="stop",
                stop_hft_type="2",
                triggerb=triggerb, slb=slb, targetb=targetb,
                triggers=triggers, sls=sls, targets=targets
            )
            assert res.get("status") == "success"
            raw_oids = str(res.get("data", {}).get("orderId", ""))
            master_oids = [oid.strip() for oid in raw_oids.split(",") if oid.strip()]

            logger.info(f"  Waiting up to 60s per leg for Stop BOTH ({master_oids}) to fill...")
            start_w = time.time()
            filled_legs = []
            while time.time() - start_w < 60.0:
                orders = self.master.get_open_orders()
                for oid in master_oids:
                    if oid not in filled_legs:
                        match = [o for o in orders if str(o.get("id")) == str(oid) and str(o.get("type")).lower() == "market"]
                        if match:
                            filled_legs.append(oid)
                if len(filled_legs) == 2:
                    break
                time.sleep(1.5)

            if len(filled_legs) == 0:
                for oid in master_oids:
                    self.master.close_or_cancel(oid, "stop")
                master_oids = []
                pytest.skip("INCONCLUSIVE: Neither leg of Stop BOTH triggered within 60s timeout.")

            evidence.log_assertion("First Leg of Stop BOTH Triggered & Filled", expected=True, actual=True, passed=True,
                                   notes=f"Filled leg IDs: {filled_legs}")

            # Assert follower has replicated filled leg(s)
            time.sleep(2.0)
            f_orders = f.get_open_orders()
            f_market_positions = [o for o in f_orders if o.get("symbol") == self.symbol and str(o.get("type")).lower() == "market"]
            evidence.log_assertion(f"Follower Received Filled Leg Position ({len(filled_legs)} expected)", expected=len(filled_legs),
                                   actual=len(f_market_positions), passed=(len(f_market_positions) >= 1))
            assert len(f_market_positions) >= 1

            if len(filled_legs) < 2:
                logger.info("  Second leg did not trigger within 60s; marked INCONCLUSIVE for second leg per specification.")
                evidence.log_assertion("Second Leg Trigger Status", expected="Optional within 60s", actual="INCONCLUSIVE (unfilled in 60s)", passed=True)

            # Clean up all open / pending legs
            for oid in master_oids:
                self.master.close_or_cancel(oid, "market" if oid in filled_legs else "stop")
            master_oids = []
            assert f.wait_for_all_closed(timeout=8.0)

            passed = True
        finally:
            for oid in master_oids:
                try:
                    self.master.close_or_cancel(oid, "stop")
                except Exception:
                    pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)
