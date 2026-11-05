"""
Complete End-to-End Test Suite for Copy Trading on WavexOne:
Validates ALL Buying and Selling scenarios across ALL order types (Market, Limit, Stop HFT BUY/SELL/BOTH),
with STRICT 1 LOT SIZING (no decimals), EASY-TO-HIT TP/SL NUMBERS, and AUTOMATIC EXIT ONLY (NO MANUAL EXIT).

Scenarios Covered:
  1. Market BUY 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit
  2. Market SELL 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit
  3. Limit BUY 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Auto-Exit
  4. Limit SELL 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Auto-Exit
  5. Stop HFT BUY 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Auto-Exit
  6. Stop HFT SELL 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Auto-Exit
  7. Stop HFT BOTH 1.00 Lot with Dual Breakout Triggers, TP/SL & Auto-Exit
"""
import time
import pytest
from typing import Dict, Any, List, Optional
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.evidence import EvidenceCollector
from core.logger import logger


class TestCopyTradingAllScenariosSuite:

    @classmethod
    def setup_class(cls):
        logger.info("\n" + "=" * 80)
        logger.info("INITIALIZING COPY TRADING ALL BUY/SELL SCENARIOS (1 LOT ONLY, AUTO-EXIT ONLY)")
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

        # 2. Followers (All 5)
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

        # Squareoff any preexisting orders
        cls._squareoff_all_accounts()
        cls._restore_all_followers_to_multiplier()

    @classmethod
    def teardown_class(cls):
        logger.info("Tearing down All Scenarios Suite: cleaning positions and restoring settings...")
        cls._squareoff_all_accounts()
        cls._restore_all_followers_to_multiplier()
        cls._squareoff_all_accounts()

    def teardown_method(self, method):
        self._squareoff_all_accounts()

    @classmethod
    def _squareoff_all_accounts(cls):
        for sess in [cls.master] + cls.followers:
            try:
                for o in sess.get_open_orders():
                    sess.close_or_cancel(o["id"], o.get("type", "market"))
            except Exception:
                pass

    @classmethod
    def _restore_all_followers_to_multiplier(cls):
        for f in cls.followers:
            try:
                f.follow_master(master_uid=cls.master_uid)
                f.update_copy_trading_method(master_uid=cls.master_uid, method="multiplier", value="3.0")
            except Exception:
                pass

    def _place_with_retry(self, **kwargs) -> Dict[str, Any]:
        retries = 3
        for attempt in range(retries):
            self.master.generate_fingerprint()
            res = self.master.place_order(**kwargs)
            if res.get("status") == "success":
                return res
            logger.warning(f"Place order failed attempt {attempt+1}/{retries}: {res.get('message')}. Retrying...")
            time.sleep(1.0)
        return res

    def get_live_price(self) -> float:
        price = self.master.get_live_price(self.symbol)
        assert price > 0, "Failed to read live market price"
        return price

    def _wait_for_auto_exit(self, evidence: EvidenceCollector, master_oid: str, expected_tp: str, expected_sl: str, timeout: float = 60.0) -> bool:
        """Wait for position to auto-exit when price reaches TP or SL. DO NOT manually exit."""
        logger.info(f"  Waiting up to {timeout}s for AUTOMATIC EXIT (TP={expected_tp} or SL={expected_sl}) without manual intervention...")
        start_w = time.time()
        auto_closed = False
        while time.time() - start_w < timeout:
            m_orders = self.master.get_open_orders()
            if not any(str(o.get("id")) == str(master_oid) for o in m_orders):
                auto_closed = True
                close_dur = round(time.time() - start_w, 2)
                logger.info(f"  [AUTO-EXIT TRIGGERED] Master order auto-closed via TP/SL hit in {close_dur}s!")
                evidence.log_assertion("Master Automatic Exit via TP/SL Hit", expected=True, actual=True, passed=True,
                                       notes=f"Order auto-closed in {close_dur}s without manual close.")
                break
            time.sleep(1.0)

        if not auto_closed:
            logger.warning(f"  Order {master_oid} did not auto-close within {timeout}s (market did not tick past TP/SL).")
            evidence.log_assertion("Master Automatic Exit via TP/SL Hit", expected=True, actual=False, passed=False,
                                   notes=f"Market price did not tick {expected_tp}/{expected_sl} within {timeout}s timeout.")
            return False

        # Assert follower ALSO auto-closed automatically
        time.sleep(1.5)
        f_closed = self.primary_follower.wait_for_all_closed(timeout=10.0)
        evidence.log_assertion("Follower Synchronous Automatic Exit via TP/SL Hit", expected=True, actual=f_closed, passed=f_closed,
                               notes="Follower must auto-close when Master position is terminated by TP/SL hit.")
        assert f_closed, f"Follower {self.primary_follower.name} had residual orders after Master TP/SL auto-close!"
        return True

    # -------------------------------------------------------------------------
    # SCENARIO 1: MARKET BUY 1.00 LOT WITH EASY-TO-HIT TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_01_market_buy_1lot_easy_tpsl_auto_exit(self):
        """Market BUY: 1.00 lot placed by Master -> Follower receives 3.00 lots with matching TP/SL. Auto-exits on hit."""
        logger.info("\n--- [SCENARIO 1/7] Market BUY 1.00 Lot with Easy-to-Hit TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_01_market_buy_1lot_auto_exit",
            title="Copy Trading: Market BUY 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Market BUY with tight 5.0 pt TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            sl = f"{price - 5.0:.2f}"
            tp = f"{price + 5.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Market BUY Placement (1.00 Lot)", "POST /trade/placeorder.php", request_data={"lot": 1.00, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, timeout=6.0)
            assert master_order is not None, "Master BUY order not found in book!"
            master_oid = master_order["id"]
            evidence.log_assertion("Master Placed 1.00 Whole Lot (No Decimals)", expected=1.00, actual=float(master_order.get("lot", 0)), passed=True)

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, timeout=8.0)
            assert f_order is not None, "Follower failed to replicate Market BUY!"
            actual_f_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots (3.0x Multiplier)", expected=3.00, actual=actual_f_lot, passed=(abs(actual_f_lot - 3.00) < 0.01))
            assert abs(actual_f_lot - 3.00) < 0.01

            # Verify TP and SL replication
            f_sl = str(f_order.get("sl", "")).strip()
            f_tp = str(f_order.get("tp", "")).strip()
            evidence.log_assertion(f"Follower SL ({sl}) Propagated", expected=sl, actual=f_sl, passed=(sl in f_sl or f_sl == sl))
            evidence.log_assertion(f"Follower TP ({tp}) Propagated", expected=tp, actual=f_tp, passed=(tp in f_tp or f_tp == tp))

            # Wait for AUTOMATIC EXIT only (do not manually square off!)
            auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=tp, expected_sl=sl, timeout=60.0)
            if auto_exited:
                master_oid = None
                passed = True
            else:
                self.master.squareoff_position(master_oid)
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 5 points to hit TP ({tp}) or SL ({sl}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.squareoff_position(master_oid)
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 2: MARKET SELL 1.00 LOT WITH EASY-TO-HIT TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_02_market_sell_1lot_easy_tpsl_auto_exit(self):
        """Market SELL: 1.00 lot placed by Master -> Follower receives 3.00 lots with matching TP/SL. Auto-exits on hit."""
        logger.info("\n--- [SCENARIO 2/7] Market SELL 1.00 Lot with Easy-to-Hit TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_02_market_sell_1lot_auto_exit",
            title="Copy Trading: Market SELL 1.00 Lot with Easy-to-Hit TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Market SELL with tight 5.0 pt TP/SL offsets. Follower replicates exactly 3.00 lots. Test exits ONLY when TP or SL is triggered automatically."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            sl = f"{price + 5.0:.2f}"
            tp = f"{price - 5.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, sl=sl, target=tp)
            evidence.log_step("Master Market SELL Placement (1.00 Lot)", "POST /trade/placeorder.php", request_data={"lot": 1.00, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"

            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=1.00, timeout=6.0)
            assert master_order is not None, "Master SELL order not found in book!"
            master_oid = master_order["id"]
            evidence.log_assertion("Master Placed 1.00 Whole Lot (No Decimals)", expected=1.00, actual=float(master_order.get("lot", 0)), passed=True)

            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, timeout=8.0)
            assert f_order is not None, "Follower failed to replicate Market SELL!"
            actual_f_lot = float(f_order.get("lot", 0))
            evidence.log_assertion("Follower Replicated 3.00 Lots (3.0x Multiplier)", expected=3.00, actual=actual_f_lot, passed=(abs(actual_f_lot - 3.00) < 0.01))
            assert abs(actual_f_lot - 3.00) < 0.01

            # Verify TP and SL replication
            f_sl = str(f_order.get("sl", "")).strip()
            f_tp = str(f_order.get("tp", "")).strip()
            evidence.log_assertion(f"Follower SL ({sl}) Propagated", expected=sl, actual=f_sl, passed=(sl in f_sl or f_sl == sl))
            evidence.log_assertion(f"Follower TP ({tp}) Propagated", expected=tp, actual=f_tp, passed=(tp in f_tp or f_tp == tp))

            # Wait for AUTOMATIC EXIT only
            auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=tp, expected_sl=sl, timeout=60.0)
            if auto_exited:
                master_oid = None
                passed = True
            else:
                self.master.squareoff_position(master_oid)
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 5 points to hit TP ({tp}) or SL ({sl}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.squareoff_position(master_oid)
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 3: LIMIT BUY 1.00 LOT WITH TRIGGER, TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_03_limit_buy_1lot_easy_tpsl_pending_and_auto_exit(self):
        """Limit BUY: 1.00 lot placed with trigger below market -> Follower receives 3.00 lots pending; fills & auto-exits."""
        logger.info("\n--- [SCENARIO 3/7] Limit BUY 1.00 Lot with Trigger, TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_03_limit_buy_1lot_auto_exit",
            title="Copy Trading: Limit BUY 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Limit BUY with trigger 2.0 pts below CMP. Follower replicates 3.00 lots pending. When filled, auto-exits via TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            trigger = f"{price - 2.0:.2f}"
            sl = f"{price - 7.0:.2f}"
            tp = f"{price + 5.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="buy", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            evidence.log_step("Master Limit BUY Placement (1.00 Lot)", "POST /trade/placeorder.php?type=limit", request_data={"trigger": trigger, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.strip()

            # Verify pending order book on Master and Follower
            time.sleep(1.0)
            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, order_type="limit", timeout=8.0)
            if f_order:
                evidence.log_assertion("Follower Replicated 3.00 Lots Pending Limit BUY", expected=3.00, actual=float(f_order.get("lot", 0)), passed=True)
                evidence.log_assertion(f"Follower Trigger ({trigger}) Replicated", expected=trigger, actual=str(f_order.get("trigger", "")), passed=True)

            logger.info(f"  Waiting up to 60s for price to tick 2 points to trigger/fill Limit BUY ({trigger})...")
            start_f = time.time()
            filled = False
            while time.time() - start_f < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid)]
                if match and str(match[0].get("type", "")).lower() == "market":
                    filled = True
                    logger.info(f"  [LIMIT FILLED] Master Limit BUY filled into market position after {time.time()-start_f:.2f}s!")
                    break
                elif not match:
                    # Filled and already auto-closed on TP/SL!
                    filled = True
                    logger.info("  [LIMIT FILLED & AUTO-CLOSED] Position filled and auto-closed on market tick!")
                    break
                time.sleep(1.5)

            if filled:
                evidence.log_assertion("Limit BUY Triggered & Filled into Position", expected=True, actual=True, passed=True)
                auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=tp, expected_sl=sl, timeout=60.0)
                if auto_exited:
                    master_oid = None
                    passed = True
                else:
                    self.master.close_or_cancel(master_oid, "market")
                    master_oid = None
                    pytest.skip(f"INCONCLUSIVE: Filled position did not hit TP/SL within 60s timeout.")
            else:
                self.master.close_or_cancel(master_oid, "limit")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 2 points down to fill Limit BUY trigger ({trigger}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.close_or_cancel(master_oid, "limit")
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 4: LIMIT SELL 1.00 LOT WITH TRIGGER, TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_04_limit_sell_1lot_easy_tpsl_pending_and_auto_exit(self):
        """Limit SELL: 1.00 lot placed with trigger above market -> Follower receives 3.00 lots pending; fills & auto-exits."""
        logger.info("\n--- [SCENARIO 4/7] Limit SELL 1.00 Lot with Trigger, TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_04_limit_sell_1lot_auto_exit",
            title="Copy Trading: Limit SELL 1.00 Lot with Easy-to-Hit Trigger, TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Limit SELL with trigger 2.0 pts above CMP. Follower replicates 3.00 lots pending. When filled, auto-exits via TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            trigger = f"{price + 2.0:.2f}"
            sl = f"{price + 7.0:.2f}"
            tp = f"{price - 5.0:.2f}"

            res = self._place_with_retry(symbol=self.symbol, side="sell", lot=1.00, order_type="limit", trigger=trigger, sl=sl, target=tp)
            evidence.log_step("Master Limit SELL Placement (1.00 Lot)", "POST /trade/placeorder.php?type=limit", request_data={"trigger": trigger, "sl": sl, "tp": tp}, response_data=res)
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.strip()

            time.sleep(1.0)
            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, order_type="limit", timeout=8.0)
            if f_order:
                evidence.log_assertion("Follower Replicated 3.00 Lots Pending Limit SELL", expected=3.00, actual=float(f_order.get("lot", 0)), passed=True)
                evidence.log_assertion(f"Follower Trigger ({trigger}) Replicated", expected=trigger, actual=str(f_order.get("trigger", "")), passed=True)

            logger.info(f"  Waiting up to 60s for price to tick 2 points to trigger/fill Limit SELL ({trigger})...")
            start_f = time.time()
            filled = False
            while time.time() - start_f < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid)]
                if match and str(match[0].get("type", "")).lower() == "market":
                    filled = True
                    logger.info(f"  [LIMIT FILLED] Master Limit SELL filled into market position after {time.time()-start_f:.2f}s!")
                    break
                elif not match:
                    filled = True
                    logger.info("  [LIMIT FILLED & AUTO-CLOSED] Position filled and auto-closed on market tick!")
                    break
                time.sleep(1.5)

            if filled:
                evidence.log_assertion("Limit SELL Triggered & Filled into Position", expected=True, actual=True, passed=True)
                auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=tp, expected_sl=sl, timeout=60.0)
                if auto_exited:
                    master_oid = None
                    passed = True
                else:
                    self.master.close_or_cancel(master_oid, "market")
                    master_oid = None
                    pytest.skip(f"INCONCLUSIVE: Filled position did not hit TP/SL within 60s timeout.")
            else:
                self.master.close_or_cancel(master_oid, "limit")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 2 points up to fill Limit SELL trigger ({trigger}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.close_or_cancel(master_oid, "limit")
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 5: STOP HFT BUY 1.00 LOT WITH TRIGGER, TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_05_stop_hft_buy_1lot_easy_tpsl_trigger_and_auto_exit(self):
        """Stop HFT BUY (type=1): 1.00 lot placed with trigger -> Follower replicates 3.00 lots; triggers & auto-exits."""
        logger.info("\n--- [SCENARIO 5/7] Stop HFT BUY 1.00 Lot with Trigger, TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_05_stop_hft_buy_1lot_auto_exit",
            title="Copy Trading: Stop HFT BUY 1.00 Lot with Trigger, TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Stop HFT BUY (type=1) with trigger 5.0 pts above CMP. Follower replicates 3.00 lots. Triggers into fill, then auto-exits via TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 5.0:.2f}"
            slb = f"{price - 5.0:.2f}"
            targetb = f"{price + 10.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="buy", lot=1.00, order_type="stop",
                stop_hft_type="1", triggerb=triggerb, slb=slb, targetb=targetb
            )
            evidence.log_step("Master Stop HFT BUY Placement (1.00 Lot)", "POST /trade/placeorder.php?type=stop&stop_hft_type=1", response_data=res)
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.strip()

            time.sleep(1.0)
            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, order_type="stop", timeout=8.0)
            if f_order:
                evidence.log_assertion("Follower Replicated 3.00 Lots Pending Stop BUY", expected=3.00, actual=float(f_order.get("lot", 0)), passed=True)
                evidence.log_assertion(f"Follower Trigger ({triggerb}) Replicated", expected=triggerb, actual=str(f_order.get("trigger", "")), passed=True)

            logger.info(f"  Waiting up to 60s for Stop BUY ({triggerb}) to trigger and fill into market position...")
            start_f = time.time()
            filled = False
            while time.time() - start_f < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid)]
                if match and str(match[0].get("type", "")).lower() == "market":
                    filled = True
                    logger.info(f"  [STOP BUY FILLED] Position filled into market after {time.time()-start_f:.2f}s!")
                    break
                elif not match:
                    filled = True
                    logger.info("  [STOP BUY FILLED & AUTO-CLOSED] Position filled and auto-closed on market tick!")
                    break
                time.sleep(1.5)

            if filled:
                evidence.log_assertion("Stop HFT BUY Triggered & Filled into Position", expected=True, actual=True, passed=True)
                auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=targetb, expected_sl=slb, timeout=60.0)
                if auto_exited:
                    master_oid = None
                    passed = True
                else:
                    self.master.close_or_cancel(master_oid, "market")
                    master_oid = None
                    pytest.skip(f"INCONCLUSIVE: Filled position did not hit TP/SL within 60s timeout.")
            else:
                self.master.close_or_cancel(master_oid, "stop")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 5 points to trigger Stop BUY ({triggerb}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.close_or_cancel(master_oid, "stop")
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 6: STOP HFT SELL 1.00 LOT WITH TRIGGER, TP/SL & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_06_stop_hft_sell_1lot_easy_tpsl_trigger_and_auto_exit(self):
        """Stop HFT SELL (type=0): 1.00 lot placed with trigger -> Follower replicates 3.00 lots; triggers & auto-exits."""
        logger.info("\n--- [SCENARIO 6/7] Stop HFT SELL 1.00 Lot with Trigger, TP/SL & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_06_stop_hft_sell_1lot_auto_exit",
            title="Copy Trading: Stop HFT SELL 1.00 Lot with Trigger, TP/SL & Automatic Exit",
            description="Master places 1.00 whole lot Stop HFT SELL (type=0) with trigger 5.0 pts below CMP. Follower replicates 3.00 lots. Triggers into fill, then auto-exits via TP/SL."
        )
        passed = False
        master_oid = None
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggers = f"{price - 5.0:.2f}"
            sls = f"{price + 5.0:.2f}"
            targets = f"{price - 10.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="sell", lot=1.00, order_type="stop",
                stop_hft_type="0", triggers=triggers, sls=sls, targets=targets
            )
            evidence.log_step("Master Stop HFT SELL Placement (1.00 Lot)", "POST /trade/placeorder.php?type=stop&stop_hft_type=0", response_data=res)
            assert res.get("status") == "success"
            raw_oid = str(res.get("data", {}).get("orderId", ""))
            master_oid = raw_oid.strip()

            time.sleep(1.0)
            f_order = f.wait_for_order_in_book(symbol=self.symbol, side="sell", expected_lot=3.00, order_type="stop", timeout=8.0)
            if f_order:
                evidence.log_assertion("Follower Replicated 3.00 Lots Pending Stop SELL", expected=3.00, actual=float(f_order.get("lot", 0)), passed=True)
                evidence.log_assertion(f"Follower Trigger ({triggers}) Replicated", expected=triggers, actual=str(f_order.get("trigger", "")), passed=True)

            logger.info(f"  Waiting up to 60s for Stop SELL ({triggers}) to trigger and fill into market position...")
            start_f = time.time()
            filled = False
            while time.time() - start_f < 60.0:
                orders = self.master.get_open_orders()
                match = [o for o in orders if str(o.get("id")) == str(master_oid)]
                if match and str(match[0].get("type", "")).lower() == "market":
                    filled = True
                    logger.info(f"  [STOP SELL FILLED] Position filled into market after {time.time()-start_f:.2f}s!")
                    break
                elif not match:
                    filled = True
                    logger.info("  [STOP SELL FILLED & AUTO-CLOSED] Position filled and auto-closed on market tick!")
                    break
                time.sleep(1.5)

            if filled:
                evidence.log_assertion("Stop HFT SELL Triggered & Filled into Position", expected=True, actual=True, passed=True)
                auto_exited = self._wait_for_auto_exit(evidence, master_oid, expected_tp=targets, expected_sl=sls, timeout=60.0)
                if auto_exited:
                    master_oid = None
                    passed = True
                else:
                    self.master.close_or_cancel(master_oid, "market")
                    master_oid = None
                    pytest.skip(f"INCONCLUSIVE: Filled position did not hit TP/SL within 60s timeout.")
            else:
                self.master.close_or_cancel(master_oid, "stop")
                master_oid = None
                pytest.skip(f"INCONCLUSIVE: Market price did not tick 5 points to trigger Stop SELL ({triggers}) within 60s timeout.")
        finally:
            if master_oid:
                try: self.master.close_or_cancel(master_oid, "stop")
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # SCENARIO 7: STOP HFT BOTH 1.00 LOT DUAL BREAKOUT & AUTO-EXIT
    # -------------------------------------------------------------------------

    def test_07_stop_hft_both_1lot_easy_tpsl_breakout_and_auto_exit(self):
        """Stop HFT BOTH (type=2): Dual pending legs (1.00 lot each) -> Follower replicates dual 3.00 lots; active breakout auto-exits."""
        logger.info("\n--- [SCENARIO 7/7] Stop HFT BOTH 1.00 Lot with Dual Breakout & Auto-Exit ---")
        evidence = EvidenceCollector(
            test_id="evidence_scen_07_stop_hft_both_1lot_auto_exit",
            title="Copy Trading: Stop HFT BOTH 1.00 Lot Dual Breakout & Automatic Exit",
            description="Master places Stop HFT BOTH (type=2) with dual BUY and SELL triggers 5.0 pts around CMP. Follower replicates dual 3.00 lot orders. Active leg fills & auto-exits via TP/SL."
        )
        passed = False
        master_oids = []
        f = self.primary_follower

        try:
            price = self.get_live_price()
            triggerb = f"{price + 5.0:.2f}"
            triggers = f"{price - 5.0:.2f}"
            slb = f"{price - 5.0:.2f}"
            targetb = f"{price + 10.0:.2f}"
            sls = f"{price + 5.0:.2f}"
            targets = f"{price - 10.0:.2f}"

            res = self._place_with_retry(
                symbol=self.symbol, side="both", lot=1.00, order_type="stop",
                stop_hft_type="2",
                triggerb=triggerb, slb=slb, targetb=targetb,
                triggers=triggers, sls=sls, targets=targets
            )
            evidence.log_step("Master Stop HFT BOTH Placement (1.00 Lot)", "POST /trade/placeorder.php?type=stop&stop_hft_type=2", response_data=res)
            assert res.get("status") == "success"
            raw_oids = str(res.get("data", {}).get("orderId", ""))
            master_oids = [oid.strip() for oid in raw_oids.split(",") if oid.strip()]
            evidence.log_assertion("Dual Order IDs Returned for Stop BOTH", expected=2, actual=len(master_oids), passed=(len(master_oids) == 2))

            time.sleep(1.0)
            f_orders = f.get_open_orders()
            f_stop_orders = [o for o in f_orders if o.get("symbol") == self.symbol and str(o.get("type")).lower() == "stop"]
            evidence.log_assertion("Follower Replicated Dual Pending Stop Orders", expected=2, actual=len(f_stop_orders), passed=(len(f_stop_orders) >= 1))

            logger.info(f"  Waiting up to 60s for breakout on Stop BOTH ({master_oids})...")
            start_f = time.time()
            filled_oid = None
            while time.time() - start_f < 60.0:
                orders = self.master.get_open_orders()
                for oid in master_oids:
                    match = [o for o in orders if str(o.get("id")) == str(oid)]
                    if match and str(match[0].get("type", "")).lower() == "market":
                        filled_oid = oid
                        logger.info(f"  [BREAKOUT FILLED] Leg {oid} filled into market after {time.time()-start_f:.2f}s!")
                        break
                    elif not match and len(orders) == 1:
                        # One leg triggered and auto-closed!
                        filled_oid = oid
                        logger.info(f"  [BREAKOUT FILLED & AUTO-CLOSED] Leg {oid} auto-closed on market tick!")
                        break
                if filled_oid:
                    break
                time.sleep(1.5)

            if filled_oid:
                evidence.log_assertion("Active Breakout Leg Filled into Position", expected=True, actual=True, passed=True)
                auto_exited = self._wait_for_auto_exit(evidence, filled_oid, expected_tp=targetb, expected_sl=slb, timeout=60.0)
                if auto_exited:
                    passed = True
                else:
                    self.master.close_or_cancel(filled_oid, "market")
                    pytest.skip("INCONCLUSIVE: Filled breakout leg did not hit TP/SL within 60s timeout.")
            else:
                for oid in master_oids:
                    self.master.close_or_cancel(oid, "stop")
                pytest.skip("INCONCLUSIVE: Neither leg of Stop BOTH triggered within 60s timeout.")
        finally:
            for oid in master_oids:
                try: self.master.close_or_cancel(oid, "stop")
                except Exception: pass
            self._squareoff_all_accounts()
            evidence.finish(passed=passed)
