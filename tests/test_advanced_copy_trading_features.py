"""
WavexOne Copy Trading: Advanced In-Flight Features Test Suite.
Validates:
1. Mid-Trade Order Modification Fanout (Modifying StopLoss & Target on live open trades).
2. Partial Position Close Proportional Fanout (Multiplier Mode: 0.50 -> 0.30 lot => Follower 1.50 -> 0.90 lot).
3. Partial Position Close in Balance Mode (0.50 -> 0.30 lot => Follower 0.05 -> 0.03 lot).
4. Rapid-Fire Burst Concurrency Stress Test (Master places 5 orders in rapid succession; fanout queue integrity).

Ensures deterministic teardown and clean slate verification across all 6 accounts.
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


@pytest.fixture(scope="class")
def adv_env():
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
    logger.info("Executing advanced suite teardown...")
    teardown.execute_complete_teardown()
    config_mgr.restore_baseline()


class TestAdvancedCopyTradingFeatures:
    """Advanced In-Flight and Stress Tests for WavexOne Copy Trading."""

    symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"

    # =========================================================================
    # 1. MID-TRADE ORDER MODIFICATION FANOUT
    # =========================================================================

    @pytest.mark.trading
    def test_01_mid_trade_modification_fanout(self, adv_env):
        """
        Verify that modifying StopLoss and Target on Master's open position
        dynamically updates all 5 follower tickets in real-time.
        """
        master = adv_env["master"]
        followers = adv_env["followers"]
        teardown = adv_env["teardown"]
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ADV-01-MOD",
            title="Mid-Trade Order Modification Fanout (Live SL/TP Update)",
            category="Trade Management"
        )

        teardown.assert_clean_slate()
        cmp = master.get_live_price(self.symbol)
        sl_init = f"{cmp - 1000.0:.2f}"
        tp_init = f"{cmp + 1000.0:.2f}"

        try:
            # 1. Place order on Master (0.50 lot)
            place_res = master.place_order(symbol=self.symbol, side="buy", lot=0.50, order_type="market", sl=sl_init, target=tp_init)
            assert place_res.get("status") == "success"
            time.sleep(2.0)

            m_orders = master.get_open_orders()
            assert len(m_orders) >= 1
            master_oid = str(m_orders[0]["id"])
            rec.log_step("Master Placed 0.50 BUY", "POST /trade/placeorder.php", extra={"order_id": master_oid, "sl": sl_init, "tp": tp_init})

            # Verify initial replication across followers
            for f in followers:
                f_orders = f.get_open_orders()
                assert len(f_orders) >= 1
                assert abs(float(f_orders[0].get("sl", 0.0)) - float(sl_init)) < 0.05
                assert abs(float(f_orders[0].get("tp", 0.0)) - float(tp_init)) < 0.05
            rec.log_assertion("Initial SL/TP Replicated on All Followers", True, True, True)

            # 2. Modify StopLoss on Master
            sl_new = f"{cmp - 400.0:.2f}"
            mod_sl_res = master.modify_order(order_id=master_oid, name="StopLoss", val=sl_new)
            assert mod_sl_res.get("status") == "success", f"Modify SL failed: {mod_sl_res}"
            rec.log_step("Master Modified StopLoss", f"GET /book/modify.php?id={master_oid}&name=StopLoss&val={sl_new}", extra=mod_sl_res)

            # 3. Modify Target on Master
            tp_new = f"{cmp + 1600.0:.2f}"
            mod_tp_res = master.modify_order(order_id=master_oid, name="Target", val=tp_new)
            assert mod_tp_res.get("status") == "success", f"Modify TP failed: {mod_tp_res}"
            rec.log_step("Master Modified Target", f"GET /book/modify.php?id={master_oid}&name=Target&val={tp_new}", extra=mod_tp_res)

            # 4. Verify updated SL and TP propagated across all 5 followers
            time.sleep(2.0)
            for f in followers:
                f_orders = f.get_open_orders()
                assert len(f_orders) >= 1
                act_sl = str(f_orders[0].get("sl", ""))
                act_tp = str(f_orders[0].get("tp", ""))
                sl_match = abs(float(act_sl or 0.0) - float(sl_new)) < 0.05
                tp_match = abs(float(act_tp or 0.0) - float(tp_new)) < 0.05
                rec.log_assertion(f"{f.name} Updated SL Propagated ({sl_new})", sl_new, act_sl, sl_match)
                rec.log_assertion(f"{f.name} Updated TP Propagated ({tp_new})", tp_new, act_tp, tp_match)
                assert sl_match, f"{f.name} SL not updated! Expected {sl_new}, got {act_sl}"
                assert tp_match, f"{f.name} TP not updated! Expected {tp_new}, got {act_tp}"

            # Cleanup
            master.squareoff_position(master_oid)
            time.sleep(2.0)
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    # =========================================================================
    # 2. PARTIAL POSITION CLOSE (MULTIPLIER MODE)
    # =========================================================================

    @pytest.mark.trading
    def test_02_partial_close_multiplier_fanout(self, adv_env):
        """
        Verify that when Master partially closes 0.20 lots out of 0.50 (leaving 0.30),
        all followers in Multiplier mode (3.0x) proportionally reduce their positions
        from 1.50 to 0.90 lots, and the remaining trade remains active and intact.
        """
        master = adv_env["master"]
        followers = adv_env["followers"]
        teardown = adv_env["teardown"]
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ADV-02-PRT-MUL",
            title="Partial Close Proportional Reduction (Multiplier Mode: 0.50 -> 0.30 => Follower 1.50 -> 0.90)",
            category="Trade Management"
        )

        teardown.assert_clean_slate()
        try:
            # 1. Master opens 0.50 lot BUY
            place_res = master.place_order(symbol=self.symbol, side="buy", lot=0.50, order_type="market")
            assert place_res.get("status") == "success"
            time.sleep(2.0)

            m_orders = master.get_open_orders()
            assert len(m_orders) >= 1
            master_oid = str(m_orders[0]["id"])

            # Verify initial follower 1.50 lots
            for f in followers:
                f_orders = f.get_open_orders()
                assert len(f_orders) >= 1
                assert abs(float(f_orders[0].get("lot", 0.0)) - 1.50) < 0.001
            rec.log_assertion("Initial Replicated Lots == 1.50 across all 5 followers", 1.50, 1.50, True)

            # 2. Master partially closes 0.20 lots (remaining = 0.30 lots)
            partial_res = master.partial_close_position(order_id=master_oid, partial_lot=0.20)
            assert partial_res.get("status") == "success", f"Partial close failed: {partial_res}"
            rec.log_step("Master Partial Close 0.20 Lots", f"GET /book/squareoff.php?id={master_oid}&close_mode=partial&partial_lot=0.20", extra=partial_res)

            # 3. Verify Master remaining lot is 0.30
            time.sleep(2.5)
            m_rem = master.get_open_orders()
            assert len(m_rem) >= 1
            m_lot_after = float(m_rem[0].get("lot", 0.0))
            rec.log_assertion("Master Remaining Lot == 0.30", 0.30, m_lot_after, abs(m_lot_after - 0.30) < 0.001)
            assert abs(m_lot_after - 0.30) < 0.001

            # 4. Verify all Followers proportionally reduced to 0.90 lots (0.30 * 3.0x = 0.90)
            for f in followers:
                f_rem = f.get_open_orders()
                assert len(f_rem) >= 1, f"{f.name} position was prematurely closed!"
                f_lot_after = float(f_rem[0].get("lot", 0.0))
                rec.log_assertion(f"{f.name} Proportional Remaining Lot == 0.90", 0.90, f_lot_after, abs(f_lot_after - 0.90) < 0.001)
                assert abs(f_lot_after - 0.90) < 0.001, f"{f.name} lot size {f_lot_after} != 0.90!"

            # 5. Clean close remaining position
            master.squareoff_position(master_oid)
            time.sleep(2.0)
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    # =========================================================================
    # 3. PARTIAL POSITION CLOSE (BALANCE-BASED MODE)
    # =========================================================================

    @pytest.mark.trading
    def test_03_partial_close_balance_mode_fanout(self, adv_env):
        """
        Verify partial position close in Balance-Based mode:
        Master reduces from 0.50 to 0.30 lots -> Follower reduces from 0.05 to 0.03 lots.
        """
        master = adv_env["master"]
        followers = adv_env["followers"]
        config_mgr = adv_env["config_mgr"]
        teardown = adv_env["teardown"]
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ADV-03-PRT-BAL",
            title="Partial Close Proportional Reduction (Balance Mode: 0.50 -> 0.30 => Follower 0.05 -> 0.03)",
            category="Trade Management"
        )

        teardown.assert_clean_slate()
        config_mgr.set_all_followers_mode(method="balance")

        try:
            place_res = master.place_order(symbol=self.symbol, side="buy", lot=0.50, order_type="market")
            assert place_res.get("status") == "success"
            time.sleep(2.0)

            m_orders = master.get_open_orders()
            master_oid = str(m_orders[0]["id"])

            # Verify initial 0.05 lots
            for f in followers:
                f_orders = f.get_open_orders()
                assert len(f_orders) >= 1
                assert abs(float(f_orders[0].get("lot", 0.0)) - 0.05) < 0.001

            # Master partially closes 0.20 lots
            master.partial_close_position(order_id=master_oid, partial_lot=0.20)
            time.sleep(2.5)

            # Master remaining lot = 0.30
            m_rem = master.get_open_orders()
            assert abs(float(m_rem[0].get("lot", 0.0)) - 0.30) < 0.001

            # Follower remaining lot: round(0.30 * 0.10, 2) = 0.03 lots
            for f in followers:
                f_rem = f.get_open_orders()
                assert len(f_rem) >= 1
                f_lot = float(f_rem[0].get("lot", 0.0))
                rec.log_assertion(f"{f.name} Balance Mode Remaining Lot == 0.03", 0.03, f_lot, abs(f_lot - 0.03) < 0.001)
                assert abs(f_lot - 0.03) < 0.001

            # Clean close
            master.squareoff_position(master_oid)
            time.sleep(2.0)
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

    # =========================================================================
    # 4. RAPID-FIRE BURST CONCURRENCY STRESS TEST
    # =========================================================================

    @pytest.mark.trading
    def test_04_rapid_burst_concurrency_stress(self, adv_env):
        """
        Stress test the Copy Trading fanout queue by firing a rapid burst
        of 4 consecutive market orders within 2 seconds.
        Validates replication integrity, order isolation, and mass square-off.
        """
        master = adv_env["master"]
        followers = adv_env["followers"]
        teardown = adv_env["teardown"]
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ADV-04-BURST",
            title="Rapid-Fire Scalping Burst Concurrency Test (4 Fast Orders)",
            category="Stress & Concurrency"
        )

        teardown.assert_clean_slate()
        burst_orders = []
        try:
            # Fire 4 consecutive orders in rapid succession
            t_burst_start = time.time()
            for i in range(4):
                side = "buy" if i % 2 == 0 else "sell"
                res = master.place_order(symbol=self.symbol, side=side, lot=0.50, order_type="market")
                assert res.get("status") == "success"
                burst_orders.append(res)
                time.sleep(0.3)
            burst_duration = round(time.time() - t_burst_start, 2)
            rec.log_step("Fired 4 Rapid Orders", "POST /trade/placeorder.php x4", extra={"burst_duration_sec": burst_duration})

            time.sleep(3.0)
            m_orders = master.get_open_orders()
            rec.log_assertion("Master Has 4 Open Positions", 4, len(m_orders), len(m_orders) == 4)
            assert len(m_orders) == 4, f"Expected 4 master orders, got {len(m_orders)}"

            # Verify each follower replicated all 4 orders
            for f in followers:
                f_orders = f.get_open_orders()
                rec.log_assertion(f"{f.name} Replicated All 4 Burst Orders", 4, len(f_orders), len(f_orders) == 4)
                assert len(f_orders) == 4, f"{f.name} only replicated {len(f_orders)} of 4 burst orders!"
                for fo in f_orders:
                    assert abs(float(fo.get("lot", 0.0)) - 1.50) < 0.001

            # Mass square-off all 4 master orders
            for mo in m_orders:
                master.squareoff_position(str(mo["id"]))
                time.sleep(0.3)

            time.sleep(3.0)
            clean_res = teardown.assert_clean_slate()
            rec.log_assertion("Mass Square-Off Clean Slate Verified", True, clean_res["status"] in ["clean", "recovered"], True)
            assert clean_res["status"] in ["clean", "recovered"]
            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

    def test_05_live_tp_sl_market_trigger_and_fanout_closure(self, adv_env):
        """CT-ADV-05: Real-market Take Profit / Stop Loss trigger and automated follower square-off."""
        master = adv_env["master"]
        followers = adv_env["followers"]
        teardown = adv_env["teardown"]
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ADV-05-TPSL-HIT",
            title="Real-Market TP/SL Hit & Automated Follower Fanout Closure",
            category="Risk & Auto Square-Off"
        )

        try:
            teardown.execute_complete_teardown()
            cmp = master.get_live_price(self.symbol)
            sl = f"{cmp - 2.0:.2f}"
            tp = f"{cmp + 2.0:.2f}"

            rec.log_step("Live Price Probed", "Probe execution price", extra={"cmp": cmp, "sl": sl, "tp": tp})
            res = master.place_order(symbol=self.symbol, side="buy", lot=0.10, sl=sl, target=tp)
            assert res.get("status") == "success"
            master_oid = str(res.get("data", {}).get("orderId", ""))

            # Monitor for live market tick to hit SL or TP (up to 30s)
            hit_detected = False
            for _ in range(15):
                time.sleep(2.0)
                m_open = master.get_open_orders()
                if len(m_open) == 0:
                    hit_detected = True
                    break

            if not hit_detected:
                # If market was flat, modify SL to current live price to ensure trigger
                current_cmp = master.get_live_price(self.symbol)
                master.modify_order(order_id=master_oid, name="StopLoss", val=str(current_cmp))
                for _ in range(10):
                    time.sleep(2.0)
                    if len(master.get_open_orders()) == 0:
                        hit_detected = True
                        break

            rec.log_assertion("Master Order Hit TP/SL & Auto-Closed", True, hit_detected, hit_detected)
            assert hit_detected, "Master order did not trigger TP/SL within timeout"

            # Assert all 5 followers closed automatically
            time.sleep(2.5)
            for f in followers:
                f_orders = f.get_open_orders()
                rec.log_assertion(f"{f.name} Automatically Closed via Fanout", 0, len(f_orders), len(f_orders) == 0)
                assert len(f_orders) == 0, f"{f.name} still has {len(f_orders)} open orders after master SL/TP hit!"

            rec.finish(status="PASS")
        finally:
            teardown.execute_complete_teardown()

