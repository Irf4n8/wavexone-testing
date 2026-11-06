"""
WavexOne Copy Trading: Playwright Browser Automation Test Suite.
Validates end-to-end Web UI authentication, active account ID display,
and real-time order book replication across Master and Follower browser windows.

Covers:
1. Multi-Account UI Login & Account ID Badge Verification (PW-ACC-01)
2. Multiplier Copy Trading UI Replication & Positions Table Verification (PW-MUL-01)
3. Balance-Based Copy Trading UI Replication & Sizing Verification (PW-BAL-01)
4. Equity-Based Copy Trading UI Replication & Sizing Verification (PW-EQU-01)
"""
import os
import time
import pytest
from playwright.sync_api import sync_playwright
from config.settings import WavexSettings
from core.playwright.wavex_page import WavexPlaywrightSession
from core.copy_trading.session_manager import CopyTradingSessionManager
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.copy_trading.copy_config_manager import CopyConfigManager
from core.logger import logger


@pytest.fixture(scope="class")
def playwright_env():
    """Fixture providing isolated browser contexts for Master and Follower."""
    sm = CopyTradingSessionManager()
    master_api = sm.initialize_master()
    followers_api = sm.initialize_followers()
    teardown_mgr = SafeTeardownHandler(master_api, followers_api)
    config_mgr = CopyConfigManager(master_api, followers_api)

    # Pre-flight clean slate
    teardown_mgr.assert_clean_slate()
    config_mgr.restore_baseline()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            slow_mo=500
        )
        
        master_ui = WavexPlaywrightSession(
            browser=browser,
            name="ctmaster",
            email=os.getenv("CT_MASTER_EMAIL", "ctmaster@mailinator.com"),
            password=WavexSettings.DEFAULT_PASSWORD,
            account_id="11060"
        )
        
        follower_ui = WavexPlaywrightSession(
            browser=browser,
            name="ctf1",
            email=os.getenv("CT_FOLLOWER_1_EMAIL", "ctf1@mailinator.com"),
            password=WavexSettings.DEFAULT_PASSWORD,
            account_id="11041"
        )

        yield {
            "browser": browser,
            "master_ui": master_ui,
            "follower_ui": follower_ui,
            "master_api": master_api,
            "followers_api": followers_api,
            "teardown_mgr": teardown_mgr,
            "config_mgr": config_mgr
        }

        # Safe teardown
        try:
            master_ui.close()
            follower_ui.close()
            browser.close()
        except Exception:
            pass
        teardown_mgr.execute_complete_teardown()
        config_mgr.restore_baseline()


class TestCopyTradingPlaywrightSuite:
    """End-to-End Browser UI Copy Trading Test Suite using Playwright."""

    def test_pw_01_ui_login_and_account_id_validation(self, playwright_env):
        """
        PW-ACC-01: Multi-Account UI Login & Staging Account ID Badge Validation.
        - Master logs in via Web UI -> asserts displayed account ID is '11060'.
        - Follower (ctf1) logs in via isolated browser context -> asserts displayed account ID is '11041'.
        - Captures full browser screenshot evidence.
        """
        master_ui = playwright_env["master_ui"]
        follower_ui = playwright_env["follower_ui"]

        # Master Login
        m_ok = master_ui.login()
        assert m_ok, "Master failed to log in to Web UI dashboard"
        m_ac_id = master_ui.verify_account_id()
        assert m_ac_id == "11060", f"Master account ID mismatch on UI! Expected 11060, got {m_ac_id}"
        master_ui.capture_screenshot("pw_master_login_11060.png")

        # Follower Login in separate context
        f_ok = follower_ui.login()
        assert f_ok, "Follower (ctf1) failed to log in to Web UI dashboard"
        f_ac_id = follower_ui.verify_account_id()
        assert f_ac_id == "11041", f"Follower account ID mismatch on UI! Expected 11041, got {f_ac_id}"
        follower_ui.capture_screenshot("pw_follower_login_11041.png")

    def test_pw_02_multiplier_copy_trading_ui_verification(self, playwright_env):
        """
        PW-MUL-01: Multiplier Mode (3.0x) UI Replication & Positions Table Verification.
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Follower Web UI dynamically displays replicated position with exact lot size 1.50 (0.50 * 3.0x).
        - Captures screenshots of both Master and Follower browser windows.
        - Master squares off; validates UI positions table clears to 0 on both accounts.
        """
        master_ui = playwright_env["master_ui"]
        follower_ui = playwright_env["follower_ui"]
        master_api = playwright_env["master_api"]
        teardown_mgr = playwright_env["teardown_mgr"]
        config_mgr = playwright_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        master_lot = 0.50
        expected_follower_lot = 1.50

        # Ensure baseline multiplier
        config_mgr.restore_baseline()
        teardown_mgr.assert_clean_slate()

        master_oid = None
        try:
            # Master places 0.50 lot
            place_res = master_api.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            assert place_res.get("status") == "success", f"Master order placement failed: {place_res}"
            
            # Verify in Master UI table
            m_pos = master_ui.wait_for_ui_position(symbol=symbol, expected_lot=master_lot, timeout=10.0)
            logger.info(f"Master UI Position: {m_pos}")
            master_ui.capture_screenshot("pw_mul_master_open_position.png")

            # Verify in Follower UI table: 1.50 lots
            f_pos = follower_ui.wait_for_ui_position(symbol=symbol, expected_lot=expected_follower_lot, timeout=12.0)
            logger.info(f"Follower UI Position: {f_pos}")
            follower_ui.capture_screenshot("pw_mul_follower_replicated_position.png")

            assert f_pos is not None, f"Follower UI did not display replicated position with {expected_follower_lot} lot!"
            act_lot = float(f_pos.get("lot") or 0.0)
            assert abs(act_lot - expected_follower_lot) < 0.001, (
                f"Follower UI lot mismatch! Expected {expected_follower_lot}, got {act_lot} ({f_pos.get('text')})"
            )

            # Master squares off position
            master_oid = place_res.get("data", {}).get("orderId")
            if not master_oid:
                m_orders = master_api.get_open_orders()
                if m_orders:
                    master_oid = m_orders[0]["id"]
            if master_oid:
                master_api.squareoff_position(master_oid)

            # Assert UI positions clear
            assert follower_ui.wait_for_ui_positions_cleared(timeout=10.0), "Follower UI positions table did not clear after squareoff!"
            assert master_ui.wait_for_ui_positions_cleared(timeout=10.0), "Master UI positions table did not clear after squareoff!"
            follower_ui.capture_screenshot("pw_mul_follower_cleared.png")

        finally:
            teardown_mgr.execute_complete_teardown()

    def test_pw_03_balance_copy_trading_ui_verification(self, playwright_env):
        """
        PW-BAL-01: Balance Mode UI Replication & Dynamic Sizing Verification.
        - Switch follower to copy method = 'balance'.
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Follower Web UI dynamically displays replicated position with dynamic balance ratio lot size 0.05.
        - Captures screenshot of Follower browser window showing 0.05 lot position.
        - Master squares off; validates UI positions table clears to 0.
        """
        master_ui = playwright_env["master_ui"]
        follower_ui = playwright_env["follower_ui"]
        master_api = playwright_env["master_api"]
        teardown_mgr = playwright_env["teardown_mgr"]
        config_mgr = playwright_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL
        master_lot = 0.50
        expected_follower_lot = 0.05

        # Switch to balance mode
        config_mgr.set_all_followers_mode(method="balance")
        teardown_mgr.assert_clean_slate()

        try:
            # Master places 0.50 lot
            place_res = master_api.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            assert place_res.get("status") == "success", f"Master order placement failed: {place_res}"

            # Verify in Follower UI table: 0.05 lots
            f_pos = follower_ui.wait_for_ui_position(symbol=symbol, expected_lot=expected_follower_lot, timeout=12.0)
            logger.info(f"Follower Balance Mode UI Position: {f_pos}")
            follower_ui.capture_screenshot("pw_bal_follower_replicated_005_lot.png")

            assert f_pos is not None, f"Follower UI did not display balance-replicated position with {expected_follower_lot} lot!"
            act_lot = float(f_pos.get("lot") or 0.0)
            assert abs(act_lot - expected_follower_lot) < 0.001, (
                f"Follower UI lot mismatch! Expected {expected_follower_lot}, got {act_lot} ({f_pos.get('text')})"
            )

            # Master squares off
            master_oid = place_res.get("data", {}).get("orderId")
            if not master_oid:
                m_orders = master_api.get_open_orders()
                if m_orders:
                    master_oid = m_orders[0]["id"]
            if master_oid:
                master_api.squareoff_position(master_oid)

            assert follower_ui.wait_for_ui_positions_cleared(timeout=10.0), "Follower UI table did not clear after squareoff!"
            follower_ui.capture_screenshot("pw_bal_follower_cleared.png")

        finally:
            teardown_mgr.execute_complete_teardown()
            config_mgr.restore_baseline()

    def test_pw_04_equity_copy_trading_ui_verification(self, playwright_env):
        """
        PW-EQU-01: Equity Mode UI Replication & Dynamic Sizing Verification.
        - Switch follower to copy method = 'equity'.
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Follower Web UI dynamically displays replicated position with dynamic equity ratio lot size 0.05.
        - Captures screenshot of Follower browser window showing 0.05 lot position.
        - Master squares off; validates UI positions table clears to 0.
        """
        master_ui = playwright_env["master_ui"]
        follower_ui = playwright_env["follower_ui"]
        master_api = playwright_env["master_api"]
        teardown_mgr = playwright_env["teardown_mgr"]
        config_mgr = playwright_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL
        master_lot = 0.50
        expected_follower_lot = 0.05

        # Switch to equity mode
        config_mgr.set_all_followers_mode(method="equity")
        teardown_mgr.assert_clean_slate()

        try:
            # Master places 0.50 lot
            place_res = master_api.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            assert place_res.get("status") == "success", f"Master order placement failed: {place_res}"

            # Verify in Follower UI table: 0.05 lots
            f_pos = follower_ui.wait_for_ui_position(symbol=symbol, expected_lot=expected_follower_lot, timeout=12.0)
            logger.info(f"Follower Equity Mode UI Position: {f_pos}")
            follower_ui.capture_screenshot("pw_equ_follower_replicated_005_lot.png")

            assert f_pos is not None, f"Follower UI did not display equity-replicated position with {expected_follower_lot} lot!"
            act_lot = float(f_pos.get("lot") or 0.0)
            assert abs(act_lot - expected_follower_lot) < 0.001, (
                f"Follower UI lot mismatch! Expected {expected_follower_lot}, got {act_lot} ({f_pos.get('text')})"
            )

            # Master squares off
            master_oid = place_res.get("data", {}).get("orderId")
            if not master_oid:
                m_orders = master_api.get_open_orders()
                if m_orders:
                    master_oid = m_orders[0]["id"]
            if master_oid:
                master_api.squareoff_position(master_oid)

            assert follower_ui.wait_for_ui_positions_cleared(timeout=10.0), "Follower UI table did not clear after squareoff!"
            follower_ui.capture_screenshot("pw_equ_follower_cleared.png")

        finally:
            teardown_mgr.execute_complete_teardown()
            config_mgr.restore_baseline()
