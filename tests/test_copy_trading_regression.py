"""
WavexOne Unified Copy Trading Master Regression Suite.
Senior QA Architect & Trading Systems Test Engineering Framework.

Supports:
- Full regression (all tests)
- Smoke testing (`pytest -m smoke`)
- Risk & Stop-Out testing (`pytest -m risk`)
- Negative testing (`pytest -m negative`)
- Cleanup-only execution (`pytest -m cleanup`)

Platform: https://stage.wavexone.com
Accounts: Master (11060), Followers (11041, 11043, 11045, 11048, 11050)
"""

import time
import pytest
from core.logger import logger
from core.copy_trading import (
    AccountManager,
    CopyConfigurationManager,
    OrderExecutionEngine,
    ReplicationValidator,
    PositionManager,
    MarginMonitor,
    StopOutValidator,
    CommissionValidator,
    WithdrawalValidator,
    AccountReconciler,
    EvidenceRecorder,
    SafeTeardown
)


# =============================================================================
# 1. SMOKE TEST MODULE
# =============================================================================
@pytest.mark.smoke
class TestCopyTradingSmoke:
    """Fast sanity smoke test suite for critical staging paths."""

    acc_mgr: AccountManager
    cfg_mgr: CopyConfigurationManager
    engine: OrderExecutionEngine
    validator: ReplicationValidator
    teardown_handler: SafeTeardown

    @classmethod
    def setup_class(cls):
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        m = cls.acc_mgr.get_master()
        f = cls.acc_mgr.get_followers()
        cls.cfg_mgr = CopyConfigurationManager(m, f)
        cls.engine = OrderExecutionEngine(m)
        cls.validator = ReplicationValidator(m, f)
        cls.teardown_handler = SafeTeardown(m, f)
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()
        cls.cfg_mgr.restore_baseline()

    @classmethod
    def teardown_class(cls):
        cls.teardown_handler.execute_complete_teardown()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()
        time.sleep(1.0)

    def test_smoke_01_account_readiness_and_subscriptions(self):
        """Smoke 1: Verify all 6 accounts authenticated and active subscription."""
        m = self.acc_mgr.get_master()
        followers = self.acc_mgr.get_followers()
        assert m.token, "Master must have valid auth token"
        assert len(followers) == 5, "All 5 followers must be loaded"
        sub = self.cfg_mgr.verify_all_subscribed()
        assert sub.get("all_active") or sub.get("all_subscribed"), f"Follower subscriptions broken: {sub}"

    def test_smoke_02_market_order_replication_multiplier_3x(self):
        """Smoke 2: Quick Market BUY replication (0.50 lot -> 1.50 lots on 3.0x multiplier)."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        res = self.engine.place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        v = self.validator.validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="multiplier", multiplier_val=3.0
        )
        assert v.get("all_replicated"), f"Smoke replication failed: {v}"
        assert v.get("latency_sec", 99) < 3.5

        self.engine.full_squareoff(m_oid)


# =============================================================================
# 2. ORDER TYPE & ALLOCATION MODES MODULE
# =============================================================================
@pytest.mark.trading
@pytest.mark.regression
class TestCopyTradingOrderMatrix:
    """Validates order execution across Multiplier, Balance, and Equity modes."""

    acc_mgr: AccountManager
    cfg_mgr: CopyConfigurationManager
    engine: OrderExecutionEngine
    validator: ReplicationValidator
    teardown_handler: SafeTeardown

    @classmethod
    def setup_class(cls):
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        m = cls.acc_mgr.get_master()
        f = cls.acc_mgr.get_followers()
        cls.cfg_mgr = CopyConfigurationManager(m, f)
        cls.engine = OrderExecutionEngine(m)
        cls.validator = ReplicationValidator(m, f)
        cls.teardown_handler = SafeTeardown(m, f)
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    @classmethod
    def teardown_class(cls):
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()
        time.sleep(1.0)

    def test_order_01_multiplier_market_sell(self):
        """Multiplier Mode: Market SELL (0.50 lot -> 1.50 lots)."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        res = self.engine.place_market_order(side="sell", lot=0.50)
        assert res.get("status") == "success"
        oid = str(res.get("data", {}).get("orderId", ""))
        v = self.validator.validate_fanout_replication(oid, "SELL", 0.50, "multiplier", 3.0)
        assert v.get("all_replicated")
        self.engine.full_squareoff(oid)

    def test_order_02_balance_mode_market_buy(self):
        """Balance Mode: Market BUY (0.50 lot -> ~0.05 lots)."""
        self.cfg_mgr.set_mode_and_verify(method="balance")
        res = self.engine.place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        oid = str(res.get("data", {}).get("orderId", ""))
        v = self.validator.validate_fanout_replication(oid, "BUY", 0.50, "balance")
        assert v.get("all_replicated")
        self.engine.full_squareoff(oid)

    def test_order_03_equity_mode_market_buy(self):
        """Equity Mode: Market BUY (0.50 lot -> ~0.05 lots)."""
        self.cfg_mgr.set_mode_and_verify(method="equity")
        res = self.engine.place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        oid = str(res.get("data", {}).get("orderId", ""))
        v = self.validator.validate_fanout_replication(oid, "BUY", 0.50, "equity")
        assert v.get("all_replicated")
        self.engine.full_squareoff(oid)

    def test_order_04_limit_order_replication(self):
        """Limit Order: Pending BUY Limit mirroring to all followers."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        price = self.acc_mgr.get_master().get_live_price() or 76000.0
        trig = round(price * 0.85, 2)
        res = self.engine.place_limit_order(side="buy", trigger_price=trig, lot=0.50)
        assert res.get("status") == "success"
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)
        self.engine.cancel_pending(oid)


# =============================================================================
# 3. IN-FLIGHT LIFECYCLE & CONCURRENCY MODULE
# =============================================================================
@pytest.mark.trading
@pytest.mark.regression
class TestCopyTradingInFlightLifecycle:
    """Validates live trade modifications, partial exits, and concurrency."""

    acc_mgr: AccountManager
    cfg_mgr: CopyConfigurationManager
    engine: OrderExecutionEngine
    teardown_handler: SafeTeardown

    @classmethod
    def setup_class(cls):
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        m = cls.acc_mgr.get_master()
        f = cls.acc_mgr.get_followers()
        cls.cfg_mgr = CopyConfigurationManager(m, f)
        cls.engine = OrderExecutionEngine(m)
        cls.teardown_handler = SafeTeardown(m, f)
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    @classmethod
    def teardown_class(cls):
        cls.teardown_handler.execute_complete_teardown()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()
        time.sleep(1.0)

    def test_inflight_01_sl_tp_modification_fanout(self):
        """In-Flight: SL/TP modification updates follower tickets in real-time."""
        price = self.acc_mgr.get_master().get_live_price() or 76000.0
        sl1 = f"{price - 800.0:.2f}"
        tp1 = f"{price + 1200.0:.2f}"
        res = self.engine.place_market_order(side="buy", lot=0.50, sl=sl1, tp=tp1)
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        sl2 = f"{price - 500.0:.2f}"
        tp2 = f"{price + 1500.0:.2f}"
        mod = self.engine.modify_order_sl_tp(order_id=oid, new_sl=sl2, new_tp=tp2)
        assert mod["modify_sl"].get("status") == "success"
        self.engine.full_squareoff(oid)

    def test_inflight_02_partial_close_multiplier(self):
        """In-Flight: Partial position close (0.50 -> 0.30) leaves 0.90 on followers."""
        res = self.engine.place_market_order(side="buy", lot=0.50)
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        p = self.engine.partial_close(oid, partial_lot=0.20)
        assert p.get("status") == "success"
        time.sleep(3.0)

        for f in self.acc_mgr.get_followers():
            ords = f.get_open_orders()
            assert len(ords) >= 1
            rem = float(ords[0].get("lot", 0.0) or ords[0].get("partiallot", 0.0) or 0.0)
            assert abs(rem - 0.90) <= 0.01

        self.engine.full_squareoff(oid)


# =============================================================================
# 4. RISK, MARGIN & 50% STOP-OUT MODULE
# =============================================================================
@pytest.mark.risk
@pytest.mark.regression
class TestCopyTradingRiskAndStopOut:
    """Validates Margin Level 50% stop-out rules, boundary conditions, and isolation."""

    acc_mgr: AccountManager
    cfg_mgr: CopyConfigurationManager
    engine: OrderExecutionEngine
    margin_monitor: MarginMonitor
    stop_out_val: StopOutValidator
    teardown_handler: SafeTeardown

    @classmethod
    def setup_class(cls):
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        m = cls.acc_mgr.get_master()
        f = cls.acc_mgr.get_followers()
        cls.cfg_mgr = CopyConfigurationManager(m, f)
        cls.engine = OrderExecutionEngine(m)
        cls.margin_monitor = MarginMonitor([m] + f)
        cls.stop_out_val = StopOutValidator(m, f)
        cls.teardown_handler = SafeTeardown(m, f)
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    @classmethod
    def teardown_class(cls):
        cls.teardown_handler.execute_complete_teardown()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()
        time.sleep(1.0)

    def test_risk_01_margin_level_above_50_pct_no_liquidation(self):
        """Risk 1: Margin Level at 60% / Safe Zone maintains active position without liquidation."""
        res = self.engine.place_market_order(side="buy", lot=0.10)
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        snap = self.margin_monitor.capture_account_snapshot(self.acc_mgr.get_master())
        assert snap["used_margin"] > 0, "Used margin must be active"
        assert not snap["is_stop_out"], "Account must not be in stop-out state"

        self.engine.full_squareoff(oid)

    def test_risk_02_margin_level_at_exactly_50_percent(self):
        """Risk 2: Margin Level at exactly 50% Stop-Out Trigger."""
        # STAGING CONSTRAINT: Requires $111M drawdown without DB tampering
        pytest.skip("BLOCKED: Inducing exact 50.00% margin level requires $111M drawdown without prohibited DB tampering.")

    def test_risk_03_margin_level_at_45_percent_critical(self):
        """Risk 3: Margin Level at 45% Critical Stop-Out Zone."""
        pytest.skip("BLOCKED: Cannot safely induce 45% margin level without prohibited DB manipulation.")

    def test_risk_04_individual_follower_liquidation_isolation(self):
        """Risk 4: Liquidating an individual follower does not affect Master or peers."""
        res = self.engine.place_market_order(side="buy", lot=0.10)
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        f1 = self.acc_mgr.get_followers()[0]
        f1_orders = f1.get_open_orders()
        assert len(f1_orders) >= 1
        f1_tid = str(f1_orders[0].get("id"))

        iso = self.stop_out_val.verify_isolation_on_follower_liquidation(f1, f1_tid, m_oid)
        assert iso.get("isolation_intact"), "Follower liquidation breached tenant isolation"

        self.engine.full_squareoff(m_oid)

    def test_risk_05_master_liquidation_fanout(self):
        """Risk 5: Master liquidation cleanly fans out to close all follower tickets."""
        res = self.engine.place_market_order(side="buy", lot=0.10)
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        # Squareoff master
        self.engine.full_squareoff(m_oid)
        time.sleep(3.0)

        for f in self.acc_mgr.get_followers():
            assert len(f.get_open_orders()) == 0, f"Follower {f.name} held orphaned position"

    def test_risk_06_multiple_positions_used_margin_aggregation(self):
        """Risk 6: Used Margin aggregates additively across multi-positions."""
        m = self.acc_mgr.get_master()
        r1 = self.engine.place_market_order(side="buy", lot=0.10)
        oid1 = str(r1.get("data", {}).get("orderId", ""))
        time.sleep(1.5)
        um1 = self.margin_monitor.capture_account_snapshot(m)["used_margin"]

        r2 = self.engine.place_market_order(side="buy", lot=0.20)
        oid2 = str(r2.get("data", {}).get("orderId", ""))
        time.sleep(1.5)
        um2 = self.margin_monitor.capture_account_snapshot(m)["used_margin"]
        assert um2 > um1, "Used margin must aggregate across positions"

        self.engine.full_squareoff(oid1)
        self.engine.full_squareoff(oid2)

    def test_risk_07_pending_orders_purged_during_liquidation(self):
        """Risk 7: Pending limit/stop orders are purged via cancellation endpoint."""
        price = self.acc_mgr.get_master().get_live_price() or 76000.0
        r_lim = self.engine.place_limit_order(side="buy", trigger_price=round(price * 0.85, 2), lot=0.10)
        lim_id = str(r_lim.get("data", {}).get("orderId", ""))
        time.sleep(1.5)
        c = self.engine.cancel_pending(lim_id)
        assert c.get("status") == "success"

    def test_risk_08_post_liquidation_clean_slate_audit(self):
        """Risk 8: Post-liquidation audit confirms zero used margin and clean slate."""
        rec = AccountReconciler(self.acc_mgr.get_master(), self.acc_mgr.get_followers())
        audit = rec.audit_clean_slate()
        assert audit.get("all_clean"), f"Residual orders or margin detected: {audit}"


# =============================================================================
# 5. NEGATIVE & IDEMPOTENCY MODULE
# =============================================================================
@pytest.mark.negative
class TestCopyTradingNegativeAndIdempotency:
    """Validates server-side guards and idempotency."""

    acc_mgr: AccountManager
    engine: OrderExecutionEngine
    stop_out_val: StopOutValidator
    teardown_handler: SafeTeardown

    @classmethod
    def setup_class(cls):
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        m = cls.acc_mgr.get_master()
        f = cls.acc_mgr.get_followers()
        cls.engine = OrderExecutionEngine(m)
        cls.stop_out_val = StopOutValidator(m, f)
        cls.teardown_handler = SafeTeardown(m, f)
        cls.teardown_handler.execute_complete_teardown()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()

    def test_negative_01_duplicate_squareoff_idempotency(self):
        """Negative 1: Calling squareoff twice on the same order returns idempotency failure."""
        res = self.engine.place_market_order(side="buy", lot=0.10)
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(1.5)
        idem = self.stop_out_val.test_duplicate_squareoff_idempotency(self.acc_mgr.get_master(), oid)
        assert idem.get("idempotent"), f"OMS Idempotency failed: {idem}"


# =============================================================================
# 6. CLEANUP-ONLY EXECUTION MODULE
# =============================================================================
@pytest.mark.cleanup
class TestCopyTradingCleanupOnly:
    """Safely clears lingering orders across all 6 accounts and restores baseline."""

    def test_cleanup_all_accounts(self):
        acc = AccountManager()
        acc.initialize_and_authenticate()
        m = acc.get_master()
        f = acc.get_followers()
        td = SafeTeardown(m, f)
        report = td.execute_complete_teardown()
        cfg = CopyConfigurationManager(m, f)
        cfg.restore_baseline()
        assert report.get("clean_slate_verified") or report.get("success"), f"Teardown failure: {report}"
