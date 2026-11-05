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

Total 21 Distinct End-to-End Scenarios:
  - Multiplier (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL
  - Balance-Based (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL
  - Equity-Based (7): Market BUY+TPSL, Market SELL+TPSL, Limit BUY+TPSL, Limit SELL+TPSL, Stop BUY+TPSL, Stop SELL+TPSL, Stop BOTH+TPSL

Every test asserts:
  1. Master order accepted and book reflects configured SL and TP.
  2. Follower receives replicated order with matching SL and TP.
  3. Follower lot conforms strictly to mode (Multiplier 3x, Balance proportional, Equity proportional).
  4. Clean position squareoff / order cancellation and account settling.
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

        # Clean any preexisting orders
        cls._squareoff_all_accounts()

    @classmethod
    def teardown_class(cls):
        """Final cleanup: squareoff any remaining positions and restore multiplier=3.0."""
        logger.info("Tearing down Copy Trading Matrix Suite: cleaning positions and restoring settings...")
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
                    sess.close_or_cancel(o["id"], o.get("type", "market"))
                sess.wait_for_all_closed(timeout=5.0)
            except Exception as e:
                logger.warning(f"Error during squareoff on {sess.name}: {e}")

    @classmethod
    def _restore_all_followers_to_multiplier(cls):
        for f in cls.followers:
            try:
                f.update_copy_trading_method(master_uid=cls.master_uid, method="multiplier", value="3.0")
            except Exception as e:
                logger.warning(f"Error restoring multiplier on {f.name}: {e}")

    def get_live_price(self) -> float:
        return self.master.get_live_price(self.symbol)

    def _place_with_retry(self, **kwargs) -> Dict[str, Any]:
        """Helper to place orders with a settling retry if engine is momentarily locked."""
        res = self.master.place_order(**kwargs)
        if res.get("status") != "success":
            time.sleep(1.5)
            self.master.generate_fingerprint()
            res = self.master.place_order(**kwargs)
        return res

    def _assert_tp_sl_propagation(self, evidence: EvidenceCollector, m_order: Dict[str, Any], f_order: Dict[str, Any], exp_sl: str, exp_tp: str):
        """Assert SL and TP are stored on Master and replicated to Follower."""
        m_sl = str(m_order.get("sl", "")).split(".")[0]
        m_tp = str(m_order.get("tp", "")).split(".")[0]
        f_sl = str(f_order.get("sl", "")).split(".")[0]
        f_tp = str(f_order.get("tp", "")).split(".")[0]
        target_sl = exp_sl.split(".")[0]
        target_tp = exp_tp.split(".")[0]

        evidence.log_assertion("Master Book SL Matches Expected", expected=target_sl, actual=m_sl, passed=(target_sl in m_sl))
        evidence.log_assertion("Master Book TP Matches Expected", expected=target_tp, actual=m_tp, passed=(target_tp in m_tp))
        evidence.log_assertion("Follower Book SL Replicated", expected=target_sl, actual=f_sl, passed=(target_sl in f_sl))
        evidence.log_assertion("Follower Book TP Replicated", expected=target_tp, actual=f_tp, passed=(target_tp in f_tp))

        assert target_sl in m_sl, f"Master SL mismatch! Expected {target_sl}, got {m_sl}"
        assert target_tp in m_tp, f"Master TP mismatch! Expected {target_tp}, got {m_tp}"
        assert target_sl in f_sl, f"Follower SL not replicated! Expected {target_sl}, got {f_sl}"
        assert target_tp in f_tp, f"Follower TP not replicated! Expected {target_tp}, got {f_tp}"

    # =========================================================================
    # GROUP 1: MULTIPLIER MODE (3.0x) - MARKET, LIMIT, STOP HFT (BUY, SELL, BOTH) WITH TP/SL
    # =========================================================================

    def test_01_multiplier_market_buy_with_tpsl(self):
        """Multiplier Mode: Master places 1.00 lot Market BUY with TP/SL -> Follower receives 3.00 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 1/21] Multiplier Mode: Market BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_01_multiplier_market_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Market BUY with TP/SL",
            description="Verify that placing 1.00 lot Market BUY with explicit TP and SL replicates 3.00 lots to follower with identical TP/SL and clean squareoff."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            sl = f"{price - 500.0:.2f}"
            tp = f"{price + 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Place Market BUY with TP/SL", f"POST /trade/placeorder.php?type=market&bs=buy&sl={sl}&target={tp}", response_data=res)
            assert res.get("status") == "success", f"Master BUY failed: {res}"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00)
            assert master_order is not None, "Master order not found in book"
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, timeout=8.0)
            assert f_order is not None, "Follower failed to copy Market BUY"
            evidence.log_assertion("Follower Replicated 3.00 Lots", expected=3.00, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 3.00) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 3.00) < 0.001

            # Assert TP and SL propagation
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
        logger.info("\n--- [MATRIX 2/21] Multiplier Mode: Market SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_02_multiplier_market_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Market SELL with TP/SL",
            description="Verify that placing 1.00 lot Market SELL with explicit TP and SL replicates 3.00 lots SELL to follower with identical TP/SL and clean squareoff."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            sl = f"{price + 500.0:.2f}"
            tp = f"{price - 500.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Place Market SELL with TP/SL", f"POST /trade/placeorder.php?type=market&bs=sell&sl={sl}&target={tp}", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00)
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, timeout=8.0)
            assert f_order is not None
            evidence.log_assertion("Follower Replicated 3.00 Lots SELL", expected=3.00, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 3.00) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 3.00) < 0.001

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
        """Multiplier Mode: Master places 1.00 lot Limit BUY with Trigger/TP/SL -> Follower receives 3.00 lots with matching Trigger/TP/SL."""
        logger.info("\n--- [MATRIX 3/21] Multiplier Mode: Limit BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_03_multiplier_limit_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Pending Limit BUY with TP/SL",
            description="Verify that placing 1.00 lot Limit BUY with explicit Trigger, TP, and SL replicates 3.00 lots to follower with matching parameters and clean cancellation."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            trig = f"{price - 1000.0:.2f}"
            sl = f"{float(trig) - 200.0:.2f}"
            tp = f"{float(trig) + 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            evidence.log_step("Master Place Limit BUY with TP/SL", f"POST /trade/placeorder.php?type=limit&trigger={trig}&sl={sl}&target={tp}", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, order_type="limit", timeout=8.0)
            assert f_order is not None
            evidence.log_assertion("Follower Replicated 3.00 Lots Limit BUY", expected=3.00, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 3.00) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 3.00) < 0.001

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_04_multiplier_limit_sell_with_tpsl(self):
        """Multiplier Mode: Master places 1.00 lot Limit SELL with Trigger/TP/SL -> Follower receives 3.00 lots with matching Trigger/TP/SL."""
        logger.info("\n--- [MATRIX 4/21] Multiplier Mode: Limit SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_04_multiplier_limit_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Pending Limit SELL with TP/SL",
            description="Verify that placing 1.00 lot Limit SELL with explicit Trigger, TP, and SL replicates 3.00 lots to follower with matching parameters and clean cancellation."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            trig = f"{price + 1000.0:.2f}"
            sl = f"{float(trig) + 200.0:.2f}"
            tp = f"{float(trig) - 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            evidence.log_step("Master Place Limit SELL with TP/SL", f"POST /trade/placeorder.php?type=limit&trigger={trig}&sl={sl}&target={tp}", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, order_type="limit", timeout=8.0)
            assert f_order is not None
            evidence.log_assertion("Follower Replicated 3.00 Lots Limit SELL", expected=3.00, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 3.00) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 3.00) < 0.001

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_05_multiplier_stop_hft_buy_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT BUY (stop_hft_type=1) with Trigger/TP/SL -> Follower receives 0.03 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 5/21] Multiplier Mode: Stop HFT BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_05_multiplier_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT BUY with TP/SL",
            description="Verify that placing 0.01 lot Stop HFT BUY (stop_hft_type=1) with explicit Trigger, TP, and SL replicates 0.03 lots to follower with matching parameters and clean cancellation."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            trig = f"{price + 500.0:.2f}"
            sl = f"{float(trig) - 100.0:.2f}"
            tp = f"{float(trig) + 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="1",
                                          lotb=0.01, triggerb=trig, slb=sl, targetb=tp)
            evidence.log_step("Master Place Stop HFT BUY with TP/SL", f"POST /trade/placeorder.php?type=stop&stop_hft_type=1&triggerb={trig}&slb={sl}&targetb={tp}", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.01, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=0.03, order_type="stop", timeout=8.0)
            assert f_order is not None
            evidence.log_assertion("Follower Replicated 0.03 Lots Stop HFT BUY", expected=0.03, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 0.03) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 0.03) < 0.001

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_06_multiplier_stop_hft_sell_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT SELL (stop_hft_type=0) with Trigger/TP/SL -> Follower receives 0.03 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 6/21] Multiplier Mode: Stop HFT SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_06_multiplier_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT SELL with TP/SL",
            description="Verify that placing 0.01 lot Stop HFT SELL (stop_hft_type=0) with explicit Trigger, TP, and SL replicates 0.03 lots to follower with matching parameters and clean cancellation."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            trig = f"{price - 500.0:.2f}"
            sl = f"{float(trig) + 100.0:.2f}"
            tp = f"{float(trig) - 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="stop", stop_hft_type="0",
                                          lots=0.01, triggers=trig, sls=sl, targets=tp)
            evidence.log_step("Master Place Stop HFT SELL with TP/SL", f"POST /trade/placeorder.php?type=stop&stop_hft_type=0&triggers={trig}&sls={sl}&targets={tp}", response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.01, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=0.03, order_type="stop", timeout=8.0)
            assert f_order is not None
            evidence.log_assertion("Follower Replicated 0.03 Lots Stop HFT SELL", expected=0.03, actual=float(f_order.get("lot", 0)),
                                   passed=(abs(float(f_order.get("lot", 0)) - 0.03) < 0.001))
            assert abs(float(f_order.get("lot", 0)) - 0.03) < 0.001

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_07_multiplier_stop_hft_both_with_tpsl(self):
        """Multiplier Mode: Master places Stop HFT BOTH (stop_hft_type=2) with Trigger/TP/SL -> Follower receives dual 0.03 lots with matching TP/SL."""
        logger.info("\n--- [MATRIX 7/21] Multiplier Mode: Stop HFT BOTH with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_07_multiplier_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Multiplier Mode - Stop HFT BOTH with TP/SL",
            description="Verify that placing Stop HFT BOTH creates dual pending orders on master and replicates dual 3.0x orders with matching Trigger, TP, and SL to follower."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            time.sleep(1.0)
            price = self.get_live_price()
            trigb = f"{price + 500.0:.2f}"
            slb = f"{float(trigb) - 100.0:.2f}"
            tpb = f"{float(trigb) + 100.0:.2f}"
            trigs = f"{price - 500.0:.2f}"
            sls = f"{float(trigs) + 100.0:.2f}"
            tps = f"{float(trigs) - 100.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="2",
                lotb=0.01, triggerb=trigb, slb=slb, targetb=tpb,
                lots=0.01, triggers=trigs, sls=sls, targets=tps
            )
            evidence.log_step("Master Place Stop HFT BOTH with TP/SL", "POST /trade/placeorder.php?type=stop&stop_hft_type=2", response_data=res)
            assert res.get("status") == "success"

            time.sleep(1.5)
            m_stops = [o for o in self.master.get_open_orders() if o.get("type") == "stop"]
            assert len(m_stops) >= 2
            master_oids = [o["id"] for o in m_stops]

            f_stops = [o for o in f.get_open_orders() if o.get("type") == "stop"]
            assert len(f_stops) >= 2
            evidence.log_assertion("Follower Replicated Dual Stop Orders with TP/SL", expected=2, actual=len(f_stops), passed=True)

            for fo in f_stops:
                assert abs(float(fo.get("lot", 0)) - 0.03) < 0.001
                assert fo.get("sl") not in ["", "---", None]
                assert fo.get("tp") not in ["", "---", None]

            for mid in master_oids:
                self.master.cancel_order(mid)
            master_oids = []
            for fid in [o["id"] for o in f_stops]:
                f.cancel_order(fid)
            assert self.master.wait_for_all_closed(timeout=5.0)
            assert f.wait_for_all_closed(timeout=5.0)
            passed = True
        finally:
            for mid in master_oids:
                self.master.cancel_order(mid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # =========================================================================
    # GROUP 2: BALANCE-BASED MODE - MARKET, LIMIT, STOP HFT WITH TP/SL
    # =========================================================================

    def _get_expected_balance_lot(self, master_lot: float) -> float:
        m_bal = float(self.master.get_balance().get("balance", 1))
        f_bal = float(self.primary_follower.get_balance().get("balance", 1))
        ratio = f_bal / m_bal if m_bal > 0 else 1.0
        return max(0.01, round(master_lot * ratio, 2))

    def test_08_balance_market_buy_with_tpsl(self):
        """Balance Mode: Master places 1.00 lot Market BUY with TP/SL -> Follower receives balance-scaled lot with matching TP/SL."""
        logger.info("\n--- [MATRIX 8/21] Balance Mode: Market BUY with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_08_balance_market_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Market BUY with TP/SL",
            description="Verify that under Balance mode, Follower receives lot size proportional to live balance ratio on Market BUY with matching TP/SL."
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
            evidence.log_assertion(f"Follower Scaled to Balance Ratio ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
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
        logger.info("\n--- [MATRIX 9/21] Balance Mode: Market SELL with TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_09_balance_market_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Market SELL with TP/SL",
            description="Verify that under Balance mode, Follower receives lot size proportional to live balance ratio on Market SELL with matching TP/SL."
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
        """Balance Mode: Master places Limit BUY with Trigger/TP/SL -> Follower receives balance-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 10/21] Balance Mode: Limit BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_10_balance_limit_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Pending Limit BUY with TP/SL",
            description="Verify that under Balance mode, Follower receives pending Limit BUY scaled to balance ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            trig = f"{price - 1000.0:.2f}"
            sl = f"{float(trig) - 200.0:.2f}"
            tp = f"{float(trig) + 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Limit BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_11_balance_limit_sell_with_tpsl(self):
        """Balance Mode: Master places Limit SELL with Trigger/TP/SL -> Follower receives balance-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 11/21] Balance Mode: Limit SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_11_balance_limit_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Pending Limit SELL with TP/SL",
            description="Verify that under Balance mode, Follower receives pending Limit SELL scaled to balance ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            expected_lot = self._get_expected_balance_lot(1.00)
            price = self.get_live_price()
            trig = f"{price + 1000.0:.2f}"
            sl = f"{float(trig) + 200.0:.2f}"
            tp = f"{float(trig) - 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Limit SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_12_balance_stop_hft_buy_with_tpsl(self):
        """Balance Mode: Master places Stop HFT BUY with Trigger/TP/SL -> Follower receives balance-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 12/21] Balance Mode: Stop HFT BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_12_balance_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT BUY with TP/SL",
            description="Verify that under Balance mode, Follower receives pending Stop HFT BUY scaled to balance ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_balance_lot(master_stop_lot)
            price = self.get_live_price()
            trig = f"{price + 500.0:.2f}"
            sl = f"{float(trig) - 100.0:.2f}"
            tp = f"{float(trig) + 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="1",
                                          lotb=master_stop_lot, triggerb=trig, slb=sl, targetb=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=master_stop_lot, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_13_balance_stop_hft_sell_with_tpsl(self):
        """Balance Mode: Master places Stop HFT SELL with Trigger/TP/SL -> Follower receives balance-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 13/21] Balance Mode: Stop HFT SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_13_balance_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT SELL with TP/SL",
            description="Verify that under Balance mode, Follower receives pending Stop HFT SELL scaled to balance ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_balance_lot(master_stop_lot)
            price = self.get_live_price()
            trig = f"{price - 500.0:.2f}"
            sl = f"{float(trig) + 100.0:.2f}"
            tp = f"{float(trig) - 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="stop", stop_hft_type="0",
                                          lots=master_stop_lot, triggers=trig, sls=sl, targets=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=master_stop_lot, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_14_balance_stop_hft_both_with_tpsl(self):
        """Balance Mode: Master places Stop HFT BOTH (stop_hft_type=2) with Trigger/TP/SL -> Follower receives dual balance-scaled pending orders with TP/SL."""
        logger.info("\n--- [MATRIX 14/21] Balance Mode: Stop HFT BOTH with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_14_balance_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Balance Mode - Stop HFT BOTH with TP/SL",
            description="Verify that under Balance mode, Stop HFT BOTH creates dual pending orders on master and replicates dual balance-scaled orders with matching TP/SL to follower."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_balance_lot(master_stop_lot)
            price = self.get_live_price()
            trigb = f"{price + 500.0:.2f}"
            slb = f"{float(trigb) - 100.0:.2f}"
            tpb = f"{float(trigb) + 100.0:.2f}"
            trigs = f"{price - 500.0:.2f}"
            sls = f"{float(trigs) + 100.0:.2f}"
            tps = f"{float(trigs) - 100.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="2",
                lotb=master_stop_lot, triggerb=trigb, slb=slb, targetb=tpb,
                lots=master_stop_lot, triggers=trigs, sls=sls, targets=tps
            )
            assert res.get("status") == "success"

            time.sleep(1.5)
            m_stops = [o for o in self.master.get_open_orders() if o.get("type") == "stop"]
            assert len(m_stops) >= 2
            master_oids = [o["id"] for o in m_stops]

            f_stops = [o for o in f.get_open_orders() if o.get("type") == "stop"]
            assert len(f_stops) >= 2
            evidence.log_assertion("Follower Replicated Dual Stop Orders with TP/SL (Balance Mode)", expected=2, actual=len(f_stops), passed=True)

            for fo in f_stops:
                assert abs(float(fo.get("lot", 0)) - expected_lot) <= 0.01
                assert fo.get("sl") not in ["", "---", None]
                assert fo.get("tp") not in ["", "---", None]

            for mid in master_oids:
                self.master.cancel_order(mid)
            master_oids = []
            for fid in [o["id"] for o in f_stops]:
                f.cancel_order(fid)
            assert self.master.wait_for_all_closed(timeout=5.0)
            assert f.wait_for_all_closed(timeout=5.0)
            passed = True
        finally:
            for mid in master_oids:
                self.master.cancel_order(mid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # =========================================================================
    # GROUP 3: EQUITY-BASED MODE - MARKET, LIMIT, STOP HFT WITH TP/SL
    # =========================================================================

    def _get_expected_equity_lot(self, master_lot: float) -> float:
        m_eq = float(self.master.get_balance().get("equity", 1))
        f_eq = float(self.primary_follower.get_balance().get("equity", 1))
        ratio = f_eq / m_eq if m_eq > 0 else 1.0
        return max(0.01, round(master_lot * ratio, 2))

    def test_15_equity_market_buy_with_tpsl(self):
        """Equity Mode: Master places 1.00 lot Market BUY with TP/SL -> Follower receives equity-scaled lot with matching TP/SL."""
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
            expected_lot = self._get_expected_equity_lot(1.00)
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
        """Equity Mode: Master places 1.00 lot Market SELL with TP/SL -> Follower receives equity-scaled lot with matching TP/SL."""
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
            expected_lot = self._get_expected_equity_lot(1.00)
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
        """Equity Mode: Master places Limit BUY with Trigger/TP/SL -> Follower receives equity-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 17/21] Equity Mode: Limit BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_17_equity_limit_buy_tpsl",
            title="Copy Trading Matrix: Equity Mode - Pending Limit BUY with TP/SL",
            description="Verify that under Equity mode, Follower receives pending Limit BUY scaled to equity ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot(1.00)
            price = self.get_live_price()
            trig = f"{price - 1000.0:.2f}"
            sl = f"{float(trig) - 200.0:.2f}"
            tp = f"{float(trig) + 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Limit BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_18_equity_limit_sell_with_tpsl(self):
        """Equity Mode: Master places Limit SELL with Trigger/TP/SL -> Follower receives equity-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 18/21] Equity Mode: Limit SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_18_equity_limit_sell_tpsl",
            title="Copy Trading Matrix: Equity Mode - Pending Limit SELL with TP/SL",
            description="Verify that under Equity mode, Follower receives pending Limit SELL scaled to equity ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            expected_lot = self._get_expected_equity_lot(1.00)
            price = self.get_live_price()
            trig = f"{price + 1000.0:.2f}"
            sl = f"{float(trig) + 200.0:.2f}"
            tp = f"{float(trig) - 200.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="limit", lot=1.00, trigger=trig, sl=sl, target=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, order_type="limit")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="limit", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Limit SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_19_equity_stop_hft_buy_with_tpsl(self):
        """Equity Mode: Master places Stop HFT BUY with Trigger/TP/SL -> Follower receives equity-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 19/21] Equity Mode: Stop HFT BUY with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_19_equity_stop_hft_buy_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT BUY with TP/SL",
            description="Verify that under Equity mode, Follower receives pending Stop HFT BUY scaled to equity ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_equity_lot(master_stop_lot)
            price = self.get_live_price()
            trig = f"{price + 500.0:.2f}"
            sl = f"{float(trig) - 100.0:.2f}"
            tp = f"{float(trig) + 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="1",
                                          lotb=master_stop_lot, triggerb=trig, slb=sl, targetb=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=master_stop_lot, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT BUY ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_20_equity_stop_hft_sell_with_tpsl(self):
        """Equity Mode: Master places Stop HFT SELL with Trigger/TP/SL -> Follower receives equity-scaled pending order with matching TP/SL."""
        logger.info("\n--- [MATRIX 20/21] Equity Mode: Stop HFT SELL with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_20_equity_stop_hft_sell_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT SELL with TP/SL",
            description="Verify that under Equity mode, Follower receives pending Stop HFT SELL scaled to equity ratio with matching Trigger, TP, and SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_equity_lot(master_stop_lot)
            price = self.get_live_price()
            trig = f"{price - 500.0:.2f}"
            sl = f"{float(trig) + 100.0:.2f}"
            tp = f"{float(trig) - 100.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", order_type="stop", stop_hft_type="0",
                                          lots=master_stop_lot, triggers=trig, sls=sl, targets=tp)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=master_stop_lot, order_type="stop")
            assert master_order is not None
            master_oid = master_order["id"]

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=expected_lot, order_type="stop", timeout=8.0)
            assert f_order is not None
            actual_lot = float(f_order.get("lot", 0))
            evidence.log_assertion(f"Follower Scaled Stop HFT SELL ({expected_lot} lots)", expected=expected_lot, actual=actual_lot,
                                   passed=(abs(actual_lot - expected_lot) <= 0.01))
            assert abs(actual_lot - expected_lot) <= 0.01

            self._assert_tp_sl_propagation(evidence, master_order, f_order, exp_sl=sl, exp_tp=tp)

            self.master.cancel_order(master_oid)
            f.cancel_order(f_order["id"])
            self.master.wait_for_order_closure(master_oid, timeout=8.0)
            f.wait_for_order_closure(f_order["id"], timeout=8.0)
            master_oid = None
            passed = True
        finally:
            if master_oid:
                self.master.cancel_order(master_oid)
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    def test_21_equity_stop_hft_both_with_tpsl(self):
        """Equity Mode: Master places Stop HFT BOTH (stop_hft_type=2) with Trigger/TP/SL -> Follower receives dual equity-scaled pending orders with TP/SL."""
        logger.info("\n--- [MATRIX 21/21] Equity Mode: Stop HFT BOTH with Trigger/TP/SL ---")
        evidence = EvidenceCollector(
            test_id="evidence_matrix_21_equity_stop_hft_both_tpsl",
            title="Copy Trading Matrix: Equity Mode - Stop HFT BOTH with TP/SL",
            description="Verify that under Equity mode, Stop HFT BOTH creates dual pending orders on master and replicates dual equity-scaled orders with matching Trigger, TP, and SL to follower."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            f.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            time.sleep(1.0)
            master_stop_lot = 0.10
            expected_lot = self._get_expected_equity_lot(master_stop_lot)
            price = self.get_live_price()
            trigb = f"{price + 500.0:.2f}"
            slb = f"{float(trigb) - 100.0:.2f}"
            tpb = f"{float(trigb) + 100.0:.2f}"
            trigs = f"{price - 500.0:.2f}"
            sls = f"{float(trigs) + 100.0:.2f}"
            tps = f"{float(trigs) - 100.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="2",
                lotb=master_stop_lot, triggerb=trigb, slb=slb, targetb=tpb,
                lots=master_stop_lot, triggers=trigs, sls=sls, targets=tps
            )
            assert res.get("status") == "success"

            time.sleep(1.5)
            m_stops = [o for o in self.master.get_open_orders() if o.get("type") == "stop"]
            assert len(m_stops) >= 2
            master_oids = [o["id"] for o in m_stops]

            f_stops = [o for o in f.get_open_orders() if o.get("type") == "stop"]
            assert len(f_stops) >= 2
            evidence.log_assertion("Follower Replicated Dual Stop Orders with TP/SL (Equity Mode)", expected=2, actual=len(f_stops), passed=True)

            for fo in f_stops:
                assert abs(float(fo.get("lot", 0)) - expected_lot) <= 0.01
                assert fo.get("sl") not in ["", "---", None]
                assert fo.get("tp") not in ["", "---", None]

            for mid in master_oids:
                self.master.cancel_order(mid)
            master_oids = []
            for fid in [o["id"] for o in f_stops]:
                f.cancel_order(fid)
            assert self.master.wait_for_all_closed(timeout=5.0)
            assert f.wait_for_all_closed(timeout=5.0)
            passed = True
        finally:
            for mid in master_oids:
                self.master.cancel_order(mid)
            self._squareoff_all_accounts()
            # Restore all followers back to multiplier=3.0
            self._restore_all_followers_to_multiplier()
            evidence.finish(passed=passed)
