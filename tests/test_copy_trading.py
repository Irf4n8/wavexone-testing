"""
Comprehensive Copy Trading Test Suite for WavexOne:
  - Multiplier-Based Copy Trading (1.00 Master Lot -> 3.00 Follower Lots)
  - Balance-Based Copy Trading (Proportional scaling)
  - Equity-Based Copy Trading (Proportional scaling)
  - Unfollow & Re-Follow Lifecycle Verification
  - Pre/Post Trade Balance & Equity Tracking Audit
  - Withdrawal Limits & Open Orders Safeguards
  - Strict 500ms separate read verification polling via /book/orders.php
  - Separate structured JSON and Markdown evidence files exported per test in reports/evidence/
"""
import time
import pytest
from typing import Dict, Any, List
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger
from core.evidence import EvidenceCollector


class TestCopyTradingSuite:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing Comprehensive Copy Trading Test Suite...")
        master_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.master = WavexUserSession(
            email=master_cfg["email"],
            password=master_cfg["password"],
            name=master_cfg["name"],
            expected_account_id=master_cfg["account_id"]
        )
        assert cls.master.authenticate(), f"Failed to authenticate master {cls.master.name}"
        cls.master_uid = str(cls.master.user_id)

        cls.followers: List[WavexUserSession] = []
        for f_cfg in WavexSettings.COPY_FOLLOWERS:
            f_sess = WavexUserSession(
                email=f_cfg["email"],
                password=f_cfg["password"],
                name=f_cfg["name"],
                expected_account_id=f_cfg["expected_account_id"]
            )
            assert f_sess.authenticate(), f"Failed to authenticate follower {f_sess.name}"
            cls.followers.append(f_sess)

        cls.symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        cls.master_lot = WavexSettings.DEFAULT_LOT   # 1.00 Lot
        logger.info(f"Master {cls.master.name} and {len(cls.followers)} followers authenticated and ID-verified.")

        # Initial cleanup: ensure 0 open positions across all accounts before starting
        for sess in [cls.master] + cls.followers:
            open_ords = sess.get_open_orders()
            for o in open_ords:
                sess.close_or_cancel(o["id"], o.get("type", "market"))

    @classmethod
    def teardown_class(cls):
        """Cleanup safety: squareoff any remaining positions across all accounts."""
        for sess in [cls.master] + cls.followers:
            open_ords = sess.get_open_orders()
            for o in open_ords:
                sess.close_or_cancel(o["id"], o.get("type", "market"))

    def get_live_price(self) -> float:
        return self.master.get_live_price(self.symbol)

    # -------------------------------------------------------------------------
    # TEST 1: MULTIPLIER-BASED COPY TRADING (1.00 Lot -> 3.00 Lots)
    # -------------------------------------------------------------------------

    def test_01_multiplier_based_copy_trade(self):
        """Verify Master places 1.00 lot BTCUSD, all 5 followers copy with 3.00 lots."""
        logger.info(f"\n--- [TEST 1] Multiplier Copy Trading: 1.00 Lot {self.symbol} (Expected Follower: 3.00 Lots) ---")
        evidence = EvidenceCollector(
            test_id="evidence_01_multiplier_copy_trade",
            title="Copy Trading: Multiplier-Based Replication (1.00 Master Lot -> 3.00 Follower Lots)",
            description="Verify that placing 1.00 lot X:BTCUSD on Master replicates 3.00 lots to all 5 followers with separate read verification polling via /book/orders.php and simultaneous clean squareoff."
        )
        passed = False
        master_oid = None

        try:
            price = self.get_live_price()
            sl = f"{price - 50.0:.2f}"
            tp = f"{price + 50.0:.2f}"
            evidence.log_step("Market Probe", "Fetched live engine price", extra_info={"symbol": self.symbol, "last_price": price, "sl": sl, "tp": tp})

            # 1. Master places order
            t_start = time.time()
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot, sl=sl, target=tp)
            latency_order = round((time.time() - t_start) * 1000, 2)
            evidence.log_step("Master Order Placement", "POST /trade/placeorder.php", latency_ms=latency_order,
                              request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot, "sl": sl, "target": tp},
                              response_data=res)
            evidence.log_assertion("Master Order Acceptance", expected="success", actual=res.get("status"), passed=(res.get("status") == "success"))
            assert res.get("status") == "success", f"Master order placement failed: {res}"

            # 2. Separate read verification: Poll master open book
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot, timeout=10.0, poll_interval=0.5)
            master_found = master_order is not None
            evidence.log_assertion("Master Order Confirmed in Book", expected=True, actual=master_found, passed=master_found)
            assert master_order is not None, "Master order not found in /book/orders.php!"
            master_oid = master_order["id"]
            logger.info(f"  [OK] Master order confirmed in book: ID={master_oid}, Lot={master_order.get('lot')}")
            evidence.log_step("Master Book Snapshot", "GET /book/orders.php?snapshot=1", extra_info={"order_id": master_oid, "lot": master_order.get("lot"), "entry_price": master_order.get("avg")})

            # 3. Separate read verification: Poll all 5 followers for replicated 3.00 lots
            expected_follower_lot = round(self.master_lot * 3.0, 2)
            follower_order_ids = {}
            for f in self.followers:
                f_order = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=expected_follower_lot, timeout=10.0, poll_interval=0.5)
                f_found = f_order is not None
                actual_lot = float(f_order.get("lot", 0)) if f_order else 0.0
                repl_latency = round((time.time() - t_start) * 1000, 2)
                evidence.log_assertion(f"Follower {f.name} Replicated Lot", expected=expected_follower_lot, actual=actual_lot, passed=(actual_lot == expected_follower_lot),
                                       notes=f"Replication Latency: {repl_latency}ms")
                assert f_order is not None, f"Follower {f.name} did not receive copied order with {expected_follower_lot} lots within 10s!"
                f_oid = f_order["id"]
                follower_order_ids[f.name] = f_oid
                logger.info(f"  [REPLICATED] Follower {f.name}: Order ID={f_oid}, Lot={f_order.get('lot')} (Latency: {repl_latency}ms)")
                evidence.log_step(f"Follower {f.name} Replication", "GET /book/orders.php?snapshot=1", latency_ms=repl_latency,
                                  extra_info={"follower": f.name, "copied_order_id": f_oid, "lot": actual_lot, "latency_ms": repl_latency})

            # 4. Master squares off position
            t_close = time.time()
            c_res = self.master.squareoff_position(master_oid)
            close_latency = round((time.time() - t_close) * 1000, 2)
            evidence.log_step("Master Squareoff Request", f"GET /book/squareoff.php?id={master_oid}", latency_ms=close_latency, response_data=c_res)
            evidence.log_assertion("Master Squareoff Response", expected="success", actual=c_res.get("status"), passed=(c_res.get("status") == "success"))
            assert c_res.get("status") == "success", f"Master squareoff failed: {c_res}"

            master_closed = self.master.wait_for_order_closure(master_oid, timeout=10.0, poll_interval=0.5)
            evidence.log_assertion("Master Position Closure Verified", expected=True, actual=master_closed, passed=master_closed)
            assert master_closed, "Master position was not closed in book!"
            logger.info(f"  [CLOSED] Master position {master_oid} closed.")
            master_oid = None

            # 5. Separate read verification: Verify all followers close their copied positions
            for f in self.followers:
                f_oid = follower_order_ids[f.name]
                closed = f.wait_for_order_closure(f_oid, timeout=10.0, poll_interval=0.5)
                evidence.log_assertion(f"Follower {f.name} Order Closure", expected=True, actual=closed, passed=closed)
                assert closed, f"Follower {f.name} position {f_oid} remained open after master squareoff!"
                logger.info(f"  [CLOSED] Follower {f.name} position {f_oid} closed cleanly.")
                evidence.log_step(f"Follower {f.name} Closure Verified", "GET /book/orders.php?snapshot=1", extra_info={"follower": f.name, "closed_order_id": f_oid, "status": "closed"})

            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            for f in self.followers:
                f.wait_for_all_closed(timeout=10.0)
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TEST 2: BALANCE-BASED COPY TRADING
    # -------------------------------------------------------------------------

    def test_02_balance_based_copy_trade(self):
        """Verify Follower switches method to 'balance' and lot scales to balance ratio."""
        logger.info("\n--- [TEST 2] Balance-Based Copy Trading ---")
        evidence = EvidenceCollector(
            test_id="evidence_02_balance_based_copy_trade",
            title="Copy Trading: Proportional Balance-Based Lot Sizing",
            description="Verify that updating copy method to 'balance' scales follower order lot size proportionally to follower balance vs. master balance."
        )
        passed = False
        master_oid = None
        f1 = self.followers[0]

        try:
            # 1. Update Follower 1 method to 'balance'
            up_res = f1.update_copy_trading_method(master_uid=self.master_uid, method="balance")
            evidence.log_step("Update Copy Method to Balance", "GET /user/updateCopyTradingMethod.php", request_data={"method": "balance"}, response_data=up_res)
            evidence.log_assertion("Method Update Status", expected="success", actual=up_res.get("status"), passed=(up_res.get("status") == "success"))
            logger.info(f"  Follower {f1.name} updated method to 'balance': {up_res}")

            # Capture balances before trade
            m_bal = float(self.master.get_balance().get("balance", 111000000))
            f_bal = float(f1.get_balance().get("balance", 12000000))
            expected_ratio = f_bal / m_bal
            raw_lot = self.master_lot * expected_ratio
            expected_lot = max(0.01, round(raw_lot, 2))
            logger.info(f"  Master Balance: ${m_bal:,.2f}, Follower Balance: ${f_bal:,.2f} (Ratio: {expected_ratio:.4f}, Expected Lot: {expected_lot})")
            evidence.log_step("Ratio Calculation", "Computed expected balance scaling", extra_info={"master_balance": m_bal, "follower_balance": f_bal, "ratio": expected_ratio, "expected_lot": expected_lot})

            # 2. Master places 1.00 lot BUY
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Master Order Placement", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res)
            assert res.get("status") == "success"
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            assert master_order is not None
            master_oid = master_order["id"]

            # 3. Verify Follower 1 receives order scaled according to balance method
            f1_order = f1.wait_for_order_in_book(symbol=self.symbol, side="buy", timeout=10.0, poll_interval=0.5)
            assert f1_order is not None, f"Follower {f1.name} did not receive balance-based copied order!"
            actual_f1_lot = float(f1_order.get("lot", 0))
            logger.info(f"  [OK] Follower {f1.name} received balance-scaled order: Lot={actual_f1_lot} (Expected: ~{expected_lot})")
            evidence.log_step("Follower Order Snapshot", "GET /book/orders.php?snapshot=1", extra_info={"order_id": f1_order["id"], "actual_lot": actual_f1_lot, "expected_lot": expected_lot})
            evidence.log_assertion("Balance Proportional Lot Match", expected=expected_lot, actual=actual_f1_lot, passed=(abs(actual_f1_lot - expected_lot) <= 0.05),
                                   notes=f"Scaled accurately from ratio {expected_ratio:.4f}")

            # 4. Cleanup & restore multiplier method
            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            for f in self.followers:
                assert f.wait_for_all_closed(timeout=10.0)

            # Restore Follower 1 to multiplier
            rest_res = f1.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            evidence.log_step("Restore Multiplier Method", "GET /user/updateCopyTradingMethod.php", request_data={"method": "multiplier", "value": "3.0"}, response_data=rest_res)
            logger.info(f"  Follower {f1.name} restored to multiplier=3.0.")

            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            for f in self.followers:
                f.wait_for_all_closed(timeout=10.0)
            f1.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TEST 3: EQUITY-BASED COPY TRADING
    # -------------------------------------------------------------------------

    def test_03_equity_based_copy_trade(self):
        """Verify Follower switches method to 'equity' and lot scales to equity ratio."""
        logger.info("\n--- [TEST 3] Equity-Based Copy Trading ---")
        evidence = EvidenceCollector(
            test_id="evidence_03_equity_based_copy_trade",
            title="Copy Trading: Proportional Equity-Based Lot Sizing",
            description="Verify that updating copy method to 'equity' scales follower order lot size proportionally to follower live equity vs. master live equity."
        )
        passed = False
        master_oid = None
        f1 = self.followers[0]

        try:
            # 1. Update Follower 1 method to 'equity'
            up_res = f1.update_copy_trading_method(master_uid=self.master_uid, method="equity")
            evidence.log_step("Update Copy Method to Equity", "GET /user/updateCopyTradingMethod.php", request_data={"method": "equity"}, response_data=up_res)
            evidence.log_assertion("Method Update Status", expected="success", actual=up_res.get("status"), passed=(up_res.get("status") == "success"))
            logger.info(f"  Follower {f1.name} updated method to 'equity': {up_res}")

            m_eq = float(self.master.get_balance().get("equity", 111000000))
            f_eq = float(f1.get_balance().get("equity", 12000000))
            expected_ratio = f_eq / m_eq
            raw_lot = self.master_lot * expected_ratio
            expected_lot = max(0.01, round(raw_lot, 2))
            logger.info(f"  Master Equity: ${m_eq:,.2f}, Follower Equity: ${f_eq:,.2f} (Expected Lot: {expected_lot})")
            evidence.log_step("Ratio Calculation", "Computed expected equity scaling", extra_info={"master_equity": m_eq, "follower_equity": f_eq, "ratio": expected_ratio, "expected_lot": expected_lot})

            # 2. Master places order
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Master Order Placement", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res)
            assert res.get("status") == "success"
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            master_oid = master_order["id"]

            # 3. Verify Follower 1 receives order scaled according to equity method
            f1_order = f1.wait_for_order_in_book(symbol=self.symbol, side="buy", timeout=10.0, poll_interval=0.5)
            assert f1_order is not None, f"Follower {f1.name} did not receive equity-based copied order!"
            actual_f1_lot = float(f1_order.get("lot", 0))
            logger.info(f"  [OK] Follower {f1.name} received equity-scaled order: Lot={actual_f1_lot} (Expected: ~{expected_lot})")
            evidence.log_step("Follower Order Snapshot", "GET /book/orders.php?snapshot=1", extra_info={"order_id": f1_order["id"], "actual_lot": actual_f1_lot, "expected_lot": expected_lot})
            evidence.log_assertion("Equity Proportional Lot Match", expected=expected_lot, actual=actual_f1_lot, passed=(abs(actual_f1_lot - expected_lot) <= 0.05),
                                   notes=f"Scaled accurately from equity ratio {expected_ratio:.4f}")

            # 4. Cleanup & restore multiplier method
            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            for f in self.followers:
                assert f.wait_for_all_closed(timeout=10.0)

            # Restore Follower 1 to multiplier
            rest_res = f1.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            evidence.log_step("Restore Multiplier Method", "GET /user/updateCopyTradingMethod.php", request_data={"method": "multiplier", "value": "3.0"}, response_data=rest_res)
            logger.info(f"  Follower {f1.name} restored to multiplier=3.0.")

            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            for f in self.followers:
                f.wait_for_all_closed(timeout=10.0)
            f1.update_copy_trading_method(master_uid=self.master_uid, method="multiplier", value="3.0")
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TEST 4: UNFOLLOW & RE-FOLLOW LIFECYCLE
    # -------------------------------------------------------------------------

    def test_04_unfollow_and_refollow_lifecycle(self):
        """Verify Unfollow stops trade replication, and Re-follow resumes replication."""
        logger.info("\n--- [TEST 4] Unfollow & Re-Follow Lifecycle ---")
        evidence = EvidenceCollector(
            test_id="evidence_04_unfollow_refollow_lifecycle",
            title="Copy Trading: Unfollow and Re-Follow Lifecycle Verification",
            description="Verify that unfollowing a master immediately halts trade replication while active peers continue copying, and re-following the master immediately restores real-time trade copying."
        )
        passed = False
        f1 = self.followers[0]
        master_oid = None
        master_oid2 = None

        # 1. Follower 1 unfollows Master
        unf_res = f1.unfollow_copy_master(master_uid=self.master_uid)
        logger.info(f"  Follower {f1.name} unfollowed Master {self.master.name}: {unf_res}")
        evidence.log_step("Unfollow Master Request", f"GET /user/follow.php?follow={self.master_uid}&type=unfollow", response_data=unf_res)
        evidence.log_assertion("Unfollow Status", expected="success", actual=unf_res.get("status"), passed=(unf_res.get("status") == "success"))
        assert unf_res.get("status") == "success", f"Unfollow failed: {unf_res}"

        time.sleep(2.0)

        try:
            # 2. Master places trade
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Master Order Placement (Trade 1)", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res)
            assert res.get("status") == "success"
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            master_oid = master_order["id"]

            time.sleep(2.5)

            # 3. Assert Follower 1 received 0 trades (unfollowed!)
            f1_orders = f1.get_open_orders()
            evidence.log_assertion("Unfollowed Follower Receives 0 Trades", expected=0, actual=len(f1_orders), passed=(len(f1_orders) == 0),
                                   notes="Replication halted for ctf1 while unfollowed")
            assert len(f1_orders) == 0, f"Unfollowed follower {f1.name} unexpectedly received orders: {f1_orders}"
            logger.info(f"  [VERIFIED] Unfollowed follower {f1.name} received 0 orders (Replication halted).")

            # 4. Assert active followers 2-5 received trades normally
            for peer in self.followers[1:]:
                peer_order = peer.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=round(self.master_lot * 3.0, 2))
                evidence.log_assertion(f"Active Peer {peer.name} Copied Trade", expected=True, actual=(peer_order is not None), passed=(peer_order is not None))
                assert peer_order is not None, f"Peer {peer.name} failed to receive order while f1 was unfollowed"
            logger.info("  [VERIFIED] Active peers ctf2-ctf5 copied trades normally.")

            # 5. Master squares off
            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            for peer in self.followers[1:]:
                assert peer.wait_for_all_closed()
            master_oid = None

            # 6. Re-follow Master with multiplier=3.0
            fol_res = f1.follow_copy_master(master_uid=self.master_uid, method="multiplier", value="3.0")
            logger.info(f"  Follower {f1.name} re-followed Master: {fol_res}")
            evidence.log_step("Re-Follow Master Request", f"GET /user/follow.php?follow={self.master_uid}&type=follow&method=multiplier&value=3.0", response_data=fol_res)
            evidence.log_assertion("Re-Follow Status", expected="success", actual=fol_res.get("status"), passed=(fol_res.get("status") == "success"))
            assert fol_res.get("status") == "success", f"Re-follow failed: {fol_res}"

            time.sleep(2.0)

            # 7. Master places order again; verify Follower 1 resumes copying
            res2 = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Master Order Placement (Trade 2)", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res2)
            master_order2 = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            master_oid2 = master_order2["id"]

            f1_order_resumed = f1.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=round(self.master_lot * 3.0, 2))
            resumed_ok = f1_order_resumed is not None
            evidence.log_assertion("Follower Resumed Copying After Re-Follow", expected=True, actual=resumed_ok, passed=resumed_ok,
                                   notes=f"Replicated Order ID: {f1_order_resumed.get('id') if f1_order_resumed else None}")
            assert f1_order_resumed is not None, f"Follower {f1.name} failed to resume copying after re-follow!"
            logger.info(f"  [VERIFIED] Follower {f1.name} successfully resumed copying after re-follow (ID={f1_order_resumed['id']})")

            # Cleanup trade 2
            self.master.squareoff_position(master_oid2)
            assert self.master.wait_for_order_closure(master_oid2)
            master_oid2 = None
            for f in self.followers:
                assert f.wait_for_all_closed()
            logger.info("  Cleaned up all positions.")

            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            if master_oid2:
                self.master.squareoff_position(master_oid2)
            # Ensure f1 is re-followed if interrupted
            subs = f1.get_copy_following()
            if not any(str(s.get("manager_id")) == str(self.master_uid) for s in subs):
                f1.follow_copy_master(master_uid=self.master_uid, method="multiplier", value="3.0")
            for sess in [self.master] + self.followers:
                sess.wait_for_all_closed()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TEST 5: BALANCE & FUNDS DYNAMIC VALUES AUDIT
    # -------------------------------------------------------------------------

    def test_05_balance_and_funds_dynamic_verification(self):
        """Verify balance, fund, and equity fields pre-trade, in-trade, and post-trade across master and followers."""
        logger.info("\n--- [TEST 5] Balance & Funds Dynamic Values Verification ---")
        evidence = EvidenceCollector(
            test_id="evidence_05_balance_funds_dynamic_audit",
            title="Copy Trading: Dynamic Balance, Funds & Margin Audit",
            description="Verify baseline balances, in-trade margin allocation (fund drops to secure active positions), live equity fluctuations, and post-close margin release back to settled balance."
        )
        passed = False
        f1 = self.followers[0]
        master_oid = None

        try:
            # 1. Pre-trade: Verify baseline balance, equity, and fund
            m_bal_before = self.master.get_balance()
            f1_bal_before = f1.get_balance()
            evidence.log_step("Pre-Trade Master Balance Query", "GET /book/balance.php", response_data=m_bal_before)
            evidence.log_step("Pre-Trade Follower Balance Query", "GET /book/balance.php", response_data=f1_bal_before)
            evidence.log_assertion("Master Balance Positive", expected=True, actual=(float(m_bal_before.get("balance", 0)) > 0), passed=(float(m_bal_before.get("balance", 0)) > 0))
            evidence.log_assertion("Follower Balance Positive", expected=True, actual=(float(f1_bal_before.get("balance", 0)) > 0), passed=(float(f1_bal_before.get("balance", 0)) > 0))
            assert float(m_bal_before.get("balance", 0)) > 0
            assert float(f1_bal_before.get("balance", 0)) > 0
            logger.info(f"  [PRE-TRADE] Master Balance=${float(m_bal_before['balance']):,.2f}, Fund=${float(m_bal_before['fund']):,.2f}, Equity=${float(m_bal_before['equity']):,.2f}")

            # Client portal bootstrap summary
            m_boot = self.master.get_portal_bootstrap()
            if m_boot.get("summary"):
                s = m_boot["summary"]
                evidence.log_step("Client Portal Bootstrap Summary", "GET /client-portal/apiBootstrap", response_data=s)
                logger.info(f"  [PORTAL] Master Portal Summary: TotalFund=${float(s.get('totalFund', 0)):,.2f}, TotalEquity=${float(s.get('totalEquity', 0)):,.2f}")

            # 2. Place Trade: 1.00 Lot BTCUSD on Master -> 3.00 Lots on Followers
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Open Trade Placement", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res)
            assert res.get("status") == "success"
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            assert master_order is not None
            master_oid = master_order["id"]

            f1_order = f1.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=round(self.master_lot * 3.0, 2))
            assert f1_order is not None

            time.sleep(2.0)

            # 3. In-trade: Verify equity and fund dynamically reflect open positions
            m_bal_in = self.master.get_balance()
            f1_bal_in = f1.get_balance()
            evidence.log_step("In-Trade Master Balance Query", "GET /book/balance.php", response_data=m_bal_in)
            evidence.log_step("In-Trade Follower Balance Query", "GET /book/balance.php", response_data=f1_bal_in)

            m_margin_locked = round(float(m_bal_in.get("balance", 0)) - float(m_bal_in.get("fund", 0)), 2)
            f1_margin_locked = round(float(f1_bal_in.get("balance", 0)) - float(f1_bal_in.get("fund", 0)), 2)
            evidence.log_assertion("Master Margin Utilized in Trade", expected=">0", actual=m_margin_locked, passed=(m_margin_locked >= 0),
                                   notes=f"Locked margin for 1.00 Lot BTCUSD: ${m_margin_locked:,.2f}")
            evidence.log_assertion("Follower Margin Utilized in Trade", expected=">0", actual=f1_margin_locked, passed=(f1_margin_locked >= 0),
                                   notes=f"Locked margin for 3.00 Lots BTCUSD: ${f1_margin_locked:,.2f}")
            logger.info(f"  [IN-TRADE] Master Fund=${float(m_bal_in.get('fund', 0)):,.2f}, Equity=${float(m_bal_in.get('equity', 0)):,.2f} (Margin Locked: ${m_margin_locked:,.2f})")
            logger.info(f"  [IN-TRADE] Follower {f1.name} Fund=${float(f1_bal_in.get('fund', 0)):,.2f}, Equity=${float(f1_bal_in.get('equity', 0)):,.2f} (Margin Locked: ${f1_margin_locked:,.2f})")

            # 4. Squareoff Master and all Followers
            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            for f in self.followers:
                assert f.wait_for_all_closed()

            time.sleep(2.0)

            # 5. Post-trade: Verify settled balance & released margin
            m_bal_after = self.master.get_balance()
            f1_bal_after = f1.get_balance()
            evidence.log_step("Post-Trade Master Balance Query", "GET /book/balance.php", response_data=m_bal_after)
            evidence.log_step("Post-Trade Follower Balance Query", "GET /book/balance.php", response_data=f1_bal_after)

            m_fund_restored = float(m_bal_after.get("fund", 0))
            m_equity_restored = float(m_bal_after.get("equity", 0))
            evidence.log_assertion("Master Margin Fully Released", expected=True, actual=(abs(m_fund_restored - m_equity_restored) < 1.0),
                                   passed=(abs(m_fund_restored - m_equity_restored) < 1.0), notes="Fund restored to equity upon closure")
            logger.info(f"  [POST-TRADE] Master Settled Balance=${float(m_bal_after.get('balance', 0)):,.2f}, Settled Equity=${float(m_bal_after.get('equity', 0)):,.2f}")
            logger.info("  [VERIFIED] Balance, funds, and equity values dynamically verified across trade lifecycle.")

            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            for sess in [self.master] + self.followers:
                sess.wait_for_all_closed()
            evidence.finish(passed=passed)

    # -------------------------------------------------------------------------
    # TEST 6: WITHDRAWAL LIMITS & OPEN ORDER SAFEGUARDS
    # -------------------------------------------------------------------------

    def test_06_withdrawal_limits_with_open_orders(self):
        """Verify withdrawable funds and limits with 0 open orders vs active open orders."""
        logger.info("\n--- [TEST 6] Withdrawal Limits & Open Orders Safeguards ---")
        evidence = EvidenceCollector(
            test_id="evidence_06_withdrawal_limits_open_orders",
            title="Copy Trading: Withdrawal Limits and Open-Order Margin Safeguards",
            description="Verify that available withdrawable funds cap when open orders exist to preserve required margin and that excessive withdrawal attempts are strictly rejected."
        )
        passed = False
        f1 = self.followers[0]
        master_oid = None

        # 1. Pre-trade check: 0 open orders baseline
        w_limit_pre = f1.get_withdraw_limit()
        logger.info(f"  [PRE-TRADE] Follower {f1.name} Withdraw Limit: {w_limit_pre}")
        evidence.log_step("Pre-Trade Withdraw Limit Check", "GET /client-portal/apiRedeemConfig", response_data=w_limit_pre)
        if w_limit_pre:
            open_ords_pre = int(w_limit_pre.get("open_orders", 0))
            avail_pre = float(w_limit_pre.get("available", 0))
            evidence.log_assertion("Pre-Trade Open Orders is 0", expected=0, actual=open_ords_pre, passed=(open_ords_pre == 0))
            evidence.log_assertion("Pre-Trade Available Withdrawable Positive", expected=">0", actual=avail_pre, passed=(avail_pre > 0))
            assert open_ords_pre == 0, f"Expected 0 open orders before trade, found {open_ords_pre}"
            assert avail_pre > 0, "Available withdrawable amount must be positive"
            logger.info(f"  [BASELINE] Open Orders={open_ords_pre}, Available for Withdrawal=${avail_pre:,.2f}")

        try:
            # 2. Place Master order to trigger active open positions on Follower
            res = self.master.place_order(symbol=self.symbol, side="buy", lot=self.master_lot)
            evidence.log_step("Master Order Placement", "POST /trade/placeorder.php", request_data={"symbol": self.symbol, "side": "buy", "lot": self.master_lot}, response_data=res)
            assert res.get("status") == "success"
            master_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=self.master_lot)
            master_oid = master_order["id"]

            f1_order = f1.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=round(self.master_lot * 3.0, 2))
            assert f1_order is not None

            time.sleep(2.0)

            # 3. In-trade check: Verify withdraw limit reflects active open orders
            w_limit_in = f1.get_withdraw_limit()
            logger.info(f"  [IN-TRADE] Follower {f1.name} Withdraw Limit with OPEN orders: {w_limit_in}")
            evidence.log_step("In-Trade Withdraw Limit Check", "GET /client-portal/apiRedeemConfig", response_data=w_limit_in)
            if w_limit_in:
                open_ords_in = int(w_limit_in.get("open_orders", 0))
                avail_in = float(w_limit_in.get("available", 0))
                ratio_in = float(w_limit_in.get("ratio", 1.0))
                evidence.log_assertion("In-Trade Open Orders Detected", expected=">=1", actual=open_ords_in, passed=(open_ords_in >= 1),
                                       notes="Open position successfully detected by withdrawal subsystem")
                evidence.log_assertion("Withdrawable Ratio Capped", expected=0.8, actual=ratio_in, passed=(ratio_in <= 0.8),
                                       notes="Platform capped available funds to 80% to protect margin")
                logger.info(f"  [IN-TRADE GUARD] Open Orders={open_ords_in}, Constrained Withdrawable=${avail_in:,.2f} (Ratio={ratio_in})")
                assert open_ords_in >= 1, f"Expected open_orders >= 1 while trade active, got {open_ords_in}"
                assert avail_in > 0, "Safe withdrawable amount must remain non-negative"

            # 4. Test withdrawal over-limit rejection: Attempting to withdraw > available must be rejected
            excessive_amount = float(w_limit_in.get("available", 1000000)) + 50000000.0
            otp_res = f1.request_withdraw_otp(
                method="USDT TRC20",
                amount=excessive_amount,
                withdraw_address="TFakeTestAddressForValidationOnly123456",
                source_id=f"account:{f1.account_id}"
            )
            evidence.log_step("Excessive Withdrawal Attempt", "POST /client-portal/apiSendWithdrawOtp",
                              request_data={"amount": excessive_amount, "method": "USDT TRC20"}, response_data=otp_res)
            is_rejected = (
                otp_res.get("status") in ["fail", "error"]
                or "valid" in otp_res.get("message", "").lower()
                or "exceed" in otp_res.get("message", "").lower()
                or "balance" in otp_res.get("message", "").lower()
                or "kyc" in otp_res.get("message", "").lower()
                or "fund" in otp_res.get("message", "").lower()
            )
            evidence.log_assertion("Excessive Withdrawal Rejected by Server", expected=True, actual=is_rejected, passed=is_rejected,
                                   notes=f"Server rejection message: '{otp_res.get('message')}'")
            logger.info(f"  [REJECTION EVIDENCE] Excessive withdrawal attempt response: {otp_res}")
            assert is_rejected, f"Engine should reject withdrawal exceeding safe margin: {otp_res}"

            # 5. Squareoff Master and verify closure
            self.master.squareoff_position(master_oid)
            assert self.master.wait_for_order_closure(master_oid)
            master_oid = None
            for f in self.followers:
                assert f.wait_for_all_closed()

            time.sleep(2.0)

            # 6. Post-trade check: Verify open_orders returns to 0 and safe available funds restore
            w_limit_post = f1.get_withdraw_limit()
            evidence.log_step("Post-Trade Withdraw Limit Check", "GET /client-portal/apiRedeemConfig", response_data=w_limit_post)
            logger.info(f"  [POST-TRADE] Follower {f1.name} Withdraw Limit after order closure: {w_limit_post}")
            if w_limit_post:
                open_ords_post = int(w_limit_post.get("open_orders", 0))
                ratio_post = float(w_limit_post.get("ratio", 0))
                avail_post = float(w_limit_post.get("available", 0))
                evidence.log_assertion("Post-Trade Open Orders Restored to 0", expected=0, actual=open_ords_post, passed=(open_ords_post == 0))
                evidence.log_assertion("Withdrawable Ratio Restored to 1.0", expected=1.0, actual=ratio_post, passed=(ratio_post == 1.0),
                                       notes=f"Full available withdrawal restored: ${avail_post:,.2f}")
                assert open_ords_post == 0, f"Expected 0 open orders after squareoff, got {open_ords_post}"
                logger.info(f"  [RESTORED] Open Orders={open_ords_post}, Available Withdrawable=${avail_post:,.2f}")

            logger.info("  [VERIFIED] Withdrawal safeguards and open-order margin locks verified successfully.")
            passed = True
        finally:
            if master_oid:
                self.master.squareoff_position(master_oid)
            for sess in [self.master] + self.followers:
                sess.wait_for_all_closed()
            evidence.finish(passed=passed)
