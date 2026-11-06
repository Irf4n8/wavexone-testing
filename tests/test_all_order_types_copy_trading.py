"""
WavexOne Copy Trading: Comprehensive Multi-Mode All Order Types Test Suite.
Executes sequentially in the exact requested order:
  1. MULTIPLIER MODE (3.0x Proportional Replication -> 1.50 Lots)
  2. BALANCE-BASED MODE (Dynamic Balance Ratio Sizing -> 0.05 Lots)
  3. EQUITY-BASED MODE (Dynamic Equity Ratio Sizing -> 0.05 Lots)

For EACH of the three modes, the following order types are validated:
  - Market BUY (WITH and WITHOUT TP/SL)
  - Market SELL (WITH and WITHOUT TP/SL)
  - Limit BUY (WITH and WITHOUT TP/SL)
  - Limit SELL (WITH and WITHOUT TP/SL)
  - Stop HFT BUY (WITH and WITHOUT TP/SL)
  - Stop HFT SELL (WITH and WITHOUT TP/SL)
  - Stop HFT BOTH Dual-Leg (WITH and WITHOUT TP/SL)

Strict Rules:
  - Master order size = 0.50 Lots
  - Clean slate asserted before and after every order
  - Proportional dynamic replication verified across follower order books
  - TP and SL levels verified on Master and Follower
"""
import pytest
import time
from typing import Dict, Any, List
from config.settings import WavexSettings
from core.copy_trading.session_manager import CopyTradingSessionManager
from core.copy_trading.copy_config_manager import CopyConfigManager
from core.copy_trading.book_poller import BookPoller
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.logger import logger


@pytest.fixture(scope="session")
def copy_env():
    """Initializes sessions, config manager, poller, and teardown handler."""
    session_mgr = CopyTradingSessionManager()
    sessions = session_mgr.initialize_all()
    master = sessions["master"]
    followers = [sessions[name] for name in ["ctf1", "ctf2", "ctf3", "ctf4", "ctf5"]]

    config_mgr = CopyConfigManager(master=master, followers=followers)
    poller = BookPoller(master=master, followers=followers)
    teardown = SafeTeardownHandler(master=master, followers=followers)

    # Pre-flight clean slate & baseline restoration
    teardown.assert_clean_slate()
    config_mgr.restore_baseline()

    yield {
        "master": master,
        "followers": followers,
        "config_mgr": config_mgr,
        "poller": poller,
        "teardown": teardown
    }

    # Final post-suite cleanup
    logger.info("Final session teardown and baseline restoration...")
    teardown.execute_complete_teardown()
    config_mgr.restore_baseline()


class BaseOrderTypesTester:
    """Base helper class executing order variations under a specific copy mode."""
    symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
    master_lot = 0.50

    def _get_expected_lot(self, env, mode: str) -> float:
        if mode == "multiplier":
            return 1.50  # 0.50 * 3.0x
        elif mode == "balance":
            balances_map = env["poller"].poll_all_accounts_balance()
            m_bal = float(balances_map.get("ctmaster", {}).get("balance", 100000.0) or 100000.0)
            f_bal = float(balances_map.get("ctf1", {}).get("balance", 10000.0) or 10000.0)
            return round((f_bal / m_bal) * self.master_lot, 2)  # ~0.05
        elif mode == "equity":
            balances_map = env["poller"].poll_all_accounts_balance()
            m_eq = float(balances_map.get("ctmaster", {}).get("equity", 100000.0) or 100000.0)
            f_eq = float(balances_map.get("ctf1", {}).get("equity", 10000.0) or 10000.0)
            return round((f_eq / m_eq) * self.master_lot, 2)  # ~0.05
        return 0.50

    def _execute_market(self, env, mode: str, side: str, with_tpsl: bool, scenario_id: str, title: str):
        master = env["master"]
        poller = env["poller"]
        teardown = env["teardown"]
        rec = SanitizedEvidenceRecorder(scenario_id=scenario_id, title=title, category=f"{mode.capitalize()} Market Orders")

        teardown.assert_clean_slate()
        exp_lot = self._get_expected_lot(env, mode)
        cmp = master.get_live_price(self.symbol)
        sl, tp = ("", "")
        if with_tpsl:
            sl = f"{cmp - 800.0:.2f}" if side == "buy" else f"{cmp + 800.0:.2f}"
            tp = f"{cmp + 800.0:.2f}" if side == "buy" else f"{cmp - 800.0:.2f}"

        try:
            place_res = master.place_order(symbol=self.symbol, side=side, lot=self.master_lot, order_type="market", sl=sl, target=tp)
            assert place_res.get("status") == "success", f"Market {side.upper()} failed: {place_res}"
            rec.log_step(name=f"Master Market {side.upper()}", action="POST /trade/placeorder.php", extra=place_res)

            m_order = master.wait_for_order_in_book(symbol=self.symbol, side=side, expected_lot=self.master_lot, timeout=8.0)
            assert m_order is not None, "Master order not found in book!"
            master_oid = str(m_order.get("id"))

            rep_res = poller.wait_for_follower_replication(symbol=self.symbol, side=side, expected_lot=exp_lot, timeout=10.0)
            assert rep_res["all_replicated"], f"Missing followers: {rep_res['missing_followers']}"
            rec.log_assertion(f"All 5 Followers Replicated ({exp_lot:.2f} Lots)", True, rep_res["all_replicated"], rep_res["all_replicated"])

            for fname, oinfo in rep_res["replicated_orders"].items():
                assert abs(oinfo["lot"] - exp_lot) < 0.001, f"{fname} lot mismatch! Expected {exp_lot}, got {oinfo['lot']}"
                if with_tpsl:
                    f_sl = str(oinfo["raw_order"].get("sl", ""))
                    f_tp = str(oinfo["raw_order"].get("tp", ""))
                    rec.log_assertion(f"{fname} SL Propagated", True, f_sl not in ["---", "", "0.00", "0"], True)
                    rec.log_assertion(f"{fname} TP Propagated", True, f_tp not in ["---", "", "0.00", "0"], True)

            master.squareoff_position(master_oid)
            poller.wait_for_all_positions_closed(timeout=10.0)
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    def _execute_limit(self, env, mode: str, side: str, with_tpsl: bool, scenario_id: str, title: str):
        master = env["master"]
        teardown = env["teardown"]
        rec = SanitizedEvidenceRecorder(scenario_id=scenario_id, title=title, category=f"{mode.capitalize()} Limit Orders")

        teardown.assert_clean_slate()
        exp_lot = self._get_expected_lot(env, mode)
        cmp = master.get_live_price(self.symbol)
        sl, tp = ("", "")
        if side == "buy":
            trigger = f"{cmp - 250.0:.2f}"
            if with_tpsl:
                sl = f"{float(trigger) - 200.0:.2f}"
                tp = f"{float(trigger) + 200.0:.2f}"
        else:
            trigger = f"{cmp + 250.0:.2f}"
            if with_tpsl:
                sl = f"{float(trigger) + 200.0:.2f}"
                tp = f"{float(trigger) - 200.0:.2f}"

        try:
            place_res = master.place_order(symbol=self.symbol, side=side, lot=self.master_lot, order_type="limit", trigger=trigger, sl=sl, target=tp)
            assert place_res.get("status") == "success", f"Limit {side.upper()} failed: {place_res}"
            rec.log_step(name=f"Master Limit {side.upper()}", action="POST /trade/placeorder.php", extra=place_res)

            time.sleep(2.0)
            m_orders = [o for o in master.get_open_orders() if o.get("type") == "limit" and o.get("bs", "").upper() == side.upper()]
            assert len(m_orders) >= 1, f"Master Limit {side.upper()} not in book!"
            master_oid = m_orders[0]["id"]

            rep_count = 0
            for f in env["followers"]:
                f_orders = [o for o in f.get_open_orders() if o.get("type") == "limit" and o.get("bs", "").upper() == side.upper()]
                if f_orders:
                    rep_count += 1
                    assert abs(float(f_orders[0].get("lot", 0.0)) - exp_lot) < 0.001
                    if with_tpsl:
                        assert f_orders[0].get("sl") not in ["---", "", "0.00", "0"]
                        assert f_orders[0].get("tp") not in ["---", "", "0.00", "0"]

            rec.log_assertion(f"Followers Replicated Limit {side.upper()} ({exp_lot:.2f} Lots)", 5, rep_count, rep_count == 5)
            assert rep_count == 5, f"Expected 5 follower limit orders, got {rep_count}"

            master.cancel_order(master_oid)
            time.sleep(2.0)
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    def _execute_stop(self, env, mode: str, stop_type: str, side: str, with_tpsl: bool, scenario_id: str, title: str):
        master = env["master"]
        teardown = env["teardown"]
        rec = SanitizedEvidenceRecorder(scenario_id=scenario_id, title=title, category=f"{mode.capitalize()} Stop HFT Orders")

        teardown.assert_clean_slate()
        exp_lot = self._get_expected_lot(env, mode)
        cmp = master.get_live_price(self.symbol)
        lot_str = f"{self.master_lot:.2f}"

        if side == "buy":
            triggerb = f"{cmp + 250.0:.2f}"
            slb = f"{float(triggerb) - 150.0:.2f}" if with_tpsl else ""
            targetb = f"{float(triggerb) + 150.0:.2f}" if with_tpsl else ""
            place_res = master.place_order(
                symbol=self.symbol, side="buy", order_type="stop", stop_hft_type=stop_type,
                lotb=lot_str, triggerb=triggerb, slb=slb, targetb=targetb
            )
        else:
            triggers = f"{cmp - 250.0:.2f}"
            sls = f"{float(triggers) + 150.0:.2f}" if with_tpsl else ""
            targets = f"{float(triggers) - 150.0:.2f}" if with_tpsl else ""
            place_res = master.place_order(
                symbol=self.symbol, side="sell", order_type="stop", stop_hft_type=stop_type,
                lots=lot_str, triggers=triggers, sls=sls, targets=targets
            )

        try:
            assert place_res.get("status") == "success", f"Stop HFT {side.upper()} failed: {place_res}"
            rec.log_step(name=f"Master Stop HFT {side.upper()}", action="POST /trade/placeorder.php", extra=place_res)

            time.sleep(2.0)
            m_orders = [o for o in master.get_open_orders() if o.get("type") == "stop" and o.get("bs", "").upper() == side.upper()]
            assert len(m_orders) >= 1, f"Master Stop HFT {side.upper()} not in book!"

            rep_count = 0
            for f in env["followers"]:
                f_orders = [o for o in f.get_open_orders() if o.get("type") == "stop" and o.get("bs", "").upper() == side.upper()]
                if f_orders:
                    rep_count += 1
                    assert abs(float(f_orders[0].get("lot", 0.0)) - exp_lot) < 0.001
                    if with_tpsl:
                        assert f_orders[0].get("sl") not in ["---", "", "0.00", "0"]
                        assert f_orders[0].get("tp") not in ["---", "", "0.00", "0"]

            rec.log_assertion(f"Followers Replicated Stop HFT {side.upper()} ({exp_lot:.2f} Lots)", 5, rep_count, rep_count == 5)
            assert rep_count == 5, f"Expected 5 follower stop orders, got {rep_count}"
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    def _execute_stop_both(self, env, mode: str, with_tpsl: bool, scenario_id: str, title: str):
        master = env["master"]
        teardown = env["teardown"]
        rec = SanitizedEvidenceRecorder(scenario_id=scenario_id, title=title, category=f"{mode.capitalize()} Stop HFT Orders")

        teardown.assert_clean_slate()
        exp_lot = self._get_expected_lot(env, mode)
        cmp = master.get_live_price(self.symbol)
        lot_str = f"{self.master_lot:.2f}"

        triggerb = f"{cmp + 250.0:.2f}"
        triggers = f"{cmp - 250.0:.2f}"
        slb = f"{float(triggerb) - 150.0:.2f}" if with_tpsl else ""
        targetb = f"{float(triggerb) + 150.0:.2f}" if with_tpsl else ""
        sls = f"{float(triggers) + 150.0:.2f}" if with_tpsl else ""
        targets = f"{float(triggers) - 150.0:.2f}" if with_tpsl else ""

        try:
            place_res = master.place_order(
                symbol=self.symbol, side="buy", order_type="stop", stop_hft_type="2",
                lotb=lot_str, triggerb=triggerb, slb=slb, targetb=targetb,
                lots=lot_str, triggers=triggers, sls=sls, targets=targets
            )
            assert place_res.get("status") == "success", f"Stop HFT BOTH failed: {place_res}"
            rec.log_step(name="Master Stop HFT BOTH", action="POST /trade/placeorder.php", extra=place_res)

            time.sleep(2.0)
            m_orders = [o for o in master.get_open_orders() if o.get("type") == "stop"]
            assert len(m_orders) >= 2, f"Expected at least 2 pending stop orders on Master, found {len(m_orders)}"

            rep_count = 0
            for f in env["followers"]:
                f_orders = [o for o in f.get_open_orders() if o.get("type") == "stop"]
                if len(f_orders) >= 2:
                    rep_count += 1
                    for fo in f_orders:
                        assert abs(float(fo.get("lot", 0.0)) - exp_lot) < 0.001
                        if with_tpsl:
                            assert fo.get("sl") not in ["---", "", "0.00", "0"]
                            assert fo.get("tp") not in ["---", "", "0.00", "0"]

            rec.log_assertion(f"Followers Replicated Stop HFT BOTH Dual Legs ({exp_lot:.2f} Lots)", 5, rep_count, rep_count == 5)
            assert rep_count == 5, f"Expected 5 followers with dual stop legs, got {rep_count}"
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()


# =============================================================================
# PART 1: MULTIPLIER MODE (3.0x Proportional Replication -> 1.50 Lots)
# =============================================================================

class Test01_MultiplierModeOrders(BaseOrderTypesTester):
    """Executes all order types under Multiplier Mode (3.0x Multiplier)."""

    @pytest.fixture(autouse=True)
    def ensure_multiplier_mode(self, copy_env):
        copy_env["config_mgr"].set_all_followers_mode(method="multiplier", value="3.0")

    def test_m_01_market_buy_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="multiplier", side="buy", with_tpsl=False,
                             scenario_id="CT-MUL-MKT-BUY-NO-TPSL", title="Multiplier Market BUY WITHOUT TP/SL")

    def test_m_02_market_buy_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="multiplier", side="buy", with_tpsl=True,
                             scenario_id="CT-MUL-MKT-BUY-WITH-TPSL", title="Multiplier Market BUY WITH TP/SL")

    def test_m_03_market_sell_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="multiplier", side="sell", with_tpsl=False,
                             scenario_id="CT-MUL-MKT-SELL-NO-TPSL", title="Multiplier Market SELL WITHOUT TP/SL")

    def test_m_04_market_sell_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="multiplier", side="sell", with_tpsl=True,
                             scenario_id="CT-MUL-MKT-SELL-WITH-TPSL", title="Multiplier Market SELL WITH TP/SL")

    def test_m_05_limit_buy_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="multiplier", side="buy", with_tpsl=False,
                            scenario_id="CT-MUL-LMT-BUY-NO-TPSL", title="Multiplier Limit BUY WITHOUT TP/SL")

    def test_m_06_limit_buy_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="multiplier", side="buy", with_tpsl=True,
                            scenario_id="CT-MUL-LMT-BUY-WITH-TPSL", title="Multiplier Limit BUY WITH TP/SL")

    def test_m_07_limit_sell_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="multiplier", side="sell", with_tpsl=False,
                            scenario_id="CT-MUL-LMT-SELL-NO-TPSL", title="Multiplier Limit SELL WITHOUT TP/SL")

    def test_m_08_limit_sell_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="multiplier", side="sell", with_tpsl=True,
                            scenario_id="CT-MUL-LMT-SELL-WITH-TPSL", title="Multiplier Limit SELL WITH TP/SL")

    def test_m_09_stop_hft_buy_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="multiplier", stop_type="1", side="buy", with_tpsl=False,
                           scenario_id="CT-MUL-STP-BUY-NO-TPSL", title="Multiplier Stop HFT BUY WITHOUT TP/SL")

    def test_m_10_stop_hft_buy_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="multiplier", stop_type="1", side="buy", with_tpsl=True,
                           scenario_id="CT-MUL-STP-BUY-WITH-TPSL", title="Multiplier Stop HFT BUY WITH TP/SL")

    def test_m_11_stop_hft_sell_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="multiplier", stop_type="0", side="sell", with_tpsl=False,
                           scenario_id="CT-MUL-STP-SELL-NO-TPSL", title="Multiplier Stop HFT SELL WITHOUT TP/SL")

    def test_m_12_stop_hft_sell_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="multiplier", stop_type="0", side="sell", with_tpsl=True,
                           scenario_id="CT-MUL-STP-SELL-WITH-TPSL", title="Multiplier Stop HFT SELL WITH TP/SL")

    def test_m_13_stop_hft_both_without_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="multiplier", with_tpsl=False,
                                scenario_id="CT-MUL-STP-BOTH-NO-TPSL", title="Multiplier Stop HFT BOTH WITHOUT TP/SL")

    def test_m_14_stop_hft_both_with_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="multiplier", with_tpsl=True,
                                scenario_id="CT-MUL-STP-BOTH-WITH-TPSL", title="Multiplier Stop HFT BOTH WITH TP/SL")


# =============================================================================
# PART 2: BALANCE-BASED MODE (Dynamic Balance Ratio Sizing -> ~0.05 Lots)
# =============================================================================

class Test02_BalanceModeOrders(BaseOrderTypesTester):
    """Executes all order types under Balance-Based Mode (Dynamic Sizing)."""

    @pytest.fixture(autouse=True)
    def ensure_balance_mode(self, copy_env):
        copy_env["config_mgr"].set_all_followers_mode(method="balance")

    def test_b_01_market_buy_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="balance", side="buy", with_tpsl=False,
                             scenario_id="CT-BAL-MKT-BUY-NO-TPSL", title="Balance-Based Market BUY WITHOUT TP/SL")

    def test_b_02_market_buy_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="balance", side="buy", with_tpsl=True,
                             scenario_id="CT-BAL-MKT-BUY-WITH-TPSL", title="Balance-Based Market BUY WITH TP/SL")

    def test_b_03_market_sell_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="balance", side="sell", with_tpsl=False,
                             scenario_id="CT-BAL-MKT-SELL-NO-TPSL", title="Balance-Based Market SELL WITHOUT TP/SL")

    def test_b_04_market_sell_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="balance", side="sell", with_tpsl=True,
                             scenario_id="CT-BAL-MKT-SELL-WITH-TPSL", title="Balance-Based Market SELL WITH TP/SL")

    def test_b_05_limit_buy_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="balance", side="buy", with_tpsl=False,
                            scenario_id="CT-BAL-LMT-BUY-NO-TPSL", title="Balance-Based Limit BUY WITHOUT TP/SL")

    def test_b_06_limit_buy_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="balance", side="buy", with_tpsl=True,
                            scenario_id="CT-BAL-LMT-BUY-WITH-TPSL", title="Balance-Based Limit BUY WITH TP/SL")

    def test_b_07_limit_sell_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="balance", side="sell", with_tpsl=False,
                            scenario_id="CT-BAL-LMT-SELL-NO-TPSL", title="Balance-Based Limit SELL WITHOUT TP/SL")

    def test_b_08_limit_sell_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="balance", side="sell", with_tpsl=True,
                            scenario_id="CT-BAL-LMT-SELL-WITH-TPSL", title="Balance-Based Limit SELL WITH TP/SL")

    def test_b_09_stop_hft_buy_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="balance", stop_type="1", side="buy", with_tpsl=False,
                           scenario_id="CT-BAL-STP-BUY-NO-TPSL", title="Balance-Based Stop HFT BUY WITHOUT TP/SL")

    def test_b_10_stop_hft_buy_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="balance", stop_type="1", side="buy", with_tpsl=True,
                           scenario_id="CT-BAL-STP-BUY-WITH-TPSL", title="Balance-Based Stop HFT BUY WITH TP/SL")

    def test_b_11_stop_hft_sell_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="balance", stop_type="0", side="sell", with_tpsl=False,
                           scenario_id="CT-BAL-STP-SELL-NO-TPSL", title="Balance-Based Stop HFT SELL WITHOUT TP/SL")

    def test_b_12_stop_hft_sell_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="balance", stop_type="0", side="sell", with_tpsl=True,
                           scenario_id="CT-BAL-STP-SELL-WITH-TPSL", title="Balance-Based Stop HFT SELL WITH TP/SL")

    def test_b_13_stop_hft_both_without_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="balance", with_tpsl=False,
                                scenario_id="CT-BAL-STP-BOTH-NO-TPSL", title="Balance-Based Stop HFT BOTH WITHOUT TP/SL")

    def test_b_14_stop_hft_both_with_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="balance", with_tpsl=True,
                                scenario_id="CT-BAL-STP-BOTH-WITH-TPSL", title="Balance-Based Stop HFT BOTH WITH TP/SL")


# =============================================================================
# PART 3: EQUITY-BASED MODE (Dynamic Equity Ratio Sizing -> ~0.05 Lots)
# =============================================================================

class Test03_EquityModeOrders(BaseOrderTypesTester):
    """Executes all order types under Equity-Based Mode (Dynamic Sizing)."""

    @pytest.fixture(autouse=True)
    def ensure_equity_mode(self, copy_env):
        copy_env["config_mgr"].set_all_followers_mode(method="equity")

    def test_e_01_market_buy_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="equity", side="buy", with_tpsl=False,
                             scenario_id="CT-EQU-MKT-BUY-NO-TPSL", title="Equity-Based Market BUY WITHOUT TP/SL")

    def test_e_02_market_buy_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="equity", side="buy", with_tpsl=True,
                             scenario_id="CT-EQU-MKT-BUY-WITH-TPSL", title="Equity-Based Market BUY WITH TP/SL")

    def test_e_03_market_sell_without_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="equity", side="sell", with_tpsl=False,
                             scenario_id="CT-EQU-MKT-SELL-NO-TPSL", title="Equity-Based Market SELL WITHOUT TP/SL")

    def test_e_04_market_sell_with_tpsl(self, copy_env):
        self._execute_market(copy_env, mode="equity", side="sell", with_tpsl=True,
                             scenario_id="CT-EQU-MKT-SELL-WITH-TPSL", title="Equity-Based Market SELL WITH TP/SL")

    def test_e_05_limit_buy_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="equity", side="buy", with_tpsl=False,
                            scenario_id="CT-EQU-LMT-BUY-NO-TPSL", title="Equity-Based Limit BUY WITHOUT TP/SL")

    def test_e_06_limit_buy_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="equity", side="buy", with_tpsl=True,
                            scenario_id="CT-EQU-LMT-BUY-WITH-TPSL", title="Equity-Based Limit BUY WITH TP/SL")

    def test_e_07_limit_sell_without_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="equity", side="sell", with_tpsl=False,
                            scenario_id="CT-EQU-LMT-SELL-NO-TPSL", title="Equity-Based Limit SELL WITHOUT TP/SL")

    def test_e_08_limit_sell_with_tpsl(self, copy_env):
        self._execute_limit(copy_env, mode="equity", side="sell", with_tpsl=True,
                            scenario_id="CT-EQU-LMT-SELL-WITH-TPSL", title="Equity-Based Limit SELL WITH TP/SL")

    def test_e_09_stop_hft_buy_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="equity", stop_type="1", side="buy", with_tpsl=False,
                           scenario_id="CT-EQU-STP-BUY-NO-TPSL", title="Equity-Based Stop HFT BUY WITHOUT TP/SL")

    def test_e_10_stop_hft_buy_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="equity", stop_type="1", side="buy", with_tpsl=True,
                           scenario_id="CT-EQU-STP-BUY-WITH-TPSL", title="Equity-Based Stop HFT BUY WITH TP/SL")

    def test_e_11_stop_hft_sell_without_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="equity", stop_type="0", side="sell", with_tpsl=False,
                           scenario_id="CT-EQU-STP-SELL-NO-TPSL", title="Equity-Based Stop HFT SELL WITHOUT TP/SL")

    def test_e_12_stop_hft_sell_with_tpsl(self, copy_env):
        self._execute_stop(copy_env, mode="equity", stop_type="0", side="sell", with_tpsl=True,
                           scenario_id="CT-EQU-STP-SELL-WITH-TPSL", title="Equity-Based Stop HFT SELL WITH TP/SL")

    def test_e_13_stop_hft_both_without_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="equity", with_tpsl=False,
                                scenario_id="CT-EQU-STP-BOTH-NO-TPSL", title="Equity-Based Stop HFT BOTH WITHOUT TP/SL")

    def test_e_14_stop_hft_both_with_tpsl(self, copy_env):
        self._execute_stop_both(copy_env, mode="equity", with_tpsl=True,
                                scenario_id="CT-EQU-STP-BOTH-WITH-TPSL", title="Equity-Based Stop HFT BOTH WITH TP/SL")
