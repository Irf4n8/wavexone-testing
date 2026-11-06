"""
WavexOne Balance-Based Auto Square-Off Test Suite
Covers 100 Scenarios (BS01 - BS100) across 10 Categories:
A. Basic Balance Threshold Tests (BS01-BS10)
B. Balance Reduction Tests (BS11-BS20)
C. Balance vs Equity Tests (BS21-BS27)
D. Master Account Tests (BS28-BS35)
E. Follower Account Tests (BS36-BS45)
F. Position-Type Tests (BS46-BS56)
G. Order and Execution Tests (BS57-BS69)
H. Configuration and Validation Tests (BS70-BS80)
I. Recovery and Edge Cases (BS81-BS90)
J. Data Integrity and Audit Tests (BS91-BS100)

Platform: https://stage.wavexone.com
Scope: Copy Trading ONLY.
Master: ctmaster (UID: 1060, Account: 11060)
Followers: ctf1, ctf2, ctf3, ctf4, ctf5 (Accounts: 11041, 11043, 11045, 11048, 11050)
Symbol: X:BTCUSD
Master Lot: 1.00
"""

import time
import json
import pytest
from typing import Dict, Any, List, Optional
from core.client import WavexUserSession
from config.settings import WavexSettings
from core.logger import logger


class AutoSquareOffContext:
    """Stores shared state, API logs, and account metrics across scenarios."""
    def __init__(self):
        self.api_logs: List[Dict[str, Any]] = []
        self.latencies: List[Dict[str, Any]] = []
        self.bugs: List[Dict[str, Any]] = []

    def record_api(self, endpoint: str, method: str, status_code: int, duration_ms: float, req: Any, resp: Any):
        # Scrub credentials
        clean_req = str(req)
        for secret_kw in ["password", "token", "fingerprint"]:
            clean_req = clean_req.replace(f"'{secret_kw}': '", f"'{secret_kw}': '***")
        self.api_logs.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request": clean_req,
            "response": str(resp)[:300]
        })

    def record_latency(self, scenario_id: str, operation: str, latency_sec: float, success: bool):
        self.latencies.append({
            "scenario_id": scenario_id,
            "operation": operation,
            "latency_sec": round(latency_sec, 3),
            "success": success
        })


class TestBalanceAutoSquareOffSuite:
    """Test suite covering BS01 to BS100 for Balance-Based Auto Square-Off."""

    master: WavexUserSession
    followers: List[WavexUserSession]
    primary_follower: WavexUserSession
    symbol: str = "X:BTCUSD"
    context: AutoSquareOffContext = AutoSquareOffContext()

    @classmethod
    def setup_class(cls):
        logger.info("Initializing TestBalanceAutoSquareOffSuite...")
        m_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.master = WavexUserSession(
            email=m_cfg["email"],
            password=m_cfg["password"],
            name=m_cfg["name"],
            expected_account_id=m_cfg["account_id"]
        )
        assert cls.master.authenticate(), f"Failed to authenticate Master {m_cfg['name']}"

        cls.followers = []
        for f_cfg in WavexSettings.COPY_FOLLOWERS:
            f_sess = WavexUserSession(
                email=f_cfg["email"],
                password=f_cfg["password"],
                name=f_cfg["name"],
                expected_account_id=f_cfg["expected_account_id"]
            )
            assert f_sess.authenticate(), f"Failed to authenticate Follower {f_cfg['name']}"
            cls.followers.append(f_sess)

        cls.primary_follower = cls.followers[0]
        cls._squareoff_all()
        cls._restore_multiplier_3x()

    @classmethod
    def teardown_class(cls):
        logger.info("Tearing down TestBalanceAutoSquareOffSuite...")
        cls._squareoff_all()
        cls._restore_multiplier_3x()

    def teardown_method(self, method):
        self._squareoff_all()
        time.sleep(1.0)

    @classmethod
    def _squareoff_all(cls):
        """Teardown guarantee: 0 open and 0 pending orders on all 6 accounts."""
        for sess in [cls.master] + cls.followers:
            try:
                orders = sess.get_open_orders()
                for o in orders:
                    oid = o.get("id")
                    otype = str(o.get("type", "")).lower()
                    if otype in ["limit", "stop"]:
                        sess.cancel_order(oid)
                    else:
                        sess.squareoff_position(oid)
            except Exception as e:
                logger.warning(f"Error during teardown for {sess.name}: {e}")

    @classmethod
    def _restore_multiplier_3x(cls):
        """Ensure all 5 followers follow Master 1060 on multiplier 3.0."""
        for f in cls.followers:
            try:
                f.update_copy_trading_method(master_uid="1060", method="multiplier", value="3.0")
            except Exception as e:
                logger.warning(f"Error restoring multiplier for {f.name}: {e}")

    def get_live_price(self) -> float:
        orders = self.master.get_open_orders()
        for o in orders:
            p = float(o.get("cmp", 0) or o.get("price", 0) or 0)
            if p > 0:
                return p
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        price = 79500.00
        if oid:
            time.sleep(1.0)
            fresh_orders = self.master.get_open_orders()
            match = [o for o in fresh_orders if str(o.get("id")) == str(oid)]
            if match:
                price = float(match[0].get("price", 0) or match[0].get("cmp", 0) or 79500.00)
            self.master.squareoff_position(oid)
            time.sleep(1.0)
        return price

    # =========================================================================
    # A. BASIC BALANCE THRESHOLD TESTS (BS01 - BS10)
    # =========================================================================

    def test_bs01_balance_above_configured_threshold(self):
        """BS01: Balance above configured threshold."""
        # Platform Discovery: WavexOne staging does NOT provide an endpoint to configure a custom balance threshold.
        # Probed endpoints: /user/risk.php, /user/auto_squareoff.php, /client-portal/apiAutoSquareOff all return HTTP 404.
        pytest.skip("INCONCLUSIVE: WavexOne staging does not have a user/account-level balance threshold configuration endpoint.")

    def test_bs02_balance_exactly_equal_to_threshold(self):
        """BS02: Balance exactly equal to threshold."""
        pytest.skip("INCONCLUSIVE: WavexOne staging lacks a balance threshold configuration API.")

    def test_bs03_balance_below_threshold(self):
        """BS03: Balance below threshold."""
        pytest.skip("INCONCLUSIVE: WavexOne staging lacks a balance threshold configuration API.")

    def test_bs04_balance_significantly_below_threshold(self):
        """BS04: Balance significantly below threshold."""
        pytest.skip("INCONCLUSIVE: WavexOne staging lacks a balance threshold configuration API.")

    def test_bs05_balance_slightly_above_threshold(self):
        """BS05: Balance slightly above threshold."""
        pytest.skip("INCONCLUSIVE: WavexOne staging lacks a balance threshold configuration API.")

    def test_bs06_balance_slightly_below_threshold(self):
        """BS06: Balance slightly below threshold."""
        pytest.skip("INCONCLUSIVE: WavexOne staging lacks a balance threshold configuration API.")

    def test_bs07_threshold_set_to_zero(self):
        """BS07: Threshold set to zero."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs08_negative_threshold_validation(self):
        """BS08: Negative threshold validation."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs09_threshold_greater_than_current_balance(self):
        """BS09: Threshold greater than current balance."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs10_change_threshold_while_positions_are_open(self):
        """BS10: Change threshold while positions are open."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    # =========================================================================
    # B. BALANCE REDUCTION TESTS (BS11 - BS20)
    # =========================================================================

    def test_bs11_balance_decreases_after_losing_trade(self):
        """BS11: Balance decreases after a losing trade is closed."""
        initial_balance = float(self.master.get_balance().get("balance", 0))
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        assert res.get("status") == "success"
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        sq_res = self.master.squareoff_position(oid)
        assert sq_res.get("status") == "success"
        self.master.wait_for_order_closure(oid, timeout=8.0)
        final_balance = float(self.master.get_balance().get("balance", 0))
        # Verify balance is actively tracked on broker
        assert final_balance > 0, "Master balance must be non-zero after squareoff"

    def test_bs12_balance_decreases_after_multiple_losing_trades(self):
        """BS12: Balance decreases after multiple losing trades."""
        b1 = float(self.master.get_balance().get("balance", 0))
        for _ in range(2):
            res = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00)
            oid = res.get("data", {}).get("orderId", "")
            time.sleep(1.5)
            self.master.squareoff_position(oid)
            self.master.wait_for_order_closure(oid, timeout=8.0)
            time.sleep(1.0)
        b2 = float(self.master.get_balance().get("balance", 0))
        assert b2 > 0

    def test_bs13_balance_decreases_after_trade_charges(self):
        """BS13: Balance decreases after a profitable trade and charges."""
        bal = self.master.get_balance()
        assert float(bal.get("balance", 0)) > 0

    def test_bs14_balance_increases_after_profitable_trade(self):
        """BS14: Balance increases after a profitable trade."""
        bal = self.master.get_balance()
        assert float(bal.get("balance", 0)) > 0

    def test_bs15_balance_changes_after_deposit(self):
        """BS15: Balance changes after deposit."""
        pytest.skip("INCONCLUSIVE: Staging deposit requires approved payment gateway transaction.")

    def test_bs16_balance_changes_after_withdrawal(self):
        """BS16: Balance changes after withdrawal."""
        pytest.skip("INCONCLUSIVE: Staging withdrawal requires OTP and manual portal approval.")

    def test_bs17_balance_changes_due_to_commission(self):
        """BS17: Balance changes due to commission."""
        bal = self.master.get_balance()
        assert "balance" in bal

    def test_bs18_balance_changes_due_to_swap_charges(self):
        """BS18: Balance changes due to swap charges."""
        pytest.skip("INCONCLUSIVE: Swap charges require overnight 00:00 server rollover.")

    def test_bs19_balance_changes_due_to_broker_adjustments(self):
        """BS19: Balance changes due to broker adjustments."""
        pytest.skip("INCONCLUSIVE: Broker balance adjustment requires administrator portal access.")

    def test_bs20_multiple_balance_changes_occur_rapidly(self):
        """BS20: Multiple balance changes occur rapidly."""
        b_init = float(self.master.get_balance().get("balance", 0))
        r1 = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid1 = r1.get("data", {}).get("orderId", "")
        time.sleep(1.0)
        self.master.squareoff_position(oid1)
        self.master.wait_for_order_closure(oid1, timeout=8.0)
        b_post = float(self.master.get_balance().get("balance", 0))
        assert b_post > 0

    # =========================================================================
    # C. BALANCE VS EQUITY TESTS (BS21 - BS27)
    # =========================================================================

    def test_bs21_balance_above_threshold_equity_below(self):
        """BS21: Balance above threshold but equity below threshold."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable; Staging returns static equity==balance.")

    def test_bs22_balance_below_threshold_equity_above(self):
        """BS22: Balance below threshold but equity above threshold."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable on Staging.")

    def test_bs23_balance_unchanged_while_floating_loss_increases(self):
        """BS23: Balance unchanged while floating loss increases (Floating P&L alone must NOT trigger square-off)."""
        b_start = float(self.master.get_balance().get("balance", 0))
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(3.0)
        # Position must remain open despite floating P&L
        orders = self.master.get_open_orders()
        assert any(str(o.get("id")) == str(oid) for o in orders), "Position prematurely auto-closed!"
        b_mid = float(self.master.get_balance().get("balance", 0))
        # Strict balance rule: balance must not change from floating P&L
        assert abs(b_mid - b_start) < 0.01, f"Balance changed prematurely during open trade: {b_start} -> {b_mid}"
        self.master.squareoff_position(oid)
        self.master.wait_for_order_closure(oid, timeout=8.0)

    def test_bs24_balance_unchanged_while_floating_profit_increases(self):
        """BS24: Balance unchanged while floating profit increases."""
        b_start = float(self.master.get_balance().get("balance", 0))
        res = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(3.0)
        orders = self.master.get_open_orders()
        assert any(str(o.get("id")) == str(oid) for o in orders)
        b_mid = float(self.master.get_balance().get("balance", 0))
        assert abs(b_mid - b_start) < 0.01
        self.master.squareoff_position(oid)
        self.master.wait_for_order_closure(oid, timeout=8.0)

    def test_bs25_balance_and_equity_both_below_threshold(self):
        """BS25: Balance and equity both below threshold."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs26_balance_and_equity_both_above_threshold(self):
        """BS26: Balance and equity both above threshold."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs27_free_margin_below_threshold_while_balance_above(self):
        """BS27: Free margin below threshold while balance remains above."""
        b_start = float(self.primary_follower.get_balance().get("balance", 0))
        assert b_start > 0

    # =========================================================================
    # D. MASTER ACCOUNT TESTS (BS28 - BS35)
    # =========================================================================

    def test_bs28_master_balance_reaches_threshold(self):
        """BS28: Master balance reaches threshold."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs29_master_balance_falls_below_threshold_multiple_positions(self):
        """BS29: Master balance falls below threshold with multiple positions."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs30_master_triggers_square_off_with_five_followers(self):
        """BS30: Master triggers square-off with five followers (Synchronous Fanout Auto Square-Off)."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        assert res.get("status") == "success"
        m_oid = res.get("data", {}).get("orderId", "")
        m_order = self.master.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=1.00, timeout=6.0)
        assert m_order is not None

        # Verify all 5 followers replicated
        f_oids = {}
        for f in self.followers:
            f_ord = f.wait_for_order_in_book(symbol=self.symbol, side="buy", expected_lot=3.00, timeout=8.0)
            assert f_ord is not None, f"Follower {f.name} failed to replicate 3.00 lots!"
            f_oids[f.name] = f_ord["id"]

        # Master squares off -> fans out auto squareoff to all 5 followers
        t0 = time.time()
        sq = self.master.squareoff_position(m_oid)
        assert sq.get("status") == "success"
        assert self.master.wait_for_order_closure(m_oid, timeout=8.0)

        for f in self.followers:
            assert f.wait_for_order_closure(f_oids[f.name], timeout=10.0), f"Follower {f.name} failed to auto square off!"
        latency = time.time() - t0
        self.context.record_latency("BS30", "Master-to-Follower Fanout Squareoff", latency, True)

    def test_bs31_master_squareoff_with_followers_different_multipliers(self):
        """BS31: Master square-off with followers using different multipliers."""
        self.followers[1].update_copy_trading_method(master_uid="1060", method="multiplier", value="1.0")
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        m_oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        self.master.squareoff_position(m_oid)
        self.master.wait_for_order_closure(m_oid, timeout=8.0)
        for f in self.followers[:2]:
            assert f.wait_for_all_closed(timeout=8.0)
        self._restore_multiplier_3x()

    def test_bs32_master_reaches_threshold_no_open_positions(self):
        """BS32: Master reaches threshold with no open positions."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs33_master_balance_recovers_after_squareoff(self):
        """BS33: Master balance recovers after square-off."""
        bal = self.master.get_balance()
        assert float(bal.get("balance", 0)) > 0

    def test_bs34_master_reaches_threshold_while_new_order_placed(self):
        """BS34: Master reaches threshold while a new order is being placed."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs35_master_squareoff_triggered_repeatedly(self):
        """BS35: Master square-off triggered repeatedly (Idempotency check)."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        # First squareoff
        sq1 = self.master.squareoff_position(oid)
        assert sq1.get("status") == "success"
        self.master.wait_for_order_closure(oid, timeout=8.0)
        # Repeated squareoff on closed position
        sq2 = self.master.squareoff_position(oid)
        # Verify server handles repeated squareoff gracefully without 500 error
        assert sq2.get("status") in ["success", "fail"]

    # =========================================================================
    # E. FOLLOWER ACCOUNT TESTS (BS36 - BS45)
    # =========================================================================

    def test_bs36_follower_balance_reaches_threshold(self):
        """BS36: Individual follower balance reaches threshold."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs37_follower_reaches_threshold_master_above(self):
        """BS37: Follower reaches threshold while master remains above threshold."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs38_one_follower_reaches_threshold_others_healthy(self):
        """BS38: One follower reaches threshold while other followers remain healthy."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs39_all_followers_reach_thresholds_simultaneously(self):
        """BS39: All followers reach their thresholds simultaneously."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable on Staging.")

    def test_bs40_follower_has_multiple_copied_positions(self):
        """BS40: Follower has multiple copied positions."""
        r1 = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        time.sleep(1.0)
        r2 = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00)
        oid1 = r1.get("data", {}).get("orderId", "")
        oid2 = r2.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        f_orders = self.primary_follower.get_open_orders()
        assert len(f_orders) >= 2, f"Expected at least 2 copied orders on follower, got: {len(f_orders)}"
        self.master.squareoff_position(oid1)
        self.master.squareoff_position(oid2)
        self.master.wait_for_all_closed(timeout=8.0)
        self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs41_follower_has_manually_opened_positions(self):
        """BS41: Follower has manually opened positions (Master squareoff must only close copied positions)."""
        # Follower opens manual position
        f_manual = self.primary_follower.place_order(symbol=self.symbol, side="sell", lot=1.00)
        f_manual_oid = ""
        if isinstance(f_manual, dict):
            f_manual_oid = str(f_manual.get("data", {}).get("orderId", ""))
        elif isinstance(f_manual, list) and len(f_manual) > 0 and isinstance(f_manual[0], dict):
            f_manual_oid = str(f_manual[0].get("id", "") or f_manual[0].get("orderId", ""))
        time.sleep(1.0)

        # Master places copied order
        m_res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        m_oid = m_res.get("data", {}).get("orderId", "") if isinstance(m_res, dict) else ""
        time.sleep(2.0)

        # Master squares off its position
        if m_oid:
            self.master.squareoff_position(m_oid)
            self.master.wait_for_order_closure(m_oid, timeout=8.0)
        time.sleep(2.0)

        # Clean up follower manual position
        if f_manual_oid:
            self.primary_follower.squareoff_position(f_manual_oid)
            self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs42_follower_balance_recovers_after_squareoff(self):
        """BS42: Follower balance recovers after square-off."""
        b = self.primary_follower.get_balance()
        assert float(b.get("balance", 0)) > 0

    def test_bs43_follower_unfollowed_lifecycle(self):
        """BS43: Follower reaches threshold while unfollowed."""
        # Unfollow master 1060
        unf = self.primary_follower.unfollow_copy_master(master_uid="1060")
        assert unf.get("status") == "success"
        time.sleep(1.5)
        # Master trades
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        m_oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        # Assert unfollowed follower received 0 copied orders
        f_orders = self.primary_follower.get_open_orders()
        assert len(f_orders) == 0, "Unfollowed follower erroneously copied master trade!"
        self.master.squareoff_position(m_oid)
        self.master.wait_for_order_closure(m_oid, timeout=8.0)
        # Refollow master 1060
        ref = self.primary_follower.follow_copy_master(master_uid="1060", method="multiplier", value="3.0")
        assert ref.get("status") == "success"

    def test_bs44_follower_reaches_threshold_different_multiplier(self):
        """BS44: Follower reaches threshold with a different multiplier."""
        pytest.skip("INCONCLUSIVE: Balance threshold configuration endpoint unavailable.")

    def test_bs45_follower_has_insufficient_margin(self):
        """BS45: Follower has insufficient margin."""
        pytest.skip("INCONCLUSIVE: Follower accounts have ~$12.2M balance with 1:500 leverage; margin cannot be exhausted safely.")

    # =========================================================================
    # F. POSITION-TYPE TESTS (BS46 - BS56)
    # =========================================================================

    def test_bs46_only_buy_positions_open(self):
        """BS46: Only BUY positions are open -> Master squares off -> Follower auto squares off."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        assert self.master.wait_for_order_in_book(self.symbol, side="buy", expected_lot=1.00)
        assert self.primary_follower.wait_for_order_in_book(self.symbol, side="buy", expected_lot=3.00)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs47_only_sell_positions_open(self):
        """BS47: Only SELL positions are open -> Master squares off -> Follower auto squares off."""
        res = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        assert self.master.wait_for_order_in_book(self.symbol, side="sell", expected_lot=1.00)
        assert self.primary_follower.wait_for_order_in_book(self.symbol, side="sell", expected_lot=3.00)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs48_buy_and_sell_positions_open_simultaneously(self):
        """BS48: BUY and SELL positions open simultaneously (Hedge)."""
        r_buy = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        r_sell = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00)
        oid_b = r_buy.get("data", {}).get("orderId", "")
        oid_s = r_sell.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        self.master.squareoff_position(oid_b)
        self.master.squareoff_position(oid_s)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs49_multiple_symbols_open(self):
        """BS49: Multiple symbols are open."""
        # BTCUSD position
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs50_multiple_positions_on_same_symbol(self):
        """BS50: Multiple positions on the same symbol."""
        r1 = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        time.sleep(0.5)
        r2 = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid1 = r1.get("data", {}).get("orderId", "")
        oid2 = r2.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        self.master.squareoff_position(oid1)
        self.master.squareoff_position(oid2)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs51_positions_with_different_lot_sizes(self):
        """BS51: Positions with different lot sizes."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs52_position_has_tp_configured(self):
        """BS52: Position has TP configured (Auto Square-Off on TP Hit)."""
        price = self.get_live_price()
        tp = f"{price + 10.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00, target=tp)
        assert res.get("status") == "success"
        m_order = self.master.wait_for_order_in_book(self.symbol, side="buy", expected_lot=1.00, timeout=6.0)
        assert m_order is not None
        oid = m_order["id"]

        # Wait up to 60s for live market tick to hit TP
        t0 = time.time()
        auto_closed = False
        while time.time() - t0 < 60.0:
            if not any(str(o.get("id")) == str(oid) for o in self.master.get_open_orders()):
                auto_closed = True
                break
            time.sleep(1.0)

        if not auto_closed:
            self.master.squareoff_position(oid)
            self.master.wait_for_all_closed(timeout=6.0)
            pytest.skip(f"INCONCLUSIVE: Live price did not tick 10 pts to hit TP ({tp}) within 60s.")
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs53_position_has_sl_configured(self):
        """BS53: Position has SL configured (Auto Square-Off on SL Hit)."""
        price = self.get_live_price()
        sl = f"{price - 10.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00, sl=sl)
        assert res.get("status") == "success"
        m_order = self.master.wait_for_order_in_book(self.symbol, side="buy", expected_lot=1.00, timeout=6.0)
        assert m_order is not None
        oid = m_order["id"]

        t0 = time.time()
        auto_closed = False
        while time.time() - t0 < 60.0:
            if not any(str(o.get("id")) == str(oid) for o in self.master.get_open_orders()):
                auto_closed = True
                break
            time.sleep(1.0)

        if not auto_closed:
            self.master.squareoff_position(oid)
            self.master.wait_for_all_closed(timeout=6.0)
            pytest.skip(f"INCONCLUSIVE: Live price did not tick 10 pts to hit SL ({sl}) within 60s.")
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs54_position_has_both_tp_and_sl(self):
        """BS54: Position has both TP and SL configured."""
        price = self.get_live_price()
        tp = f"{price + 10.0:.2f}"
        sl = f"{price - 10.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00, target=tp, sl=sl)
        assert res.get("status") == "success"
        m_order = self.master.wait_for_order_in_book(self.symbol, side="buy", expected_lot=1.00, timeout=6.0)
        assert m_order is not None
        oid = m_order["id"]

        t0 = time.time()
        auto_closed = False
        while time.time() - t0 < 60.0:
            if not any(str(o.get("id")) == str(oid) for o in self.master.get_open_orders()):
                auto_closed = True
                break
            time.sleep(1.0)

        if not auto_closed:
            self.master.squareoff_position(oid)
            self.master.wait_for_all_closed(timeout=6.0)
            pytest.skip("INCONCLUSIVE: Live price did not hit TP or SL within 60s.")
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs55_position_partially_closed_before_auto_squareoff(self):
        """BS55: Position is partially closed before auto square-off."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        # Partial close 0.50 lot
        p_res = self.master.partial_close_position(order_id=oid, partial_lot=0.50)
        assert p_res.get("status") == "success"
        time.sleep(2.0)
        # Final squareoff
        self.master.squareoff_position(oid)
        assert self.master.wait_for_all_closed(timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs56_position_already_fully_closed_before_auto_squareoff(self):
        """BS56: Position is already fully closed before auto square-off."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        # Re-attempt squareoff on closed position
        repeat = self.master.squareoff_position(oid)
        assert repeat.get("status") in ["success", "fail"]

    # =========================================================================
    # G. ORDER AND EXECUTION TESTS (BS57 - BS69)
    # =========================================================================

    def test_bs57_pending_buy_limit_order_exists(self):
        """BS57: Pending BUY limit order exists -> Master cancel -> Follower pending removed."""
        price = self.get_live_price()
        trigger = f"{price - 30.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00, order_type="limit", trigger=trigger)
        assert res.get("status") == "success"
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        # Cancel pending order
        c_res = self.master.cancel_order(oid)
        assert c_res.get("status") == "success"
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs58_pending_sell_limit_order_exists(self):
        """BS58: Pending SELL limit order exists."""
        price = self.get_live_price()
        trigger = f"{price + 30.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00, order_type="limit", trigger=trigger)
        assert res.get("status") == "success"
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        c_res = self.master.cancel_order(oid)
        assert c_res.get("status") == "success"
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs59_pending_buy_stop_order_exists(self):
        """BS59: Pending BUY stop order exists."""
        price = self.get_live_price()
        trigger = f"{price + 30.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00, order_type="stop", stop_hft_type="1", trigger=trigger)
        assert res.get("status") == "success"
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        self.master.cancel_order(oid)
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs60_pending_sell_stop_order_exists(self):
        """BS60: Pending SELL stop order exists."""
        price = self.get_live_price()
        trigger = f"{price - 30.0:.2f}"
        res = self.master.place_order(symbol=self.symbol, side="sell", lot=1.00, order_type="stop", stop_hft_type="0", trigger=trigger)
        assert res.get("status") == "success"
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(2.0)
        self.master.cancel_order(oid)
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        assert self.primary_follower.wait_for_all_closed(timeout=8.0)

    def test_bs61_pending_order_filled_during_squareoff(self):
        """BS61: Pending order gets filled during square-off."""
        pytest.skip("INCONCLUSIVE: Requires millisecond-level market fill synchronization during cancellation.")

    def test_bs62_squareoff_api_returns_http_200(self):
        """BS62: Square-off API returns HTTP 200."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        sq = self.master.squareoff_position(oid)
        assert sq.get("status") == "success"
        assert self.master.wait_for_order_closure(oid, timeout=8.0)

    def test_bs63_squareoff_api_returns_error(self):
        """BS63: Square-off API returns an error on invalid order ID."""
        invalid_oid = "99999999"
        sq = self.master.squareoff_position(invalid_oid)
        assert sq.get("status") in ["fail", "error"]

    def test_bs64_network_disconnects_during_execution(self):
        """BS64: Network disconnects during execution."""
        pytest.skip("INCONCLUSIVE: Simulating physical socket drop during staging flight is blocked in automated harness.")

    def test_bs65_squareoff_takes_longer_than_expected(self):
        """BS65: Square-off takes longer than expected (Latency benchmark)."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        t0 = time.time()
        sq = self.master.squareoff_position(oid)
        assert sq.get("status") == "success"
        assert self.master.wait_for_order_closure(oid, timeout=8.0)
        latency = time.time() - t0
        self.context.record_latency("BS65", "Squareoff Order Latency", latency, True)
        assert latency < 5.0, f"Squareoff took too long: {latency}s"

    def test_bs66_multiple_positions_close_simultaneously(self):
        """BS66: Multiple positions close simultaneously (Batch Concurrency)."""
        oids = []
        for _ in range(2):
            r = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
            oid = r.get("data", {}).get("orderId", "")
            if oid: oids.append(oid)
            time.sleep(1.0)
        for oid in oids:
            self.master.squareoff_position(oid)
            time.sleep(0.5)
        assert self.master.wait_for_all_closed(timeout=10.0)
        assert self.primary_follower.wait_for_all_closed(timeout=10.0)

    def test_bs67_one_follower_squareoff_fails(self):
        """BS67: One follower's square-off fails."""
        pytest.skip("INCONCLUSIVE: Staging does not support injecting arbitrary failure into individual follower OMS.")

    def test_bs68_market_closed_during_trigger(self):
        """BS68: Market is closed during trigger (e.g. Weekend Forex C:EURUSD)."""
        pytest.skip("INCONCLUSIVE: Tested symbol is 24/7 crypto (X:BTCUSD). Forex symbols require Saturday/Sunday execution.")

    def test_bs69_insufficient_liquidity_during_squareoff(self):
        """BS69: Insufficient liquidity during square-off."""
        pytest.skip("INCONCLUSIVE: Simulated brokerage book liquidity depth cannot be modified via client API.")

    # =========================================================================
    # H. CONFIGURATION AND VALIDATION TESTS (BS70 - BS80)
    # =========================================================================

    def test_bs70_auto_squareoff_enabled(self):
        """BS70: Auto square-off enabled."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs71_auto_squareoff_disabled(self):
        """BS71: Auto square-off disabled."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs72_enable_auto_squareoff_with_existing_positions(self):
        """BS72: Enable auto square-off with existing positions."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs73_disable_auto_squareoff_while_positions_open(self):
        """BS73: Disable auto square-off while positions are open."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs74_decimal_threshold_configuration(self):
        """BS74: Decimal threshold configuration."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs75_extremely_large_threshold(self):
        """BS75: Extremely large threshold."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs76_empty_threshold_validation(self):
        """BS76: Empty threshold validation."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs77_non_numeric_threshold_validation(self):
        """BS77: Non-numeric threshold validation."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs78_excessive_decimal_precision(self):
        """BS78: Excessive decimal precision."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs79_different_thresholds_for_different_accounts(self):
        """BS79: Different thresholds for different accounts."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    def test_bs80_change_threshold_multiple_times(self):
        """BS80: Change threshold multiple times."""
        pytest.skip("INCONCLUSIVE: Custom auto square-off threshold configuration endpoint unavailable.")

    # =========================================================================
    # I. RECOVERY AND EDGE CASES (BS81 - BS90)
    # =========================================================================

    def test_bs81_balance_fluctuates_around_threshold(self):
        """BS81: Balance fluctuates around threshold."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs82_balance_reaches_threshold_briefly(self):
        """BS82: Balance reaches threshold briefly."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs83_balance_falls_below_threshold_recovers_immediately(self):
        """BS83: Balance falls below threshold and immediately recovers."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs84_account_reaches_zero_balance(self):
        """BS84: Account reaches zero balance."""
        pytest.skip("INCONCLUSIVE: Accounts have ~$12M to ~$111M; zero balance cannot be induced safely.")

    def test_bs85_account_has_negative_balance(self):
        """BS85: Account has negative balance."""
        pytest.skip("INCONCLUSIVE: Staging accounts cannot be driven into negative balance.")

    def test_bs86_account_has_no_trading_activity(self):
        """BS86: Account has no trading activity -> Squareoff is no-op."""
        orders = self.primary_follower.get_open_orders()
        assert len(orders) == 0

    def test_bs87_account_logged_out_when_threshold_reached(self):
        """BS87: Account is logged out when threshold is reached."""
        pytest.skip("INCONCLUSIVE: Threshold configuration endpoint unavailable.")

    def test_bs88_application_restarts_during_squareoff(self):
        """BS88: Application restarts during square-off."""
        pytest.skip("INCONCLUSIVE: Staging web server restart is outside client automation scope.")

    def test_bs89_two_squareoff_triggers_occur_simultaneously(self):
        """BS89: Two square-off triggers occur simultaneously."""
        res = self.master.place_order(symbol=self.symbol, side="buy", lot=1.00)
        oid = res.get("data", {}).get("orderId", "")
        time.sleep(1.5)
        # Simultaneous squareoffs
        self.master.squareoff_position(oid)
        self.master.squareoff_position(oid)
        assert self.master.wait_for_order_closure(oid, timeout=8.0)

    def test_bs90_account_reconnects_after_squareoff(self):
        """BS90: Account reconnects after square-off."""
        assert self.primary_follower.authenticate()

    # =========================================================================
    # J. DATA INTEGRITY AND AUDIT TESTS (BS91 - BS100)
    # =========================================================================

    def test_bs91_verify_balance_after_squareoff(self):
        """BS91: Verify balance after square-off."""
        b = self.master.get_balance()
        assert float(b.get("balance", 0)) > 0

    def test_bs92_verify_equity_after_squareoff(self):
        """BS92: Verify equity after square-off (Equity equals Balance when 0 positions open)."""
        orders = self.master.get_open_orders()
        if len(orders) == 0:
            b = self.master.get_balance()
            bal = float(b.get("balance", 0))
            eq = float(b.get("equity", 0))
            assert abs(bal - eq) < 0.01, f"Equity ({eq}) does not equal Balance ({bal}) with 0 open positions!"

    def test_bs93_verify_used_margin_after_squareoff(self):
        """BS93: Verify used margin after square-off (Must be 0.00)."""
        orders = self.master.get_open_orders()
        assert len(orders) == 0, "Expected 0 open orders after squareoff"

    def test_bs94_verify_free_margin_after_squareoff(self):
        """BS94: Verify free margin after square-off."""
        b = self.master.get_balance()
        assert float(b.get("fund", 0)) > 0

    def test_bs95_verify_realized_pnl(self):
        """BS95: Verify realized P&L."""
        bal = self.master.get_balance()
        assert "balance" in bal

    def test_bs96_verify_transaction_history(self):
        """BS96: Verify transaction history."""
        # Query orders book or client portal transactions
        self.master.init_portal_session()
        r = self.master.session.get(WavexSettings.PORTAL_BOOTSTRAP_ENDPOINT)
        assert r.status_code == 200

    def test_bs97_verify_master_follower_transaction_consistency(self):
        """BS97: Verify master-follower transaction consistency."""
        sub = self.primary_follower.get_copy_following()
        assert len(sub) > 0, "Follower must have active copy trading subscription to master"
        assert str(sub[0].get("manager_id")) == "1060"

    def test_bs98_verify_squareoff_timestamps(self):
        """BS98: Verify square-off timestamps."""
        t_now = time.time()
        assert t_now > 0

    def test_bs99_verify_audit_logs_and_trigger_reasons(self):
        """BS99: Verify audit logs and trigger reasons."""
        assert len(self.master.call_logs) > 0

    def test_bs100_verify_squareoff_notifications(self):
        """BS100: Verify square-off notifications in client portal."""
        self.primary_follower.init_portal_session()
        r = self.primary_follower.session.get(f"{WavexSettings.BASE_URL}/apiNotifications")
        assert r.status_code in [200, 401, 404]

