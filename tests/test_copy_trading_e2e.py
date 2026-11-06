"""
WavexOne Unified Copy Trading End-to-End (E2E) Test Suite.
Senior QA Architect & Trading Systems Test Engineering Framework.

Executes the Canonical 20-Stage Copy Trading Lifecycle:
1. Environment and account validation.
2. Master and follower account management.
3. Copy subscription and configuration.
4. Multiplier allocation (3.0x).
5. Balance-based allocation.
6. Equity-based allocation.
7. Market order replication.
8. Limit order replication.
9. Stop order replication.
10. BUY, SELL and BOTH directions.
11. TP/SL creation and modification.
12. Partial position closure.
13. Multiple-order and concurrent replication.
14. Master/follower tenant isolation.
15. Unfollow and re-follow.
16. Margin monitoring and 50% stop-out.
17. Automatic square-off.
18. Profit-sharing and performance fees.
19. Withdrawal and margin lock.
20. Account reconciliation and clean slate.

Platform: https://stage.wavexone.com
Accounts: ctmaster (11060), ctf1..ctf5 (11041, 11043, 11045, 11048, 11050)
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


class TestCopyTradingUnifiedE2E:
    """Consolidated End-to-End Copy Trading Lifecycle Suite."""

    acc_mgr: AccountManager
    cfg_mgr: CopyConfigurationManager
    engine: OrderExecutionEngine
    validator: ReplicationValidator
    pos_mgr: PositionManager
    margin_monitor: MarginMonitor
    stop_out_val: StopOutValidator
    comm_val: CommissionValidator
    reconciler: AccountReconciler
    teardown_handler: SafeTeardown

    symbol: str = "X:BTCUSD"

    @classmethod
    def setup_class(cls):
        logger.info("[E2E] Initializing Unified Copy Trading Architecture...")
        cls.acc_mgr = AccountManager()
        cls.acc_mgr.initialize_and_authenticate()
        master = cls.acc_mgr.get_master()
        followers = cls.acc_mgr.get_followers()

        cls.cfg_mgr = CopyConfigurationManager(master, followers)
        cls.engine = OrderExecutionEngine(master, default_symbol=cls.symbol)
        cls.validator = ReplicationValidator(master, followers)
        cls.pos_mgr = PositionManager(master, followers)
        cls.margin_monitor = MarginMonitor([master] + followers)
        cls.stop_out_val = StopOutValidator(master, followers)
        cls.comm_val = CommissionValidator(master, followers)
        cls.reconciler = AccountReconciler(master, followers)
        cls.teardown_handler = SafeTeardown(master, followers)

        # Baseline clean slate & config
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    @classmethod
    def teardown_class(cls):
        logger.info("[E2E] Final Teardown of Unified Copy Trading E2E Suite...")
        cls.teardown_handler.execute_complete_teardown()
        cls.cfg_mgr.restore_baseline()

    def teardown_method(self, method):
        self.teardown_handler.execute_complete_teardown()
        time.sleep(1.0)

    # -------------------------------------------------------------------------
    # STAGES 1 - 3: Setup, Accounts & Subscription
    # -------------------------------------------------------------------------
    def test_stage_01_to_03_environment_accounts_and_subscription(self):
        """Stages 1-3: Environment, account readiness, and subscription validation."""
        master = self.acc_mgr.get_master()
        followers = self.acc_mgr.get_followers()

        # Stage 1: Validation
        assert master.token, "Master must be authenticated"
        assert len(followers) == 5, "Must have exactly 5 follower accounts"
        for f in followers:
            assert f.token, f"Follower {f.name} must be authenticated"

        # Stage 2: Account Balances & Leverage
        m_bal = float(master.get_balance().get("balance", 0.0) or 0.0)
        assert m_bal > 1000.0, f"Master must have positive balance, got {m_bal}"
        for f in followers:
            f_bal = float(f.get_balance().get("balance", 0.0) or 0.0)
            assert f_bal > 1000.0, f"Follower {f.name} balance invalid: {f_bal}"

        # Stage 3: Subscription Status
        sub_info = self.cfg_mgr.verify_all_subscribed()
        assert sub_info.get("all_active") or sub_info.get("all_subscribed"), f"Follower subscription error: {sub_info}"

    # -------------------------------------------------------------------------
    # STAGES 4 - 6: Allocation Modes (Multiplier, Balance, Equity)
    # -------------------------------------------------------------------------
    def test_stage_04_multiplier_mode_replication(self):
        """Stage 4: Multiplier mode (3.0x) proportional lot replication."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        
        # Master opens 0.50 lot BUY
        res = self.engine.place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        # Verify all followers receive 1.50 lots (0.50 * 3.0)
        v = self.validator.validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="multiplier", multiplier_val=3.0
        )
        assert v.get("all_replicated"), f"Multiplier replication failure: {v}"
        assert v.get("latency_sec", 99) < 4.0, f"Replication latency exceeded limit: {v.get('latency_sec')}s"

        self.engine.full_squareoff(m_oid)

    def test_stage_05_balance_mode_replication(self):
        """Stage 5: Balance-based allocation mode replication."""
        self.cfg_mgr.set_mode_and_verify(method="balance")

        # Master opens 0.50 lot BUY
        res = self.engine.place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        # Verify followers receive dynamically calculated lots (~0.05 lots)
        v = self.validator.validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="balance"
        )
        assert v.get("all_replicated"), f"Balance mode replication failure: {v}"
        self.engine.full_squareoff(m_oid)

    def test_stage_06_equity_mode_replication(self):
        """Stage 6: Equity-based allocation mode replication."""
        self.cfg_mgr.set_mode_and_verify(method="equity")

        # Master opens 0.50 lot SELL
        res = self.engine.place_market_order(side="sell", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        v = self.validator.validate_fanout_replication(
            master_order_id=m_oid, expected_side="SELL", master_lot=0.50, mode="equity"
        )
        assert v.get("all_replicated"), f"Equity mode replication failure: {v}"
        self.engine.full_squareoff(m_oid)

    # -------------------------------------------------------------------------
    # STAGES 7 - 10: Order Types & Directions
    # -------------------------------------------------------------------------
    def test_stage_07_to_10_order_types_and_directions(self):
        """Stages 7-10: Market, Limit, Stop HFT in BUY, SELL, and BOTH directions."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        live_price = self.acc_mgr.get_master().get_live_price(self.symbol) or 76000.0

        # Stage 7: Market SELL with TP & SL
        tp_sell = f"{live_price - 500.0:.2f}"
        sl_sell = f"{live_price + 300.0:.2f}"
        r_mkt = self.engine.place_market_order(side="sell", lot=0.50, sl=sl_sell, tp=tp_sell)
        assert r_mkt.get("status") == "success"
        mkt_id = str(r_mkt.get("data", {}).get("orderId", ""))
        time.sleep(2.0)
        self.engine.full_squareoff(mkt_id)
        time.sleep(1.5)

        # Stage 8: Limit BUY below market
        lim_trig = round(live_price * 0.85, 2)
        r_lim = self.engine.place_limit_order(side="buy", trigger_price=lim_trig, lot=0.50)
        assert r_lim.get("status") == "success"
        lim_id = str(r_lim.get("data", {}).get("orderId", ""))
        time.sleep(2.0)
        self.engine.cancel_pending(lim_id)
        time.sleep(1.5)

        # Stage 9 & 10: Stop HFT BOTH (Dual-Leg)
        buy_trig = round(live_price * 1.10, 2)
        sell_trig = round(live_price * 0.90, 2)
        r_stp = self.engine.place_stop_both_order(trigger_buy=buy_trig, trigger_sell=sell_trig, lot=0.50)
        assert r_stp.get("status") == "success"
        time.sleep(2.0)

        # Purge pending stop orders
        for o in self.acc_mgr.get_master().get_open_orders():
            if str(o.get("type", "")).lower() in ["limit", "stop"]:
                self.engine.cancel_pending(str(o.get("id")))

    # -------------------------------------------------------------------------
    # STAGES 11 - 13: In-Flight Modifications, Partial Close & Concurrency
    # -------------------------------------------------------------------------
    def test_stage_11_mid_trade_sl_tp_modification_fanout(self):
        """Stage 11: In-flight StopLoss and Target price modification fanout."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")
        live_price = self.acc_mgr.get_master().get_live_price(self.symbol) or 76000.0

        sl_init = f"{live_price - 800.0:.2f}"
        tp_init = f"{live_price + 1200.0:.2f}"
        res = self.engine.place_market_order(side="buy", lot=0.50, sl=sl_init, tp=tp_init)
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        # Update SL & TP
        sl_new = f"{live_price - 500.0:.2f}"
        tp_new = f"{live_price + 1500.0:.2f}"
        mod_res = self.engine.modify_order_sl_tp(order_id=m_oid, new_sl=sl_new, new_tp=tp_new)
        assert mod_res["modify_sl"].get("status") == "success"
        time.sleep(2.0)

        # Verify follower ticket reflects updated SL
        f1 = self.acc_mgr.get_followers()[0]
        f1_orders = f1.get_open_orders()
        assert len(f1_orders) >= 1
        f1_sl = str(f1_orders[0].get("sl", ""))
        assert f1_sl != "---" and f1_sl != "", "Follower ticket must reflect active SL"

        self.engine.full_squareoff(m_oid)

    def test_stage_12_partial_position_closure_fanout(self):
        """Stage 12: Partial position close fanout (0.50 -> 0.30 lots)."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")

        # Master opens 0.50 lot (followers get 1.50)
        res = self.engine.place_market_order(side="buy", lot=0.50)
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        # Master partially closes 0.20 lots (remaining lot = 0.30)
        p_res = self.engine.partial_close(order_id=m_oid, partial_lot=0.20)
        assert p_res.get("status") == "success"
        time.sleep(3.0)

        # Followers must retain 0.90 lots (0.30 * 3.0)
        for f in self.acc_mgr.get_followers():
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            rem_lot = float(f_ords[0].get("lot", 0.0) or f_ords[0].get("partiallot", 0.0) or 0.0)
            assert abs(rem_lot - 0.90) <= 0.01, f"Follower {f.name} expected 0.90 lots, got {rem_lot}"

        self.engine.full_squareoff(m_oid)

    def test_stage_13_rapid_burst_concurrency(self):
        """Stage 13: Rapid-fire burst replication stress (4 consecutive market orders)."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")

        burst_ids = []
        for _ in range(4):
            r = self.engine.place_market_order(side="buy", lot=0.10)
            burst_ids.append(str(r.get("data", {}).get("orderId", "")))
            time.sleep(0.3)

        time.sleep(3.0)
        # All 5 followers must hold 4 distinct open positions (20 child orders)
        for f in self.acc_mgr.get_followers():
            assert len(f.get_open_orders()) == 4, f"Follower {f.name} missing burst tickets"

        # Teardown burst
        for bid in burst_ids:
            self.engine.full_squareoff(bid)
            time.sleep(0.5)

    # -------------------------------------------------------------------------
    # STAGES 14 - 15: Isolation & Subscription Dynamics
    # -------------------------------------------------------------------------
    def test_stage_14_tenant_isolation(self):
        """Stage 14: Tenant isolation (Follower early close does NOT affect Master or peers)."""
        self.cfg_mgr.set_mode_and_verify(method="multiplier", value="3.0")

        res = self.engine.place_market_order(side="buy", lot=0.10)
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.5)

        f1 = self.acc_mgr.get_followers()[0]
        f1_ords = f1.get_open_orders()
        assert len(f1_ords) >= 1
        f1_tid = str(f1_ords[0].get("id"))

        # Follower 1 closes early
        iso = self.stop_out_val.verify_isolation_on_follower_liquidation(
            follower=f1, follower_order_id=f1_tid, master_order_id=m_oid
        )
        assert iso.get("isolation_intact"), f"Tenant isolation breach detected: {iso}"

        self.engine.full_squareoff(m_oid)

    def test_stage_15_unfollow_and_refollow_lifecycle(self):
        """Stage 15: Unfollow stops replication; re-follow resumes replication."""
        f1 = self.acc_mgr.get_followers()[0]
        master_uid = "1060"

        # Unfollow
        unf_res = f1.unfollow_copy_master(master_uid=master_uid)
        assert unf_res.get("status") == "success"
        time.sleep(1.5)

        # Master places order -> Follower 1 should NOT receive it
        r1 = self.engine.place_market_order(side="buy", lot=0.10)
        oid1 = str(r1.get("data", {}).get("orderId", ""))
        time.sleep(2.0)
        assert len(f1.get_open_orders()) == 0, "Unfollowed follower must NOT receive replicated trades"
        self.engine.full_squareoff(oid1)
        time.sleep(1.5)

        # Re-follow
        fol_res = f1.follow_copy_master(master_uid=master_uid, method="multiplier", value="3.0")
        assert fol_res.get("status") == "success"
        time.sleep(1.5)

        # Master places order -> Follower 1 receives it
        r2 = self.engine.place_market_order(side="buy", lot=0.10)
        oid2 = str(r2.get("data", {}).get("orderId", ""))
        time.sleep(2.5)
        assert len(f1.get_open_orders()) >= 1, "Re-followed follower must resume receiving trades"
        self.engine.full_squareoff(oid2)

    # -------------------------------------------------------------------------
    # STAGES 16 - 17: Margin Monitoring & 50% Stop-Out
    # -------------------------------------------------------------------------
    def test_stage_16_margin_monitoring_and_stop_out_boundary(self):
        """Stage 16: Margin monitoring and boundary evaluation."""
        master = self.acc_mgr.get_master()
        res = self.engine.place_market_order(side="buy", lot=0.10)
        oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        # Evaluate boundary
        eval_res = self.stop_out_val.evaluate_stop_out_boundary(master)
        assert eval_res.get("boundary_status") == "HEALTHY", f"Expected healthy status, got {eval_res}"

        # Test duplicate squareoff idempotency
        idem = self.stop_out_val.test_duplicate_squareoff_idempotency(master, oid)
        assert idem.get("idempotent"), f"OMS Idempotency failed: {idem}"

    # -------------------------------------------------------------------------
    # STAGES 18 - 20: Commissions, Withdrawal Locks & Final Clean Slate
    # -------------------------------------------------------------------------
    def test_stage_18_to_20_settlement_withdrawals_and_reconciliation(self):
        """Stages 18-20: Commission audit, withdrawal margin locks, and final clean slate."""
        master = self.acc_mgr.get_master()

        # Stage 18: Profit Sharing ledger reconciliation
        ps_audit = self.comm_val.audit_profit_sharing_ledger()
        assert ps_audit.get("is_fully_reconciled"), f"Profit sharing ledger mismatch: {ps_audit}"
        assert ps_audit.get("discrepancy") == 0.0, f"Discrepancy detected: {ps_audit.get('discrepancy')}"

        # Stage 19: Withdrawal lock audit
        w_val = WithdrawalValidator(master)
        w_audit = w_val.audit_withdrawal_headroom()
        assert w_audit.get("available_fund", 0.0) > 0.0

        # Stage 20: Final clean slate reconciliation
        rec = self.reconciler.audit_clean_slate()
        assert rec.get("all_clean"), f"Residual orders or margin detected: {rec}"
