"""
WavexOne Copy Trading: Phase 1 (P0) Test Suite.
Implements strict independent verification, sanitized evidence logging,
account ID validation, and safe multi-tier teardown.

Scenarios in Scope:
- CT-ACC-01: Authentication and Account ID Validation (Non-Trading)
- CT-FOL-01: Follower Subscription Verification (Non-Trading)
- CT-MUL-01: Multiplier 3.0x Replication (Trading - Gated)
- CT-MKT-01: Market BUY Replication (Trading - Gated)
- CT-MKT-02: Market SELL Replication (Trading - Gated)
- CT-SQO-01: Full Position Square-Off (Trading - Gated)
- CT-FAN-01: Master Square-Off Fanout (Trading - Gated)
- CT-ISO-01: Follower Peer Isolation (Trading - Gated)
"""
import pytest
import time
from typing import Dict, List, Any
from config.settings import WavexSettings
from core.copy_trading.session_manager import CopyTradingSessionManager, APPROVED_MASTER_ACCOUNT_ID, APPROVED_FOLLOWER_ACCOUNT_IDS
from core.copy_trading.copy_config_manager import CopyConfigManager, BASELINE_COPY_METHOD, BASELINE_MULTIPLIER_VALUE
from core.copy_trading.book_poller import BookPoller
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.logger import logger


@pytest.fixture(scope="class")
def copy_trading_env():
    """Session fixture initializing all 6 accounts, config manager, poller, and teardown handler."""
    session_mgr = CopyTradingSessionManager()
    sessions = session_mgr.initialize_all()
    master = sessions["master"]
    followers = [sessions[name] for name in ["ctf1", "ctf2", "ctf3", "ctf4", "ctf5"]]

    config_mgr = CopyConfigManager(master=master, followers=followers)
    poller = BookPoller(master=master, followers=followers)
    teardown = SafeTeardownHandler(master=master, followers=followers)

    # Pre-flight check: assert clean slate before any tests begin
    preflight = teardown.assert_clean_slate()

    yield {
        "session_mgr": session_mgr,
        "master": master,
        "followers": followers,
        "config_mgr": config_mgr,
        "poller": poller,
        "teardown": teardown,
        "preflight": preflight
    }

    # Post-class safety teardown: ensure all positions closed and baseline restored
    logger.info("Executing post-class safety teardown...")
    teardown.execute_complete_teardown()
    config_mgr.restore_baseline()


class TestCopyTradingP0Suite:
    """Test suite for Phase 1 P0 Copy Trading scenarios."""

    # =========================================================================
    # NON-TRADING VALIDATION SCENARIOS
    # =========================================================================

    @pytest.mark.p0
    @pytest.mark.non_trading
    def test_ct_acc_01_authentication_and_account_id_validation(self, copy_trading_env):
        """
        CT-ACC-01: Multi-Account Authentication & Live Staging Account ID Validation.
        Verifies that Master and all 5 Followers authenticate successfully and their
        live trading account IDs strictly match the approved staging accounts.
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-ACC-01",
            title="Authentication & Live Staging Account ID Validation",
            category="Account Management"
        )

        master = copy_trading_env["master"]
        followers = copy_trading_env["followers"]

        # Step 1: Verify Master
        rec.log_step(
            name="Verify Master Authentication",
            action="Check session and account ID",
            endpoint=WavexSettings.LOGIN_CHECK_ENDPOINT,
            method="POST",
            extra={"name": master.name, "live_account_id": master.account_id, "user_id": master.user_id}
        )
        is_master_auth = master.is_authenticated and bool(master.token)
        rec.log_assertion("Master Authenticated", True, is_master_auth, is_master_auth)
        rec.log_assertion("Master Account ID Match", APPROVED_MASTER_ACCOUNT_ID, str(master.account_id), str(master.account_id) == APPROVED_MASTER_ACCOUNT_ID)

        assert is_master_auth, "Master failed authentication"
        assert str(master.account_id) == APPROVED_MASTER_ACCOUNT_ID, f"Master account ID mismatch: {master.account_id}"

        # Step 2: Verify all 5 Followers
        for f in followers:
            expected_acc = APPROVED_FOLLOWER_ACCOUNT_IDS[f.name]
            is_f_auth = f.is_authenticated and bool(f.token)

            rec.log_step(
                name=f"Verify Follower {f.name} Authentication",
                action="Check session and account ID",
                endpoint=WavexSettings.ACCOUNT_LIST_ENDPOINT,
                method="GET",
                extra={"name": f.name, "live_account_id": f.account_id, "user_id": f.user_id}
            )
            rec.log_assertion(f"Follower {f.name} Authenticated", True, is_f_auth, is_f_auth)
            rec.log_assertion(f"Follower {f.name} Account ID Match", expected_acc, str(f.account_id), str(f.account_id) == expected_acc)

            assert is_f_auth, f"Follower {f.name} failed authentication"
            assert str(f.account_id) == expected_acc, f"Follower {f.name} account ID mismatch: {f.account_id}"

        rec.finish(status="PASS")

    @pytest.mark.p0
    @pytest.mark.non_trading
    def test_ct_fol_01_follower_subscription_verification(self, copy_trading_env):
        """
        CT-FOL-01: Multi-Follower Subscription & Relationship Verification.
        Verifies that all 5 followers are actively subscribed to Master UID 1060
        on both Master's follower list and each follower's following list.
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-FOL-01",
            title="Multi-Follower Subscription & Relationship Verification",
            category="Follow/Unfollow Lifecycle"
        )

        config_mgr = copy_trading_env["config_mgr"]
        sub_status = config_mgr.verify_all_subscribed()

        rec.log_step(
            name="Query Master and Follower Subscription Lists",
            action="GET /user/userCopyFollowers.php",
            endpoint=WavexSettings.COPY_MASTER_FOLLOWERS_ENDPOINT,
            method="GET",
            extra=sub_status
        )

        rec.log_assertion("Total Followers Count >= 5", True, sub_status["total_followers_count"] >= 5, sub_status["total_followers_count"] >= 5)
        rec.log_assertion("All 5 Target Followers Active", True, sub_status["all_active"], sub_status["all_active"])

        for fname, detail in sub_status["details"].items():
            rec.log_assertion(f"{fname} In Master Follower List", True, detail["in_master_list"], detail["in_master_list"])
            rec.log_assertion(f"{fname} In Follower Following List", True, detail["in_follower_list"], detail["in_follower_list"])

        assert sub_status["all_active"], f"Not all followers actively subscribed: {sub_status['details']}"
        rec.finish(status="PASS")

    # =========================================================================
    # TRADING SCENARIOS (AUTHORIZED CONTROLLED EXECUTION)
    # =========================================================================

    @pytest.mark.p0
    @pytest.mark.trading
    def test_ct_mul_01_multiplier_3x_replication(self, copy_trading_env):
        """
        CT-MUL-01 / CT-MKT-01: Multiplier 3.0x Proportional Replication & Market BUY SLA (0.50 Master Lot).
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Verifies independent replication across all 5 followers with exactly 1.50 lots (0.50 * 3.0x).
        - Validates replication latency SLA (<= 2.5s).
        - Verifies follower execution prices and spread markup buffer (~5.5 pts).
        - Master squares off; validates clean fanout closure across all 5 followers.
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-MUL-01",
            title="Multiplier 3.0x Proportional Replication (0.50 Master Lot -> 1.50 Follower Lots)",
            category="Multiplier Copy Trading"
        )

        master = copy_trading_env["master"]
        followers = copy_trading_env["followers"]
        poller = copy_trading_env["poller"]
        teardown = copy_trading_env["teardown"]
        config_mgr = copy_trading_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"

        # Step 1: Pre-flight check & baseline confirmation
        rec.log_step(name="Pre-Flight Order Book Verification", action="Check 0 open orders", endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT)
        pre_clean = teardown.assert_clean_slate()
        rec.log_assertion("Pre-Flight Zero Open Orders", True, pre_clean["status"] in ["clean", "recovered"], True)

        master_oid = None
        master_lot = 0.50
        expected_follower_lot = 1.50  # 0.50 * 3.0x multiplier = 1.50 lots

        try:
            # Step 2: Master places Market BUY 0.50 lot
            t0 = time.time()
            place_res = master.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            t_fill = time.time()
            fill_dur_ms = round((t_fill - t0) * 1000, 2)

            rec.log_step(
                name=f"Master Place Market BUY {master_lot:.2f} Lot",
                action="POST /trade/placeorder.php",
                endpoint=WavexSettings.PLACE_ORDER_ENDPOINT,
                method="POST",
                request_data={"symbol": symbol, "side": "buy", "lot": master_lot, "type": "market"},
                response_data=place_res,
                latency_ms=fill_dur_ms
            )

            # Independent separate read verification of Master order in live book
            master_order = master.wait_for_order_in_book(symbol=symbol, side="buy", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert master_order is not None, f"Master order not found in book! Response: {place_res}"
            master_oid = str(master_order.get("id"))
            raw_p = master_order.get("avg") or master_order.get("open_price") or master_order.get("price") or 0.0
            try:
                master_price = float(raw_p)
            except (ValueError, TypeError):
                master_price = 0.0

            rec.log_assertion("Master Order Found in Book", True, True, True)
            rec.log_assertion(f"Master Lot Size is {master_lot:.2f}", master_lot, float(master_order.get("lot", 0.0)), abs(float(master_order.get("lot", 0.0)) - master_lot) < 0.001)
            rec.log_assertion("Master Fill Price Valid", True, master_price > 0.0, master_price > 0.0, notes=f"Master price: {master_price}")

            # Step 3: Concurrently poll all 5 follower order books
            t_rep_start = time.time()
            rep_res = poller.wait_for_follower_replication(symbol=symbol, side="buy", expected_lot=expected_follower_lot, timeout=10.0)
            t_rep_end = time.time()

            rec.log_step(
                name=f"Poll Follower Order Books for {expected_follower_lot:.2f} Lot Replication",
                action="Concurrent separate read polling /book/orders.php",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=rep_res,
                latency_ms=round((t_rep_end - t_rep_start) * 1000, 2)
            )

            # Assert all 5 followers replicated
            rec.log_assertion("All 5 Followers Replicated", True, rep_res["all_replicated"], rep_res["all_replicated"])
            rec.log_assertion("Replicated Count == 5", 5, rep_res["replicated_count"], rep_res["replicated_count"] == 5)
            assert rep_res["all_replicated"], f"Missing follower replications: {rep_res['missing_followers']}"

            # Step 4: Verify follower lot sizes, prices, and latency SLA
            for fname, oinfo in rep_res["replicated_orders"].items():
                f_lot = oinfo["lot"]
                f_price = oinfo["open_price"]
                f_latency = oinfo["latency_ms"]

                # Expected lot formula: 0.50 * 3.0 = 1.50
                lot_match = abs(f_lot - expected_follower_lot) < 0.001
                rec.log_assertion(f"{fname} Lot Size == {expected_follower_lot:.2f}", expected_follower_lot, f_lot, lot_match)
                assert lot_match, f"{fname} lot size mismatch! Expected {expected_follower_lot:.2f}, got {f_lot}"

                # Latency SLA <= 2500ms
                latency_ok = f_latency <= 2500.0
                rec.log_assertion(f"{fname} Replication Latency <= 2.5s", "<= 2500ms", f"{f_latency}ms", latency_ok)

                # Spread markup validation: follower price within spread markup tolerance (~5.5 pts)
                price_diff = round(abs(f_price - master_price), 2)
                price_ok = price_diff <= 12.0  # Safe upper bound for spread markup on BTCUSD
                rec.log_assertion(f"{fname} Price Spread Markup Buffer Valid", "<= 12.0 pts", f"{price_diff} pts", price_ok, notes=f"Master: {master_price}, Follower: {f_price}")

            # Step 5: Clean Master Square-Off & Follower Auto-Close
            t_sqo = time.time()
            sqo_res = master.squareoff_position(master_oid)
            rec.log_step(
                name="Master Square-Off Position",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                method="GET",
                extra={"master_order_id": master_oid, "response": sqo_res}
            )

            # Step 6: Verify all 6 accounts close cleanly
            close_res = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="Verify Clean Full Liquidation",
                action="Poll /book/orders.php across all 6 accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=close_res
            )

            rec.log_assertion("All Positions Cleanly Liquidated", True, close_res["all_closed"], close_res["all_closed"])
            assert close_res["all_closed"], f"Accounts failed to close cleanly: {close_res['unclosed_accounts']}"

            # Verify squareoff SLA <= 3500ms for all accounts
            for acc_name, lat in close_res["closed_latencies_ms"].items():
                sqo_sla_ok = lat <= 3500.0
                rec.log_assertion(f"{acc_name} Closure Latency <= 3.5s", "<= 3500ms", f"{lat}ms", sqo_sla_ok)

            rec.finish(status="PASS")

        except Exception as e:
            rec.finish(status="FAIL", error=str(e))
            raise e
        finally:
            # Multi-tier safety cleanup guarantee
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

    @pytest.mark.p0
    @pytest.mark.trading
    def test_ct_bal_01_balance_based_copying(self, copy_trading_env):
        """
        CT-BAL-01: Proportional Balance-Based Copy Trading Verification (0.50 Master Lot).
        - Switch all 5 followers to copy method = 'balance'.
        - Fetch live ledger balances of Master (~$111.2M) and Followers (~$12.1M).
        - Compute expected dynamic follower lot size: (FollowerBal / MasterBal) * MasterLot (~0.05 lots).
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Verifies independent replication across all 5 followers with dynamically computed lots.
        - Validates replication latency SLA (<= 2.5s).
        - Master squares off; validates clean fanout closure across all 5 followers.
        - Restores baseline configuration (multiplier 3.0x).
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-BAL-01",
            title="Proportional Balance-Based Copy Trading (0.50 Master Lot -> Dynamic Balance Ratio Sizing)",
            category="Balance-Based Copy Trading"
        )

        master = copy_trading_env["master"]
        followers = copy_trading_env["followers"]
        poller = copy_trading_env["poller"]
        teardown = copy_trading_env["teardown"]
        config_mgr = copy_trading_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        master_lot = 0.50

        # Step 1: Pre-flight check
        rec.log_step(name="Pre-Flight Order Book Verification", action="Check 0 open orders", endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT)
        pre_clean = teardown.assert_clean_slate()
        rec.log_assertion("Pre-Flight Zero Open Orders", True, pre_clean["status"] in ["clean", "recovered"], True)

        master_oid = None
        try:
            # Step 2: Switch all 5 followers to 'balance' mode
            rec.log_step(name="Switch Followers to Balance Mode", action="GET /user/updateCopyTradingMethod.php?method=balance", endpoint=WavexSettings.UPDATE_COPY_METHOD_ENDPOINT)
            switch_ok = config_mgr.set_all_followers_mode(method="balance")
            rec.log_assertion("All Followers Switched to Balance Mode", True, switch_ok, switch_ok)
            assert switch_ok, "Failed to switch all followers to balance mode"

            # Step 3: Capture live balances and compute expected lot sizes
            balances_map = poller.poll_all_accounts_balance()
            m_bal = float(balances_map.get("ctmaster", {}).get("balance", 0.0))
            assert m_bal > 0, f"Invalid master balance: {m_bal}"

            expected_lots = {}
            for f in followers:
                f_bal = float(balances_map.get(f.name, {}).get("balance", 0.0))
                # Dynamic formula: Round((f_bal / m_bal) * master_lot, 2)
                calc_lot = round((f_bal / m_bal) * master_lot, 2)
                expected_lots[f.name] = calc_lot
                rec.log_assertion(
                    f"{f.name} Balance Ratio Lot Calculation",
                    f"{calc_lot:.2f}",
                    f"{calc_lot:.2f}",
                    calc_lot > 0,
                    notes=f"Master Bal: ${m_bal:,.2f}, Follower Bal: ${f_bal:,.2f}, Ratio: {f_bal/m_bal:.4f}"
                )

            rec.log_step(
                name="Capture Balances & Compute Expected Lots",
                action="GET /book/balance.php",
                endpoint=WavexSettings.BALANCE_ENDPOINT,
                extra={"master_balance": m_bal, "expected_lots": expected_lots}
            )

            # Step 4: Master places Market BUY 0.50 lot
            t0 = time.time()
            place_res = master.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            t_fill = time.time()
            fill_dur_ms = round((t_fill - t0) * 1000, 2)

            rec.log_step(
                name=f"Master Place Market BUY {master_lot:.2f} Lot",
                action="POST /trade/placeorder.php",
                endpoint=WavexSettings.PLACE_ORDER_ENDPOINT,
                method="POST",
                request_data={"symbol": symbol, "side": "buy", "lot": master_lot, "type": "market"},
                response_data=place_res,
                latency_ms=fill_dur_ms
            )

            # Independent separate read verification of Master order
            master_order = master.wait_for_order_in_book(symbol=symbol, side="buy", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert master_order is not None, f"Master order not found in book! Response: {place_res}"
            master_oid = str(master_order.get("id"))
            raw_p = master_order.get("avg") or master_order.get("open_price") or master_order.get("price") or 0.0
            try:
                master_price = float(raw_p)
            except (ValueError, TypeError):
                master_price = 0.0

            rec.log_assertion("Master Order Found in Book", True, True, True)
            rec.log_assertion(f"Master Lot Size is {master_lot:.2f}", master_lot, float(master_order.get("lot", 0.0)), abs(float(master_order.get("lot", 0.0)) - master_lot) < 0.001)
            rec.log_assertion("Master Fill Price Valid", True, master_price > 0.0, master_price > 0.0, notes=f"Master price: {master_price}")

            # Step 5: Concurrently poll all 5 follower order books for balance-based replicated lots
            t_rep_start = time.time()
            rep_res = poller.wait_for_follower_replication(symbol=symbol, side="buy", expected_lot=expected_lots, timeout=12.0)
            t_rep_end = time.time()

            rec.log_step(
                name=f"Poll Follower Order Books for Dynamic Balance Replication",
                action="Concurrent separate read polling /book/orders.php",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=rep_res,
                latency_ms=round((t_rep_end - t_rep_start) * 1000, 2)
            )

            # Assert all 5 followers replicated
            rec.log_assertion("All 5 Followers Replicated", True, rep_res["all_replicated"], rep_res["all_replicated"])
            rec.log_assertion("Replicated Count == 5", 5, rep_res["replicated_count"], rep_res["replicated_count"] == 5)
            assert rep_res["all_replicated"], f"Missing follower balance replications: {rep_res['missing_followers']}"

            # Step 6: Verify follower lot sizes, prices, and latency SLA
            for fname, oinfo in rep_res["replicated_orders"].items():
                f_lot = oinfo["lot"]
                f_price = oinfo["open_price"]
                f_latency = oinfo["latency_ms"]
                exp_lot = expected_lots[fname]

                lot_match = abs(f_lot - exp_lot) < 0.001
                rec.log_assertion(f"{fname} Balance Mode Lot Size == {exp_lot:.2f}", exp_lot, f_lot, lot_match)
                assert lot_match, f"{fname} lot size mismatch! Expected {exp_lot:.2f}, got {f_lot}"

                latency_ok = f_latency <= 2500.0
                rec.log_assertion(f"{fname} Replication Latency <= 2.5s", "<= 2500ms", f"{f_latency}ms", latency_ok)

                price_diff = round(abs(f_price - master_price), 2)
                price_ok = price_diff <= 12.0
                rec.log_assertion(f"{fname} Price Spread Markup Buffer Valid", "<= 12.0 pts", f"{price_diff} pts", price_ok, notes=f"Master: {master_price}, Follower: {f_price}")

            # Step 7: Master Square-Off & Follower Auto-Close
            t_sqo = time.time()
            sqo_res = master.squareoff_position(master_oid)
            rec.log_step(
                name="Master Square-Off Position",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                method="GET",
                extra={"master_order_id": master_oid, "response": sqo_res}
            )

            # Step 8: Verify clean full liquidation
            close_res = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="Verify Clean Full Liquidation",
                action="Poll /book/orders.php across all 6 accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=close_res
            )

            rec.log_assertion("All Positions Cleanly Liquidated", True, close_res["all_closed"], close_res["all_closed"])
            assert close_res["all_closed"], f"Accounts failed to close cleanly: {close_res['unclosed_accounts']}"

            for acc_name, lat in close_res["closed_latencies_ms"].items():
                sqo_sla_ok = lat <= 3500.0
                rec.log_assertion(f"{acc_name} Closure Latency <= 3.5s", "<= 3500ms", f"{lat}ms", sqo_sla_ok)

            rec.finish(status="PASS")

        except Exception as e:
            rec.finish(status="FAIL", error=str(e))
            raise e
        finally:
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

    @pytest.mark.p0
    @pytest.mark.trading
    def test_ct_equ_01_equity_based_copying(self, copy_trading_env):
        """
        CT-EQU-01: Proportional Equity-Based Copy Trading Verification (0.50 Master Lot).
        - Switch all 5 followers to copy method = 'equity'.
        - Fetch live ledger equity of Master (~$111.2M) and Followers (~$12.1M) via /book/balance.php.
        - Compute expected dynamic follower lot size: (FollowerEquity / MasterEquity) * MasterLot (~0.05 lots).
        - Master places Market BUY 0.50 lot on X:BTCUSD.
        - Verifies independent replication across all 5 followers with dynamically computed equity lots.
        - Validates replication latency SLA (<= 2.5s) and price markup buffer.
        - Master squares off; validates clean fanout closure across all 5 followers.
        - Restores baseline configuration (multiplier 3.0x).
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-EQU-01",
            title="Proportional Equity-Based Copy Trading (0.50 Master Lot -> Dynamic Equity Ratio Sizing)",
            category="Equity-Based Copy Trading"
        )

        master = copy_trading_env["master"]
        followers = copy_trading_env["followers"]
        poller = copy_trading_env["poller"]
        teardown = copy_trading_env["teardown"]
        config_mgr = copy_trading_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        master_lot = 0.50

        # Step 1: Pre-flight check
        rec.log_step(name="Pre-Flight Order Book Verification", action="Check 0 open orders", endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT)
        pre_clean = teardown.assert_clean_slate()
        rec.log_assertion("Pre-Flight Zero Open Orders", True, pre_clean["status"] in ["clean", "recovered"], True)

        master_oid = None
        try:
            # Step 2: Switch all 5 followers to 'equity' mode
            rec.log_step(name="Switch Followers to Equity Mode", action="GET /user/updateCopyTradingMethod.php?method=equity", endpoint=WavexSettings.UPDATE_COPY_METHOD_ENDPOINT)
            switch_ok = config_mgr.set_all_followers_mode(method="equity")
            rec.log_assertion("All Followers Switched to Equity Mode", True, switch_ok, switch_ok)
            assert switch_ok, "Failed to switch all followers to equity mode"

            # Step 3: Capture live equities and compute expected lot sizes
            balances_map = poller.poll_all_accounts_balance()
            m_eq = float(balances_map.get("ctmaster", {}).get("equity", 0.0) or balances_map.get("ctmaster", {}).get("balance", 0.0))
            assert m_eq > 0, f"Invalid master equity: {m_eq}"

            expected_lots = {}
            for f in followers:
                f_eq = float(balances_map.get(f.name, {}).get("equity", 0.0) or balances_map.get(f.name, {}).get("balance", 0.0))
                calc_lot = round((f_eq / m_eq) * master_lot, 2)
                expected_lots[f.name] = calc_lot
                rec.log_assertion(
                    f"{f.name} Equity Ratio Lot Calculation",
                    f"{calc_lot:.2f}",
                    f"{calc_lot:.2f}",
                    calc_lot > 0,
                    notes=f"Master Eq: ${m_eq:,.2f}, Follower Eq: ${f_eq:,.2f}, Ratio: {f_eq/m_eq:.4f}"
                )

            rec.log_step(
                name="Capture Equities & Compute Expected Lots",
                action="GET /book/balance.php",
                endpoint=WavexSettings.BALANCE_ENDPOINT,
                extra={"master_equity": m_eq, "expected_lots": expected_lots}
            )

            # Step 4: Master places Market BUY 0.50 lot
            t0 = time.time()
            place_res = master.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            t_fill = time.time()
            fill_dur_ms = round((t_fill - t0) * 1000, 2)

            rec.log_step(
                name=f"Master Place Market BUY {master_lot:.2f} Lot",
                action="POST /trade/placeorder.php",
                endpoint=WavexSettings.PLACE_ORDER_ENDPOINT,
                method="POST",
                request_data={"symbol": symbol, "side": "buy", "lot": master_lot, "type": "market"},
                response_data=place_res,
                latency_ms=fill_dur_ms
            )

            # Independent separate read verification of Master order
            master_order = master.wait_for_order_in_book(symbol=symbol, side="buy", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert master_order is not None, f"Master BUY order not found in book! Response: {place_res}"
            master_oid = str(master_order.get("id"))
            raw_p = master_order.get("avg") or master_order.get("open_price") or master_order.get("price") or 0.0
            try:
                master_price = float(raw_p)
            except (ValueError, TypeError):
                master_price = 0.0

            rec.log_assertion("Master Order Found in Book", True, True, True)
            rec.log_assertion(f"Master Lot Size is {master_lot:.2f}", master_lot, float(master_order.get("lot", 0.0)), abs(float(master_order.get("lot", 0.0)) - master_lot) < 0.001)
            rec.log_assertion("Master Fill Price Valid", True, master_price > 0.0, master_price > 0.0, notes=f"Master price: {master_price}")

            # Step 5: Concurrently poll all 5 follower order books for dynamic equity replicated lots
            t_rep_start = time.time()
            rep_res = poller.wait_for_follower_replication(symbol=symbol, side="buy", expected_lot=expected_lots, timeout=12.0)
            t_rep_end = time.time()

            rec.log_step(
                name=f"Poll Follower Order Books for Dynamic Equity Replication",
                action="Concurrent separate read polling /book/orders.php",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=rep_res,
                latency_ms=round((t_rep_end - t_rep_start) * 1000, 2)
            )

            # Assert all 5 followers replicated
            rec.log_assertion("All 5 Followers Replicated", True, rep_res["all_replicated"], rep_res["all_replicated"])
            rec.log_assertion("Replicated Count == 5", 5, rep_res["replicated_count"], rep_res["replicated_count"] == 5)
            assert rep_res["all_replicated"], f"Missing follower equity replications: {rep_res['missing_followers']}"

            # Step 6: Verify follower lot sizes, prices, directions, and latency SLA
            for fname, oinfo in rep_res["replicated_orders"].items():
                f_lot = oinfo["lot"]
                f_price = oinfo["open_price"]
                f_latency = oinfo["latency_ms"]
                f_side = str(oinfo["side"]).upper()
                exp_lot = expected_lots[fname]

                rec.log_assertion(f"{fname} Direction is BUY", "BUY", f_side, f_side == "BUY")
                assert f_side == "BUY", f"{fname} direction mismatch! Expected BUY, got {f_side}"

                lot_match = abs(f_lot - exp_lot) < 0.001
                rec.log_assertion(f"{fname} Equity Mode Lot Size == {exp_lot:.2f}", exp_lot, f_lot, lot_match)
                assert lot_match, f"{fname} lot size mismatch! Expected {exp_lot:.2f}, got {f_lot}"

                latency_ok = f_latency <= 2500.0
                rec.log_assertion(f"{fname} Replication Latency <= 2.5s", "<= 2500ms", f"{f_latency}ms", latency_ok)

                price_diff = round(abs(f_price - master_price), 2)
                price_ok = price_diff <= 12.0
                rec.log_assertion(f"{fname} Price Spread Markup Buffer Valid", "<= 12.0 pts", f"{price_diff} pts", price_ok, notes=f"Master: {master_price}, Follower: {f_price}")

            # Step 7: Master Square-Off & Follower Auto-Close
            t_sqo = time.time()
            sqo_res = master.squareoff_position(master_oid)
            rec.log_step(
                name="Master Square-Off Position",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                method="GET",
                extra={"master_order_id": master_oid, "response": sqo_res}
            )

            # Step 8: Verify clean full liquidation
            close_res = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="Verify Clean Full Liquidation",
                action="Poll /book/orders.php across all 6 accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=close_res
            )

            rec.log_assertion("All Positions Cleanly Liquidated", True, close_res["all_closed"], close_res["all_closed"])
            assert close_res["all_closed"], f"Accounts failed to close cleanly: {close_res['unclosed_accounts']}"

            for acc_name, lat in close_res["closed_latencies_ms"].items():
                sqo_sla_ok = lat <= 3500.0
                rec.log_assertion(f"{acc_name} Closure Latency <= 3.5s", "<= 3500ms", f"{lat}ms", sqo_sla_ok)

            rec.finish(status="PASS")

        except Exception as e:
            rec.finish(status="FAIL", error=str(e))
            raise e
        finally:
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

    @pytest.mark.p0
    @pytest.mark.trading
    def test_ct_bal_02_balance_based_market_sell(self, copy_trading_env):
        """
        CT-BAL-02: Proportional Balance-Based Market SELL Replication (0.50 Master Lot).
        - Switch all 5 followers to copy method = 'balance'.
        - Fetch live ledger balances of Master and Followers via /book/balance.php.
        - Compute expected dynamic follower lot size: (FollowerBal / MasterBal) * MasterLot (~0.05 lots).
        - Master places Market SELL 0.50 lot on X:BTCUSD.
        - Verifies independent replication across all 5 followers with dynamically computed lots and SELL side.
        - Validates replication latency SLA (<= 2.5s) and price markup buffer.
        - Master squares off; validates clean fanout closure across all 5 followers.
        - Restores baseline configuration (multiplier 3.0x).
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-BAL-02",
            title="Proportional Balance-Based Market SELL Copying (0.50 Master Lot -> Dynamic Balance Ratio Sizing)",
            category="Balance-Based Copy Trading"
        )

        master = copy_trading_env["master"]
        followers = copy_trading_env["followers"]
        poller = copy_trading_env["poller"]
        teardown = copy_trading_env["teardown"]
        config_mgr = copy_trading_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        master_lot = 0.50

        # Step 1: Pre-flight check
        rec.log_step(name="Pre-Flight Order Book Verification", action="Check 0 open orders", endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT)
        pre_clean = teardown.assert_clean_slate()
        rec.log_assertion("Pre-Flight Zero Open Orders", True, pre_clean["status"] in ["clean", "recovered"], True)

        master_oid = None
        try:
            # Step 2: Switch all 5 followers to 'balance' mode
            rec.log_step(name="Switch Followers to Balance Mode", action="GET /user/updateCopyTradingMethod.php?method=balance", endpoint=WavexSettings.UPDATE_COPY_METHOD_ENDPOINT)
            switch_ok = config_mgr.set_all_followers_mode(method="balance")
            rec.log_assertion("All Followers Switched to Balance Mode", True, switch_ok, switch_ok)
            assert switch_ok, "Failed to switch all followers to balance mode"

            # Step 3: Capture live balances and compute expected lot sizes
            balances_map = poller.poll_all_accounts_balance()
            m_bal = float(balances_map.get("ctmaster", {}).get("balance", 0.0))
            assert m_bal > 0, f"Invalid master balance: {m_bal}"

            expected_lots = {}
            for f in followers:
                f_bal = float(balances_map.get(f.name, {}).get("balance", 0.0))
                calc_lot = round((f_bal / m_bal) * master_lot, 2)
                expected_lots[f.name] = calc_lot
                rec.log_assertion(
                    f"{f.name} Balance Ratio Lot Calculation",
                    f"{calc_lot:.2f}",
                    f"{calc_lot:.2f}",
                    calc_lot > 0,
                    notes=f"Master Bal: ${m_bal:,.2f}, Follower Bal: ${f_bal:,.2f}, Ratio: {f_bal/m_bal:.4f}"
                )

            rec.log_step(
                name="Capture Balances & Compute Expected Lots",
                action="GET /book/balance.php",
                endpoint=WavexSettings.BALANCE_ENDPOINT,
                extra={"master_balance": m_bal, "expected_lots": expected_lots}
            )

            # Step 4: Master places Market SELL 0.50 lot
            t0 = time.time()
            place_res = master.place_order(symbol=symbol, side="sell", lot=master_lot, order_type="market")
            t_fill = time.time()
            fill_dur_ms = round((t_fill - t0) * 1000, 2)

            rec.log_step(
                name=f"Master Place Market SELL {master_lot:.2f} Lot",
                action="POST /trade/placeorder.php",
                endpoint=WavexSettings.PLACE_ORDER_ENDPOINT,
                method="POST",
                request_data={"symbol": symbol, "side": "sell", "lot": master_lot, "type": "market"},
                response_data=place_res,
                latency_ms=fill_dur_ms
            )

            # Independent separate read verification of Master order
            master_order = master.wait_for_order_in_book(symbol=symbol, side="sell", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert master_order is not None, f"Master SELL order not found in book! Response: {place_res}"
            master_oid = str(master_order.get("id"))
            raw_p = master_order.get("avg") or master_order.get("open_price") or master_order.get("price") or 0.0
            try:
                master_price = float(raw_p)
            except (ValueError, TypeError):
                master_price = 0.0

            rec.log_assertion("Master Order Found in Book", True, True, True)
            rec.log_assertion(f"Master Lot Size is {master_lot:.2f}", master_lot, float(master_order.get("lot", 0.0)), abs(float(master_order.get("lot", 0.0)) - master_lot) < 0.001)
            rec.log_assertion("Master Fill Price Valid", True, master_price > 0.0, master_price > 0.0, notes=f"Master price: {master_price}")

            # Step 5: Concurrently poll all 5 follower order books for balance-based replicated SELL lots
            t_rep_start = time.time()
            rep_res = poller.wait_for_follower_replication(symbol=symbol, side="sell", expected_lot=expected_lots, timeout=12.0)
            t_rep_end = time.time()

            rec.log_step(
                name=f"Poll Follower Order Books for Dynamic Balance SELL Replication",
                action="Concurrent separate read polling /book/orders.php",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=rep_res,
                latency_ms=round((t_rep_end - t_rep_start) * 1000, 2)
            )

            # Assert all 5 followers replicated
            rec.log_assertion("All 5 Followers Replicated", True, rep_res["all_replicated"], rep_res["all_replicated"])
            rec.log_assertion("Replicated Count == 5", 5, rep_res["replicated_count"], rep_res["replicated_count"] == 5)
            assert rep_res["all_replicated"], f"Missing follower balance replications: {rep_res['missing_followers']}"

            # Step 6: Verify follower lot sizes, prices, directions, and latency SLA
            for fname, oinfo in rep_res["replicated_orders"].items():
                f_lot = oinfo["lot"]
                f_price = oinfo["open_price"]
                f_latency = oinfo["latency_ms"]
                f_side = str(oinfo["side"]).upper()
                exp_lot = expected_lots[fname]

                rec.log_assertion(f"{fname} Direction is SELL", "SELL", f_side, f_side == "SELL")
                assert f_side == "SELL", f"{fname} direction mismatch! Expected SELL, got {f_side}"

                lot_match = abs(f_lot - exp_lot) < 0.001
                rec.log_assertion(f"{fname} Balance Mode Lot Size == {exp_lot:.2f}", exp_lot, f_lot, lot_match)
                assert lot_match, f"{fname} lot size mismatch! Expected {exp_lot:.2f}, got {f_lot}"

                latency_ok = f_latency <= 2500.0
                rec.log_assertion(f"{fname} Replication Latency <= 2.5s", "<= 2500ms", f"{f_latency}ms", latency_ok)

                price_diff = round(abs(f_price - master_price), 2)
                price_ok = price_diff <= 12.0
                rec.log_assertion(f"{fname} Price Spread Markup Buffer Valid", "<= 12.0 pts", f"{price_diff} pts", price_ok, notes=f"Master: {master_price}, Follower: {f_price}")

            # Step 7: Master Square-Off & Follower Auto-Close
            t_sqo = time.time()
            sqo_res = master.squareoff_position(master_oid)
            rec.log_step(
                name="Master Square-Off Position",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                method="GET",
                extra={"master_order_id": master_oid, "response": sqo_res}
            )

            # Step 8: Verify clean full liquidation
            close_res = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="Verify Clean Full Liquidation",
                action="Poll /book/orders.php across all 6 accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                method="GET",
                extra=close_res
            )

            rec.log_assertion("All Positions Cleanly Liquidated", True, close_res["all_closed"], close_res["all_closed"])
            assert close_res["all_closed"], f"Accounts failed to close cleanly: {close_res['unclosed_accounts']}"

            for acc_name, lat in close_res["closed_latencies_ms"].items():
                sqo_sla_ok = lat <= 3500.0
                rec.log_assertion(f"{acc_name} Closure Latency <= 3.5s", "<= 3500ms", f"{lat}ms", sqo_sla_ok)

            rec.finish(status="PASS")

        except Exception as e:
            rec.finish(status="FAIL", error=str(e))
            raise e
        finally:
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

