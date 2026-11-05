"""
Automated Test Suite for Order Types on WavexOne:
  - Market Orders (BUY & SELL with TP, SL)
  - Limit Orders (BUY & SELL with Trigger, TP, SL)
  - Stop HFT Orders (BUY, SELL, and BOTH)
Includes validation guard tests and captures detailed evidence for any server errors or rejections.
"""
import time
import pytest
from typing import Dict, Any, List
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger


class TestOrderTypesSuite:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing Order Types Test Suite...")
        master_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.client = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
        assert cls.client.authenticate(), "Authentication failed"
        cls.client.generate_fingerprint()
        cls.symbol = "C:EURUSD"
        cls.evidence_log: List[Dict[str, Any]] = []

    @classmethod
    def teardown_class(cls):
        """Cleanup all open positions and pending orders."""
        open_ords = cls.client.get_open_orders()
        for o in open_ords:
            cls.client.close_or_cancel(o["id"], o.get("type", "market"))

    def get_price(self) -> float:
        return self.client.get_live_price(self.symbol)

    # -------------------------------------------------------------------------
    # 1. MARKET ORDERS (BUY & SELL WITH TP / SL)
    # -------------------------------------------------------------------------

    def test_01_market_buy_with_tp_sl(self):
        """Test Market BUY with tightly reachable TP and SL."""
        price = self.get_price()
        sl = f"{price - 0.0005:.5f}"
        tp = f"{price + 0.0005:.5f}"

        logger.info(f"\n[TEST 1] Market BUY with TP/SL (Price={price}, SL={sl}, TP={tp})")
        res = self.client.place_order(symbol=self.symbol, side="buy", lot=0.01, sl=sl, target=tp)
        assert res.get("status") == "success", f"Market BUY failed: {res}"

        time.sleep(1.5)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("symbol") == self.symbol and o.get("bs", "").upper() == "BUY"]
        assert len(matched) > 0, f"Order not found in book! Orders: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Market BUY opened: ID={oid}, SL={matched[0].get('sl')}, TP={matched[0].get('tp')}")

        # Squareoff position
        c_res = self.client.squareoff_position(oid)
        assert c_res.get("status") == "success", f"Squareoff failed: {c_res}"
        logger.info(f"  [CLOSED] Position {oid} closed cleanly.")

    def test_02_market_sell_with_tp_sl(self):
        """Test Market SELL with tightly reachable TP and SL."""
        price = self.get_price()
        sl = f"{price + 0.0005:.5f}"
        tp = f"{price - 0.0005:.5f}"

        logger.info(f"\n[TEST 2] Market SELL with TP/SL (Price={price}, SL={sl}, TP={tp})")
        res = self.client.place_order(symbol=self.symbol, side="sell", lot=0.01, sl=sl, target=tp)
        assert res.get("status") == "success", f"Market SELL failed: {res}"

        time.sleep(1.5)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("symbol") == self.symbol and o.get("bs", "").upper() == "SELL"]
        assert len(matched) > 0, f"Order not found in book! Orders: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Market SELL opened: ID={oid}, SL={matched[0].get('sl')}, TP={matched[0].get('tp')}")

        # Squareoff position
        c_res = self.client.squareoff_position(oid)
        assert c_res.get("status") == "success", f"Squareoff failed: {c_res}"
        logger.info(f"  [CLOSED] Position {oid} closed cleanly.")

    def test_03_market_buy_invalid_sl_evidence(self):
        """Evidence Capture: Attempt Market BUY with invalid SL (SL > Market Price)."""
        price = self.get_price()
        invalid_sl = f"{price + 0.0050:.5f}"  # Higher than price is illegal for Buy SL
        tp = f"{price + 0.0010:.5f}"

        logger.info(f"\n[TEST 3] Capturing Evidence: Market BUY with invalid SL={invalid_sl} > Price={price}")
        res = self.client.place_order(symbol=self.symbol, side="buy", lot=0.01, sl=invalid_sl, target=tp)

        # Must be rejected by server validation guard
        assert res.get("status") == "fail", f"Expected rejection but got: {res}"
        assert "less than last price" in res.get("message", "").lower(), f"Unexpected error message: {res}"
        logger.info(f"  [EVIDENCE RECORDED] Server correctly rejected: '{res.get('message')}'")

    def test_04_market_sell_invalid_tp_evidence(self):
        """Evidence Capture: Attempt Market SELL with invalid TP (TP > Market Price)."""
        price = self.get_price()
        sl = f"{price + 0.0050:.5f}"
        invalid_tp = f"{price + 0.0010:.5f}"  # Higher than price is illegal for Sell Target

        logger.info(f"\n[TEST 4] Capturing Evidence: Market SELL with invalid TP={invalid_tp} > Price={price}")
        res = self.client.place_order(symbol=self.symbol, side="sell", lot=0.01, sl=sl, target=invalid_tp)

        # Must be rejected by server validation guard
        assert res.get("status") == "fail", f"Expected rejection but got: {res}"
        assert "less than last price" in res.get("message", "").lower(), f"Unexpected error message: {res}"
        logger.info(f"  [EVIDENCE RECORDED] Server correctly rejected: '{res.get('message')}'")

    # -------------------------------------------------------------------------
    # 2. LIMIT ORDERS (BUY LIMIT & SELL LIMIT WITH TRIGGER / TP / SL)
    # -------------------------------------------------------------------------

    def test_05_limit_buy_with_trigger_tp_sl(self):
        """Test Limit BUY (Trigger below market price) with TP and SL."""
        price = self.get_price()
        trigger = f"{price - 0.0015:.5f}"  # Below market
        sl = f"{price - 0.0025:.5f}"       # Below trigger
        tp = f"{price - 0.0005:.5f}"       # Above trigger

        logger.info(f"\n[TEST 5] Limit BUY (Trigger={trigger}, SL={sl}, TP={tp})")
        res = self.client.place_order(
            symbol=self.symbol, side="buy", lot=0.01, order_type="limit", trigger=trigger, sl=sl, target=tp
        )
        assert res.get("status") == "success", f"Limit BUY failed: {res}"

        time.sleep(1.0)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("type") == "limit" and o.get("bs", "").upper() == "BUY"]
        assert len(matched) > 0, f"Limit BUY order not found in book: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Limit BUY confirmed in pending book: ID={oid}, Trigger={matched[0].get('trigger')}")

        # Cancel pending limit order via cancel.php
        c_res = self.client.cancel_order(oid)
        assert c_res.get("status") == "success", f"Cancel limit order failed: {c_res}"
        logger.info(f"  [CANCELLED] Pending limit order {oid} cancelled cleanly.")

    def test_06_limit_sell_with_trigger_tp_sl(self):
        """Test Limit SELL (Trigger above market price) with TP and SL."""
        price = self.get_price()
        trigger = f"{price + 0.0015:.5f}"  # Above market
        sl = f"{price + 0.0025:.5f}"       # Above trigger
        tp = f"{price + 0.0005:.5f}"       # Below trigger

        logger.info(f"\n[TEST 6] Limit SELL (Trigger={trigger}, SL={sl}, TP={tp})")
        res = self.client.place_order(
            symbol=self.symbol, side="sell", lot=0.01, order_type="limit", trigger=trigger, sl=sl, target=tp
        )
        assert res.get("status") == "success", f"Limit SELL failed: {res}"

        time.sleep(1.0)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("type") == "limit" and o.get("bs", "").upper() == "SELL"]
        assert len(matched) > 0, f"Limit SELL order not found in book: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Limit SELL confirmed in pending book: ID={oid}, Trigger={matched[0].get('trigger')}")

        # Cancel pending limit order via cancel.php
        c_res = self.client.cancel_order(oid)
        assert c_res.get("status") == "success", f"Cancel limit order failed: {c_res}"
        logger.info(f"  [CANCELLED] Pending limit order {oid} cancelled cleanly.")

    # -------------------------------------------------------------------------
    # 3. STOP HFT ORDERS (BUY, SELL, AND BOTH)
    # -------------------------------------------------------------------------

    def test_07_stop_hft_buy(self):
        """Test Stop HFT BUY (stop_hft_type=1) with Trigger, TP, and SL."""
        price = self.get_price()
        triggerb = f"{price + 0.0010:.5f}"
        slb = f"{price + 0.0005:.5f}"
        targetb = f"{price + 0.0015:.5f}"

        logger.info(f"\n[TEST 7] Stop HFT BUY (Trigger={triggerb}, SL={slb}, TP={targetb})")
        res = self.client.place_order(
            symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="1",
            lotb="0.01", triggerb=triggerb, slb=slb, targetb=targetb
        )
        assert res.get("status") == "success", f"Stop HFT BUY failed: {res}"

        time.sleep(1.0)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("type") == "stop" and o.get("bs", "").upper() == "BUY"]
        assert len(matched) > 0, f"Stop HFT BUY not found in book: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Stop HFT BUY confirmed in pending book: ID={oid}, Trigger={matched[0].get('trigger')}")

        c_res = self.client.cancel_order(oid)
        assert c_res.get("status") == "success", f"Cancel stop order failed: {c_res}"
        logger.info(f"  [CANCELLED] Stop HFT BUY order {oid} cancelled cleanly.")

    def test_08_stop_hft_sell(self):
        """Test Stop HFT SELL (stop_hft_type=0) with Trigger, TP, and SL."""
        price = self.get_price()
        triggers = f"{price - 0.0010:.5f}"
        sls = f"{price - 0.0005:.5f}"
        targets = f"{price - 0.0015:.5f}"

        logger.info(f"\n[TEST 8] Stop HFT SELL (Trigger={triggers}, SL={sls}, TP={targets})")
        res = self.client.place_order(
            symbol=self.symbol, side="sell", order_type="stop", stop_hft_type="0",
            lots="0.01", triggers=triggers, sls=sls, targets=targets
        )
        assert res.get("status") == "success", f"Stop HFT SELL failed: {res}"

        time.sleep(1.0)
        orders = self.client.get_open_orders()
        matched = [o for o in orders if o.get("type") == "stop" and o.get("bs", "").upper() == "SELL"]
        assert len(matched) > 0, f"Stop HFT SELL not found in book: {orders}"
        oid = matched[0]["id"]
        logger.info(f"  [OK] Stop HFT SELL confirmed in pending book: ID={oid}, Trigger={matched[0].get('trigger')}")

        c_res = self.client.cancel_order(oid)
        assert c_res.get("status") == "success", f"Cancel stop order failed: {c_res}"
        logger.info(f"  [CANCELLED] Stop HFT SELL order {oid} cancelled cleanly.")

    def test_09_stop_hft_both(self):
        """Test Stop HFT Both (stop_hft_type=2) placing Buy & Sell pending orders simultaneously."""
        price = self.get_price()
        triggerb = f"{price + 0.0010:.5f}"
        slb = f"{price + 0.0005:.5f}"
        targetb = f"{price + 0.0015:.5f}"
        triggers = f"{price - 0.0010:.5f}"
        sls = f"{price - 0.0005:.5f}"
        targets = f"{price - 0.0015:.5f}"

        logger.info(f"\n[TEST 9] Stop HFT Both (BUY Trigger={triggerb}, SELL Trigger={triggers})")
        res = self.client.place_order(
            symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="2",
            lotb="0.01", triggerb=triggerb, slb=slb, targetb=targetb,
            lots="0.01", triggers=triggers, sls=sls, targets=targets
        )
        assert res.get("status") == "success", f"Stop HFT Both failed: {res}"
        order_ids_str = res.get("data", {}).get("orderId", "")
        logger.info(f"  [OK] Stop HFT Both created dual order IDs: {order_ids_str}")

        time.sleep(1.0)
        orders = self.client.get_open_orders()
        stop_orders = [o for o in orders if o.get("type") == "stop"]
        assert len(stop_orders) >= 2, f"Expected at least 2 pending stop orders in book, found {len(stop_orders)}"

        # Cancel all pending stop orders
        for so in stop_orders:
            c_res = self.client.cancel_order(so["id"])
            assert c_res.get("status") == "success"
            logger.info(f"  [CANCELLED] Cancelled pending Stop HFT order {so['id']}")

    def test_10_stop_hft_both_invalid_side_evidence(self):
        """Evidence Capture: Attempt Stop HFT Both with raw bs='both' instead of 'buy'."""
        price = self.get_price()
        logger.info("\n[TEST 10] Capturing Evidence: Stop HFT Both with bs='both' (API rejects with 'Invalid order side')")
        res = self.client.place_order(
            symbol=self.symbol, side="both", order_type="stop", stop_hft_type="2",
            lotb="0.01", triggerb=f"{price+0.001:.5f}", lots="0.01", triggers=f"{price-0.001:.5f}"
        )
        assert res.get("status") == "fail", f"Expected rejection but got: {res}"
        assert res.get("message") == "Invalid order side", f"Unexpected error: {res}"
        logger.info(f"  [EVIDENCE RECORDED] Server correctly validated: '{res.get('message')}' (Raw: {res})")
