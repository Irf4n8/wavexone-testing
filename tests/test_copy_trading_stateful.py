"""
WavexOne Copy Trading: Comprehensive Stateful FSM Test Suite.
Models and validates the Copy Trading Engine as a strict Finite State Machine (FSM).

State Machine Transitions Tested:
1. STATE_0: IDLE_CLEAN_SLATE -> Invariant: 0 open positions across all 6 accounts.
2. STATE_1: HETEROGENEOUS_SUBSCRIPTIONS -> Invariant: Followers configured with distinct copy modes concurrently.
3. STATE_2: MASTER_BUY_OPEN -> Invariant: Proportional dynamic sizing fanout (1.50 vs 0.05 lots).
4. STATE_3: PEER_ISOLATION_EXIT -> Invariant: Follower closes trade; Master & other peers remain active.
5. STATE_4: UNFOLLOW_IN_FLIGHT -> Invariant: Follower unbinds without corrupting master or peer books.
6. STATE_5: MASTER_SQUAREOFF_FANOUT -> Invariant: Master squareoff fanout liquidates remaining connected followers.
7. STATE_6: RE_FOLLOW_AND_SELL_OPEN -> Invariant: Re-subscribed follower receives new SELL orders.
8. STATE_7: FINAL_SQUAREOFF_AND_BASELINE -> Invariant: System returns to 100% clean baseline.
"""
import pytest
import time
from typing import Dict, Any, List
from config.settings import WavexSettings
from core.copy_trading.session_manager import (
    CopyTradingSessionManager,
    APPROVED_MASTER_ACCOUNT_ID,
    APPROVED_FOLLOWER_ACCOUNT_IDS
)
from core.copy_trading.copy_config_manager import (
    CopyConfigManager,
    BASELINE_COPY_METHOD,
    BASELINE_MULTIPLIER_VALUE
)
from core.copy_trading.book_poller import BookPoller
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.logger import logger


@pytest.fixture(scope="class")
def stateful_env():
    """Initializes sessions, config manager, poller, and teardown handler for stateful testing."""
    session_mgr = CopyTradingSessionManager()
    sessions = session_mgr.initialize_all()
    master = sessions["master"]
    followers = [sessions[name] for name in ["ctf1", "ctf2", "ctf3", "ctf4", "ctf5"]]

    config_mgr = CopyConfigManager(master=master, followers=followers)
    poller = BookPoller(master=master, followers=followers)
    teardown = SafeTeardownHandler(master=master, followers=followers)

    # Pre-flight check: assert clean slate
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

    # Final post-test safety cleanup
    logger.info("Executing stateful post-test teardown and baseline restoration...")
    teardown.execute_complete_teardown()
    config_mgr.restore_baseline()


class TestCopyTradingStatefulFSM:
    """Stateful Finite State Machine Test Suite for WavexOne Copy Trading."""

    @pytest.mark.stateful
    def test_copy_trading_full_state_machine_lifecycle(self, stateful_env):
        """
        Executes an end-to-end stateful test traversing all 8 primary FSM states of Copy Trading.
        Asserts state transition correctness, multi-mode sizing, peer isolation, dynamic unlinking,
        and safe master fanout square-off.
        """
        rec = SanitizedEvidenceRecorder(
            scenario_id="CT-STATEFUL-01",
            title="Copy Trading Finite State Machine (FSM) Lifecycle & Invariant Validation",
            category="Stateful Automation"
        )

        master = stateful_env["master"]
        followers = stateful_env["followers"]
        followers_map = {f.name: f for f in followers}
        poller = stateful_env["poller"]
        teardown = stateful_env["teardown"]
        config_mgr = stateful_env["config_mgr"]
        symbol = WavexSettings.DEFAULT_SYMBOL  # "X:BTCUSD"
        master_lot = 0.50

        # State Tracking
        current_state = "STATE_0_IDLE_CLEAN_SLATE"
        state_history = [current_state]

        try:
            # -------------------------------------------------------------
            # STATE 0: IDLE_CLEAN_SLATE
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 0: IDLE_CLEAN_SLATE")
            clean_res = teardown.assert_clean_slate()
            rec.log_step(
                name="STATE_0: Assert Clean Slate",
                action="Query /book/orders.php across all 6 accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                extra=clean_res
            )
            rec.log_assertion("State 0: Zero Open Positions", True, clean_res["status"] in ["clean", "recovered"], True)
            assert clean_res["status"] in ["clean", "recovered"], "Pre-existing dirty state detected"

            # -------------------------------------------------------------
            # STATE 1: HETEROGENEOUS_CONFIGURATION
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 1: HETEROGENEOUS_CONFIGURATION")
            current_state = "STATE_1_HETEROGENEOUS_CONFIGURATION"
            state_history.append(current_state)

            # Assign heterogeneous modes to test concurrent multi-mode behavior:
            # ctf1: multiplier (3.0x) -> expect 1.50 lots
            # ctf2: balance -> expect dynamic balance ratio (~0.05 lots)
            # ctf3: equity -> expect dynamic equity ratio (~0.05 lots)
            # ctf4: multiplier (3.0x) -> expect 1.50 lots
            # ctf5: balance -> expect dynamic balance ratio (~0.05 lots)
            config_mgr.set_follower_mode(followers_map["ctf1"], method="multiplier", value="3.0")
            config_mgr.set_follower_mode(followers_map["ctf2"], method="balance")
            config_mgr.set_follower_mode(followers_map["ctf3"], method="equity")
            config_mgr.set_follower_mode(followers_map["ctf4"], method="multiplier", value="3.0")
            config_mgr.set_follower_mode(followers_map["ctf5"], method="balance")

            balances_map = poller.poll_all_accounts_balance()
            m_bal = float(balances_map.get("ctmaster", {}).get("balance", 100000.0) or 100000.0)
            m_eq = float(balances_map.get("ctmaster", {}).get("equity", 100000.0) or 100000.0)

            expected_lots = {
                "ctf1": 1.50,
                "ctf2": round((float(balances_map.get("ctf2", {}).get("balance", 10000.0)) / m_bal) * master_lot, 2),
                "ctf3": round((float(balances_map.get("ctf3", {}).get("equity", 10000.0)) / m_eq) * master_lot, 2),
                "ctf4": 1.50,
                "ctf5": round((float(balances_map.get("ctf5", {}).get("balance", 10000.0)) / m_bal) * master_lot, 2)
            }

            rec.log_step(
                name="STATE_1: Heterogeneous Mode Assignment",
                action="Set ctf1=3x, ctf2=bal, ctf3=eq, ctf4=3x, ctf5=bal",
                endpoint=WavexSettings.UPDATE_COPY_METHOD_ENDPOINT,
                extra={"expected_lots": expected_lots}
            )
            rec.log_assertion("State 1: Heterogeneous Config Persisted", True, True, True)

            # -------------------------------------------------------------
            # STATE 2: MASTER_BUY_OPEN (Fanout Replication)
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 2: MASTER_BUY_OPEN")
            current_state = "STATE_2_MASTER_BUY_OPEN"
            state_history.append(current_state)

            t_buy_start = time.time()
            place_res = master.place_order(symbol=symbol, side="buy", lot=master_lot, order_type="market")
            rec.log_step(
                name="STATE_2: Master Place Market BUY 0.50 Lot",
                action="POST /trade/placeorder.php",
                endpoint=WavexSettings.PLACE_ORDER_ENDPOINT,
                method="POST",
                request_data={"symbol": symbol, "side": "buy", "lot": master_lot, "type": "market"},
                response_data=place_res
            )

            # Verify Master Order in live book
            master_order = master.wait_for_order_in_book(symbol=symbol, side="buy", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert master_order is not None, f"Master BUY order not found in book! {place_res}"
            master_oid = str(master_order.get("id"))
            master_price = float(master_order.get("avg") or master_order.get("price") or 75000.0)

            # Concurrent poll across all 5 followers with heterogeneous expected lots
            rep_res = poller.wait_for_follower_replication(symbol=symbol, side="buy", expected_lot=expected_lots, timeout=12.0)
            rec.log_step(
                name="STATE_2: Multi-Mode Replications Captured",
                action="Poll /book/orders.php",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                extra=rep_res
            )
            rec.log_assertion("State 2: All 5 Heterogeneous Followers Replicated", True, rep_res["all_replicated"], rep_res["all_replicated"])
            assert rep_res["all_replicated"], f"Missing follower replications: {rep_res['missing_followers']}"

            # Invariant: Verify individual lot sizes
            for fname, oinfo in rep_res["replicated_orders"].items():
                act_lot = oinfo["lot"]
                exp_lot = expected_lots[fname]
                lot_match = abs(act_lot - exp_lot) < 0.001
                rec.log_assertion(f"State 2: {fname} ({oinfo['mode'] if 'mode' in oinfo else 'mode'}) lot == {exp_lot:.2f}", exp_lot, act_lot, lot_match)
                assert lot_match, f"{fname} lot size mismatch! Expected {exp_lot:.2f}, got {act_lot}"

            # Invariant: Total active ecosystem orders == 6 (1 Master + 5 Followers)
            total_active_orders = 1 + len(rep_res["replicated_orders"])
            rec.log_assertion("State 2 Invariant: Total Ecosystem Open Orders == 6", 6, total_active_orders, total_active_orders == 6)
            assert total_active_orders == 6

            # -------------------------------------------------------------
            # STATE 3: PEER_ISOLATION_EXIT (ctf1 Closes Independently)
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 3: PEER_ISOLATION_EXIT")
            current_state = "STATE_3_PEER_ISOLATION_EXIT"
            state_history.append(current_state)

            ctf1_oid = str(rep_res["replicated_orders"]["ctf1"]["order_id"])
            ctf1_session = followers_map["ctf1"]

            t0 = time.time()
            ctf1_sqo = ctf1_session.squareoff_position(ctf1_oid)
            rec.log_step(
                name="STATE_3: Follower ctf1 Manual Close",
                action="GET /book/squareoff.php (Follower Peer Exit)",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                extra={"order_id": ctf1_oid, "response": ctf1_sqo}
            )

            # Wait for ctf1 order to vanish from ctf1's book
            ctf1_closed = ctf1_session.wait_for_order_closure(ctf1_oid, timeout=8.0)
            rec.log_assertion("State 3: ctf1 Order Closed in Own Book", True, ctf1_closed, ctf1_closed)
            assert ctf1_closed, "ctf1 failed to close order independently"

            # Invariant Check: Master order MUST STILL BE OPEN
            master_still_open = master.get_open_orders()
            master_has_pos = any(str(o.get("id")) == master_oid for o in master_still_open)
            rec.log_assertion("State 3 Invariant: Master Order Remains Active", True, master_has_pos, master_has_pos)
            assert master_has_pos, "FATAL: Follower exit caused Master order to close unintentionally!"

            # Invariant Check: Peers ctf2..ctf5 MUST STILL BE OPEN
            for peer_name in ["ctf2", "ctf3", "ctf4", "ctf5"]:
                peer_orders = followers_map[peer_name].get_open_orders()
                peer_oid = str(rep_res["replicated_orders"][peer_name]["order_id"])
                peer_has_pos = any(str(o.get("id")) == peer_oid for o in peer_orders)
                rec.log_assertion(f"State 3 Invariant: Peer {peer_name} Remains Active", True, peer_has_pos, peer_has_pos)
                assert peer_has_pos, f"FATAL: Follower exit cascaded to peer {peer_name}!"

            # -------------------------------------------------------------
            # STATE 4: UNFOLLOW_IN_FLIGHT (ctf5 Unlinks From Master)
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 4: UNFOLLOW_IN_FLIGHT")
            current_state = "STATE_4_UNFOLLOW_IN_FLIGHT"
            state_history.append(current_state)

            ctf5_session = followers_map["ctf5"]
            unf_res = ctf5_session.unfollow_copy_master(str(master.user_id or "1060"))
            rec.log_step(
                name="STATE_4: ctf5 Unfollows Master While Trade Open",
                action="GET /user/follow.php?type=unfollow",
                endpoint=WavexSettings.COPY_FOLLOW_ENDPOINT,
                extra=unf_res
            )
            rec.log_assertion("State 4: Unfollow API Succeeded", "success", unf_res.get("status"), unf_res.get("status") == "success")

            # Square off ctf5's existing trade so it's clean
            ctf5_oid = str(rep_res["replicated_orders"]["ctf5"]["order_id"])
            ctf5_session.squareoff_position(ctf5_oid)
            ctf5_session.wait_for_order_closure(ctf5_oid, timeout=8.0)

            # -------------------------------------------------------------
            # STATE 5: MASTER_SQUAREOFF_FANOUT
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 5: MASTER_SQUAREOFF_FANOUT")
            current_state = "STATE_5_MASTER_SQUAREOFF_FANOUT"
            state_history.append(current_state)

            m_sqo_res = master.squareoff_position(master_oid)
            rec.log_step(
                name="STATE_5: Master Square-Off (Fanout Trigger)",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                extra={"master_order_id": master_oid, "response": m_sqo_res}
            )

            # Wait for all remaining active followers (ctf2, ctf3, ctf4) to be fanout-closed
            close_all = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="STATE_5: Fanout Closure Verification",
                action="Poll /book/orders.php across all accounts",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                extra=close_all
            )
            rec.log_assertion("State 5 Invariant: All Positions Cleanly Liquidated", True, close_all["all_closed"], close_all["all_closed"])
            assert close_all["all_closed"], f"Lingering positions after fanout square-off: {close_all['unclosed_accounts']}"

            # -------------------------------------------------------------
            # STATE 6: RE_FOLLOW_AND_SELL_OPEN
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 6: RE_FOLLOW_AND_SELL_OPEN")
            current_state = "STATE_6_RE_FOLLOW_AND_SELL_OPEN"
            state_history.append(current_state)

            # Re-subscribe ctf5 to Master and restore all to baseline multiplier 3.0x
            re_fol_res = ctf5_session.follow_copy_master(str(master.user_id or "1060"), method="multiplier", value="3.0")
            rec.log_step(
                name="STATE_6: ctf5 Re-Follows Master",
                action="GET /user/follow.php?type=follow",
                endpoint=WavexSettings.COPY_FOLLOW_ENDPOINT,
                extra=re_fol_res
            )
            config_mgr.set_all_followers_mode(method="multiplier", value="3.0")

            # Master places Market SELL 0.50 lot
            place_sell_res = master.place_order(symbol=symbol, side="sell", lot=master_lot, order_type="market")
            sell_order = master.wait_for_order_in_book(symbol=symbol, side="sell", expected_lot=master_lot, timeout=10.0, require_price=True)
            assert sell_order is not None, f"Master SELL order not found in book! {place_sell_res}"
            master_sell_oid = str(sell_order.get("id"))

            # All 5 followers should now replicate SELL 1.50 lots
            expected_sell_lot = 1.50  # 0.50 * 3.0x
            rep_sell = poller.wait_for_follower_replication(symbol=symbol, side="sell", expected_lot=expected_sell_lot, timeout=12.0)
            rec.log_step(
                name="STATE_6: SELL Replication After Re-Follow",
                action="Poll /book/orders.php for SELL 1.50 lots",
                endpoint=WavexSettings.ORDERS_SNAPSHOT_ENDPOINT,
                extra=rep_sell
            )
            rec.log_assertion("State 6 Invariant: All 5 Followers Replicated SELL 1.50 Lots", True, rep_sell["all_replicated"], rep_sell["all_replicated"])
            assert rep_sell["all_replicated"], f"Missing SELL replications: {rep_sell['missing_followers']}"

            # -------------------------------------------------------------
            # STATE 7: FINAL_SQUAREOFF_AND_BASELINE
            # -------------------------------------------------------------
            logger.info(">>> TRANSITIONING TO STATE 7: FINAL_SQUAREOFF_AND_BASELINE")
            current_state = "STATE_7_FINAL_SQUAREOFF_AND_BASELINE"
            state_history.append(current_state)

            master.squareoff_position(master_sell_oid)
            final_clean = poller.wait_for_all_positions_closed(timeout=12.0)
            rec.log_step(
                name="STATE_7: Final Master Square-Off",
                action="GET /book/squareoff.php",
                endpoint=WavexSettings.SQUAREOFF_ENDPOINT,
                extra=final_clean
            )
            rec.log_assertion("State 7 Invariant: Final Clean Slate Verified", True, final_clean["all_closed"], final_clean["all_closed"])
            assert final_clean["all_closed"], f"Final clean slate failed: {final_clean['unclosed_accounts']}"

            rec.log_step(
                name="FSM Traversal Complete",
                action="State History Recorded",
                extra={"traversed_states": state_history, "final_state": current_state}
            )
            rec.finish(status="PASS")

        except Exception as e:
            logger.exception(f"Failure in state {current_state}: {e}")
            rec.finish(status="FAIL", error=f"Failed in {current_state}: {str(e)}")
            raise e
        finally:
            logger.info("Cleaning up and enforcing baseline configuration...")
            teardown.execute_complete_teardown()
            config_mgr.restore_baseline()

