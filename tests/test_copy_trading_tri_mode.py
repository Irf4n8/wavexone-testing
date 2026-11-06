"""
WavexOne Copy Trading Tri-Mode Symmetry Verification Suite.
Validates the complete in-flight lifecycle across all 3 Copy Allocation Modes:
  1. Multiplier Mode (3.0x)
  2. Equity-Based Mode
  3. Balance-Based Mode

For each mode, 5 core features are validated:
  - Feature 1: Market Order Placement & Proportional Replication
  - Feature 2: Mid-Trade SL/TP In-Flight Modification Fanout
  - Feature 3: Proportional Partial Position Closure
  - Feature 4: Rapid-Fire Burst Scalping Concurrency
  - Feature 5: Live Market TP/SL Hit & Automated Follower Square-Off
"""

import time
import pytest
from typing import Dict, Any, List

from core.copy_trading.unified_components import (
    AccountManager,
    CopyConfigurationManager,
    OrderExecutionEngine,
    ReplicationValidator,
    SafeTeardown
)
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.logger import logger


@pytest.fixture(scope="class")
def tri_env():
    """Initializes and authenticates all 6 staging accounts for Tri-Mode testing."""
    acc_mgr = AccountManager()
    acc_mgr.initialize_and_authenticate()
    master = acc_mgr.get_master()
    followers = acc_mgr.get_followers()

    cfg_mgr = CopyConfigurationManager(master, followers)
    engine = OrderExecutionEngine(master, default_symbol="X:BTCUSD")
    validator = ReplicationValidator(master, followers)
    teardown = SafeTeardown(master, followers)

    teardown.execute_complete_teardown()
    cfg_mgr.restore_baseline()

    yield {
        "acc_mgr": acc_mgr,
        "master": master,
        "followers": followers,
        "cfg_mgr": cfg_mgr,
        "engine": engine,
        "validator": validator,
        "teardown": teardown,
        "symbol": "X:BTCUSD"
    }

    teardown.execute_complete_teardown()
    cfg_mgr.restore_baseline()


# =============================================================================
# 1. MULTIPLIER MODE SUITE (3.0x)
# =============================================================================
class TestCopyTradingMultiplierMode:
    """Mode 1: Multiplier Mode (3.0x scaling)."""

    def test_mul_01_market_order_replication(self, tri_env):
        """MUL-01: Market order replication (0.50 -> 1.50 lots)."""
        tri_env["teardown"].execute_complete_teardown()
        tri_env["cfg_mgr"].set_all_followers_mode(method="multiplier", value="3.0")
        time.sleep(2.5)

        res = tri_env["engine"].place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        v = tri_env["validator"].validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="multiplier", multiplier_val=3.0
        )
        assert v.get("all_replicated"), f"Multiplier replication failed: {v}"
        tri_env["engine"].full_squareoff(m_oid)

    def test_mul_02_mid_trade_sltp_modification(self, tri_env):
        """MUL-02: Mid-trade SL/TP modification on Multiplier mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        cmp = master.get_live_price(tri_env["symbol"])
        sl_init = f"{cmp - 800.0:.2f}"
        tp_init = f"{cmp + 1200.0:.2f}"

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50, sl=sl_init, target=tp_init)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        # Modify SL and TP
        sl_new = f"{cmp - 400.0:.2f}"
        tp_new = f"{cmp + 1600.0:.2f}"
        master.modify_order(order_id=m_oid, name="StopLoss", val=sl_new)
        master.modify_order(order_id=m_oid, name="Target", val=tp_new)
        time.sleep(2.0)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            act_sl = float(f_ords[0].get("sl", 0.0) or 0.0)
            act_tp = float(f_ords[0].get("tp", 0.0) or 0.0)
            assert abs(act_sl - float(sl_new)) < 0.05, f"{f.name} SL mismatch: expected {sl_new}, got {act_sl}"
            assert abs(act_tp - float(tp_new)) < 0.05, f"{f.name} TP mismatch: expected {tp_new}, got {act_tp}"

        master.squareoff_position(m_oid)

    def test_mul_03_partial_position_closure(self, tri_env):
        """MUL-03: Partial close in Multiplier mode (0.50 -> 0.30 => Follower 1.50 -> 0.90)."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        # Master partially closes 0.20 lots
        master.partial_close_position(order_id=m_oid, partial_lot=0.20)
        time.sleep(2.5)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            tot_lot = sum(float(o.get("lot", 0.0) or o.get("partiallot", 0.0) or 0.0) for o in f_ords)
            assert abs(tot_lot - 0.90) < 0.01, f"{f.name} remaining lot {tot_lot} != 0.90"

        master.squareoff_position(m_oid)

    def test_mul_04_rapid_burst_concurrency(self, tri_env):
        """MUL-04: Rapid burst scalping on Multiplier mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        # Place 4 consecutive orders
        for _ in range(4):
            master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10)
            time.sleep(0.3)
        time.sleep(3.0)

        for f in followers:
            assert len(f.get_open_orders()) == 4

        tri_env["teardown"].execute_complete_teardown()

    def test_mul_05_live_tp_sl_hit_auto_squareoff(self, tri_env):
        """MUL-05: Real-market TP/SL hit on Multiplier mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()
        time.sleep(1.0)

        cmp = master.get_live_price(tri_env["symbol"])
        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        if res.get("status") != "success":
            time.sleep(1.0)
            cmp = master.get_live_price(tri_env["symbol"])
            res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        assert res.get("status") == "success", f"Failed to place order in MUL-05: {res}"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        hit = False
        for _ in range(12):
            time.sleep(2.0)
            if len(master.get_open_orders()) == 0:
                hit = True
                break
        if not hit:
            now_cmp = master.get_live_price(tri_env["symbol"])
            master.modify_order(order_id=m_oid, name="StopLoss", val=str(now_cmp))
            for _ in range(8):
                time.sleep(2.0)
                if len(master.get_open_orders()) == 0:
                    hit = True
                    break

        assert hit, "Master SL/TP hit was not triggered"
        time.sleep(2.0)
        for f in followers:
            assert len(f.get_open_orders()) == 0, f"{f.name} still open after master SL/TP hit!"


# =============================================================================
# 2. EQUITY-BASED ALLOCATION SUITE
# =============================================================================
class TestCopyTradingEquityMode:
    """Mode 2: Equity-Based Allocation Mode."""

    def test_eq_01_market_order_replication(self, tri_env):
        """EQ-01: Market order replication based on equity ratio (0.50 -> 0.05 lots)."""
        tri_env["teardown"].execute_complete_teardown()
        tri_env["cfg_mgr"].set_all_followers_mode(method="equity")
        time.sleep(1.5)

        res = tri_env["engine"].place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        v = tri_env["validator"].validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="equity"
        )
        assert v.get("all_replicated"), f"Equity replication failed: {v}"
        tri_env["engine"].full_squareoff(m_oid)

    def test_eq_02_mid_trade_sltp_modification(self, tri_env):
        """EQ-02: Mid-trade SL/TP modification on Equity mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        cmp = master.get_live_price(tri_env["symbol"])
        sl_init = f"{cmp - 800.0:.2f}"
        tp_init = f"{cmp + 1200.0:.2f}"

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50, sl=sl_init, target=tp_init)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        sl_new = f"{cmp - 400.0:.2f}"
        tp_new = f"{cmp + 1600.0:.2f}"
        master.modify_order(order_id=m_oid, name="StopLoss", val=sl_new)
        master.modify_order(order_id=m_oid, name="Target", val=tp_new)
        time.sleep(2.0)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            act_sl = float(f_ords[0].get("sl", 0.0) or 0.0)
            act_tp = float(f_ords[0].get("tp", 0.0) or 0.0)
            assert abs(act_sl - float(sl_new)) < 0.05, f"{f.name} SL mismatch: expected {sl_new}, got {act_sl}"
            assert abs(act_tp - float(tp_new)) < 0.05, f"{f.name} TP mismatch: expected {tp_new}, got {act_tp}"

        master.squareoff_position(m_oid)

    def test_eq_03_partial_position_closure(self, tri_env):
        """EQ-03: Partial close in Equity mode (0.50 -> 0.30 => Follower 0.05 -> 0.03 lots)."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        # Master partially closes 0.20 lots (40% reduction)
        master.partial_close_position(order_id=m_oid, partial_lot=0.20)
        time.sleep(2.5)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            tot_lot = sum(float(o.get("lot", 0.0) or o.get("partiallot", 0.0) or 0.0) for o in f_ords)
            assert abs(tot_lot - 0.03) < 0.01, f"{f.name} Equity remaining lot {tot_lot} != 0.03"

        master.squareoff_position(m_oid)

    def test_eq_04_rapid_burst_concurrency(self, tri_env):
        """EQ-04: Rapid burst scalping in Equity mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        for _ in range(4):
            master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10)
            time.sleep(0.3)
        time.sleep(3.0)

        for f in followers:
            assert len(f.get_open_orders()) == 4

        tri_env["teardown"].execute_complete_teardown()

    def test_eq_05_live_tp_sl_hit_auto_squareoff(self, tri_env):
        """EQ-05: Real-market TP/SL hit on Equity mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()
        time.sleep(1.0)

        cmp = master.get_live_price(tri_env["symbol"])
        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        if res.get("status") != "success":
            time.sleep(1.0)
            cmp = master.get_live_price(tri_env["symbol"])
            res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        assert res.get("status") == "success", f"Failed to place order in MUL-05: {res}"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        hit = False
        for _ in range(12):
            time.sleep(2.0)
            if len(master.get_open_orders()) == 0:
                hit = True
                break
        if not hit:
            now_cmp = master.get_live_price(tri_env["symbol"])
            master.modify_order(order_id=m_oid, name="StopLoss", val=str(now_cmp))
            for _ in range(8):
                time.sleep(2.0)
                if len(master.get_open_orders()) == 0:
                    hit = True
                    break

        assert hit, "Master SL/TP hit was not triggered in Equity mode"
        time.sleep(2.0)
        for f in followers:
            assert len(f.get_open_orders()) == 0, f"{f.name} still open after master SL/TP hit in Equity mode!"


# =============================================================================
# 3. BALANCE-BASED ALLOCATION SUITE
# =============================================================================
class TestCopyTradingBalanceMode:
    """Mode 3: Balance-Based Allocation Mode."""

    def test_bal_01_market_order_replication(self, tri_env):
        """BAL-01: Market order replication based on balance ratio (0.50 -> 0.05 lots)."""
        tri_env["teardown"].execute_complete_teardown()
        tri_env["cfg_mgr"].set_all_followers_mode(method="balance")
        time.sleep(1.5)

        res = tri_env["engine"].place_market_order(side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        v = tri_env["validator"].validate_fanout_replication(
            master_order_id=m_oid, expected_side="BUY", master_lot=0.50, mode="balance"
        )
        assert v.get("all_replicated"), f"Balance replication failed: {v}"
        tri_env["engine"].full_squareoff(m_oid)

    def test_bal_02_mid_trade_sltp_modification(self, tri_env):
        """BAL-02: Mid-trade SL/TP modification on Balance mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        cmp = master.get_live_price(tri_env["symbol"])
        sl_init = f"{cmp - 800.0:.2f}"
        tp_init = f"{cmp + 1200.0:.2f}"

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50, sl=sl_init, target=tp_init)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        sl_new = f"{cmp - 400.0:.2f}"
        tp_new = f"{cmp + 1600.0:.2f}"
        master.modify_order(order_id=m_oid, name="StopLoss", val=sl_new)
        master.modify_order(order_id=m_oid, name="Target", val=tp_new)
        time.sleep(2.0)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            act_sl = float(f_ords[0].get("sl", 0.0) or 0.0)
            act_tp = float(f_ords[0].get("tp", 0.0) or 0.0)
            assert abs(act_sl - float(sl_new)) < 0.05, f"{f.name} SL mismatch: expected {sl_new}, got {act_sl}"
            assert abs(act_tp - float(tp_new)) < 0.05, f"{f.name} TP mismatch: expected {tp_new}, got {act_tp}"

        master.squareoff_position(m_oid)

    def test_bal_03_partial_position_closure(self, tri_env):
        """BAL-03: Partial close in Balance mode (0.50 -> 0.30 => Follower 0.05 -> 0.03 lots)."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.50)
        assert res.get("status") == "success"
        m_oid = str(res.get("data", {}).get("orderId", ""))
        time.sleep(2.0)

        # Master partially closes 0.20 lots (40% reduction)
        master.partial_close_position(order_id=m_oid, partial_lot=0.20)
        time.sleep(2.5)

        for f in followers:
            f_ords = f.get_open_orders()
            assert len(f_ords) >= 1
            tot_lot = sum(float(o.get("lot", 0.0) or o.get("partiallot", 0.0) or 0.0) for o in f_ords)
            assert abs(tot_lot - 0.03) < 0.01, f"{f.name} Balance remaining lot {tot_lot} != 0.03"

        master.squareoff_position(m_oid)

    def test_bal_04_rapid_burst_concurrency(self, tri_env):
        """BAL-04: Rapid burst scalping in Balance mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()

        for _ in range(4):
            master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10)
            time.sleep(0.3)
        time.sleep(3.0)

        for f in followers:
            assert len(f.get_open_orders()) == 4

        tri_env["teardown"].execute_complete_teardown()

    def test_bal_05_live_tp_sl_hit_auto_squareoff(self, tri_env):
        """BAL-05: Real-market TP/SL hit on Balance mode."""
        master = tri_env["master"]
        followers = tri_env["followers"]
        tri_env["teardown"].execute_complete_teardown()
        time.sleep(1.0)

        cmp = master.get_live_price(tri_env["symbol"])
        res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        if res.get("status") != "success":
            time.sleep(1.0)
            cmp = master.get_live_price(tri_env["symbol"])
            res = master.place_order(symbol=tri_env["symbol"], side="buy", lot=0.10, sl=f"{cmp - 2.0:.2f}", target=f"{cmp + 2.0:.2f}")
        assert res.get("status") == "success", f"Failed to place order in MUL-05: {res}"
        m_oid = str(res.get("data", {}).get("orderId", ""))

        hit = False
        for _ in range(12):
            time.sleep(2.0)
            if len(master.get_open_orders()) == 0:
                hit = True
                break
        if not hit:
            now_cmp = master.get_live_price(tri_env["symbol"])
            master.modify_order(order_id=m_oid, name="StopLoss", val=str(now_cmp))
            for _ in range(8):
                time.sleep(2.0)
                if len(master.get_open_orders()) == 0:
                    hit = True
                    break

        assert hit, "Master SL/TP hit was not triggered in Balance mode"
        time.sleep(2.0)
        for f in followers:
            assert len(f.get_open_orders()) == 0, f"{f.name} still open after master SL/TP hit in Balance mode!"

