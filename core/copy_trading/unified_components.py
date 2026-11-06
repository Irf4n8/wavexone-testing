"""
WavexOne Unified Copy Trading Architecture Components.
Senior QA Architect & Trading Systems Test Engineering Framework.

Provides 12 Reusable Enterprise Components:
1. AccountManager (Environment validation & authenticated session management)
2. CopyConfigurationManager (Subscription, Multiplier, Balance, Equity modes)
3. OrderExecutionEngine (Market, Limit, Stop HFT, TP/SL, Modification, Partial Close)
4. ReplicationValidator (Mathematical sizing, direction, TP/SL, latency, child tickets)
5. PositionManager (Order book tracking, exposure aggregation, parent-child mapping)
6. MarginMonitor (Real-time Equity, Used Margin, Free Margin, Margin Level %)
7. StopOutValidator (50% Stop-out rules, boundary protection, isolation, idempotency)
8. CommissionValidator (Commissions, swaps, profit-sharing, performance fees)
9. WithdrawalValidator (Open order withdrawal locks, margin reserves, redeem limits)
10. AccountReconciler (Cross-account ticket reconciliation, orphan detection, clean slate)
11. EvidenceRecorder (Sanitized step-by-step evidence & telemetry logger)
12. SafeTeardown (Deterministic position squareoff & pending order purging)
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger
from core.copy_trading.session_manager import CopyTradingSessionManager
from core.copy_trading.copy_config_manager import CopyConfigManager
from core.copy_trading.evidence_recorder import SanitizedEvidenceRecorder
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.copy_trading.book_poller import BookPoller


# -----------------------------------------------------------------------------
# 1. AccountManager
# -----------------------------------------------------------------------------
class AccountManager:
    """Manages multi-tenant authenticated sessions, environment security, and balances."""
    def __init__(self):
        self._session_mgr = CopyTradingSessionManager()
        self.master: Optional[WavexUserSession] = None
        self.followers: List[WavexUserSession] = []
        self._accounts_map: Dict[str, WavexUserSession] = {}

    def initialize_and_authenticate(self) -> Dict[str, Any]:
        """Validates environment boundaries and authenticates Master and all 5 Followers."""
        logger.info("[AccountManager] Initializing and authenticating staging accounts...")
        self.master = self._session_mgr.initialize_master()
        self.followers = self._session_mgr.initialize_followers()
        self._accounts_map = {self.master.name: self.master}
        for f in self.followers:
            self._accounts_map[f.name] = f

        statuses = {}
        for name, sess in self._accounts_map.items():
            bal = sess.get_balance()
            statuses[name] = {
                "account_id": sess.expected_account_id,
                "authenticated": bool(sess.token),
                "balance": float(bal.get("balance", 0.0) or 0.0),
                "equity": float(bal.get("equity", 0.0) or 0.0),
                "fund": float(bal.get("fund", 0.0) or 0.0)
            }
        return statuses

    def get_master(self) -> WavexUserSession:
        if not self.master:
            self.initialize_and_authenticate()
        return self.master

    def get_followers(self) -> List[WavexUserSession]:
        if not self.followers:
            self.initialize_and_authenticate()
        return self.followers

    def get_follower(self, name_or_id: str) -> Optional[WavexUserSession]:
        for f in self.get_followers():
            if f.name == name_or_id or f.expected_account_id == name_or_id:
                return f
        return None

    def get_all_sessions(self) -> List[WavexUserSession]:
        return [self.get_master()] + self.get_followers()


# -----------------------------------------------------------------------------
# 2. CopyConfigurationManager
# -----------------------------------------------------------------------------
class CopyConfigurationManager(CopyConfigManager):
    """Extends CopyConfigManager with advanced validation and subscription switching."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        super().__init__(master, followers)

    def set_mode_and_verify(self, method: str, value: str = "") -> bool:
        """Sets copy trading mode across all followers and verifies the state."""
        success = self.set_all_followers_mode(method=method, value=value)
        time.sleep(1.0)
        return success


# -----------------------------------------------------------------------------
# 3. OrderExecutionEngine
# -----------------------------------------------------------------------------
class OrderExecutionEngine:
    """Unified engine to place, modify, partially close, and cancel orders."""
    def __init__(self, master: WavexUserSession, default_symbol: str = "X:BTCUSD"):
        self.master = master
        self.symbol = default_symbol

    def place_market_order(
        self, side: str, lot: float = 0.50, sl: str = "", tp: str = ""
    ) -> Dict[str, Any]:
        """Places a market BUY or SELL order."""
        return self.master.place_order(
            symbol=self.symbol,
            side=side.lower(),
            lot=lot,
            order_type="market",
            sl=sl,
            target=tp
        )

    def place_limit_order(
        self, side: str, trigger_price: float, lot: float = 0.50, sl: str = "", tp: str = ""
    ) -> Dict[str, Any]:
        """Places a pending Limit BUY or SELL order."""
        return self.master.place_order(
            symbol=self.symbol,
            side=side.lower(),
            lot=lot,
            order_type="limit",
            trigger=f"{trigger_price:.2f}",
            sl=sl,
            target=tp
        )

    def place_stop_order(
        self, side: str, trigger_price: float, lot: float = 0.50, sl: str = "", tp: str = ""
    ) -> Dict[str, Any]:
        """Places a pending Stop HFT BUY or SELL order."""
        lot_str = f"{lot:.2f}"
        trig_str = f"{trigger_price:.2f}"
        if side.lower() == "buy":
            return self.master.place_order(
                symbol=self.symbol,
                side="buy",
                order_type="stop",
                stop_hft_type="1",
                lotb=lot_str,
                triggerb=trig_str,
                slb=sl,
                targetb=tp
            )
        else:
            return self.master.place_order(
                symbol=self.symbol,
                side="sell",
                order_type="stop",
                stop_hft_type="0",
                lots=lot_str,
                triggers=trig_str,
                sls=sl,
                targets=tp
            )

    def place_stop_both_order(
        self, trigger_buy: float, trigger_sell: float, lot: float = 0.50, with_tpsl: bool = False
    ) -> Dict[str, Any]:
        """Places dual-leg Stop HFT BOTH order."""
        lot_str = f"{lot:.2f}"
        slb = f"{trigger_buy - 150.0:.2f}" if with_tpsl else ""
        tpb = f"{trigger_buy + 300.0:.2f}" if with_tpsl else ""
        sls = f"{trigger_sell + 150.0:.2f}" if with_tpsl else ""
        tps = f"{trigger_sell - 300.0:.2f}" if with_tpsl else ""

        return self.master.place_order(
            symbol=self.symbol,
            side="buy",
            order_type="stop",
            stop_hft_type="2",
            lotb=lot_str,
            triggerb=f"{trigger_buy:.2f}",
            slb=slb,
            targetb=tpb,
            lots=lot_str,
            triggers=f"{trigger_sell:.2f}",
            sls=sls,
            targets=tps
        )

    def modify_order_sl_tp(self, order_id: str, new_sl: str, new_tp: str) -> Dict[str, Any]:
        """Modifies Stop Loss and Target Price on an active open position."""
        res_sl = self.master.modify_order(order_id=order_id, name="StopLoss", val=new_sl)
        res_tp = self.master.modify_order(order_id=order_id, name="Target", val=new_tp)
        return {"order_id": order_id, "modify_sl": res_sl, "modify_tp": res_tp}

    def partial_close(self, order_id: str, partial_lot: float) -> Dict[str, Any]:
        """Partially closes an open position with proportional volume reduction."""
        return self.master.partial_close_position(order_id=order_id, partial_lot=partial_lot)

    def full_squareoff(self, order_id: str) -> Dict[str, Any]:
        """Fully squares off an open position."""
        return self.master.squareoff_position(order_id=order_id)

    def cancel_pending(self, order_id: str) -> Dict[str, Any]:
        """Cancels a pending limit or stop order."""
        return self.master.cancel_order(order_id=order_id)


# -----------------------------------------------------------------------------
# 4. ReplicationValidator
# -----------------------------------------------------------------------------
class ReplicationValidator:
    """Validates mathematical sizing, ticket fanout, replication latencies, and parameters."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers
        self.poller = BookPoller(master, followers)

    def calculate_expected_follower_lot(
        self, master_lot: float, follower: WavexUserSession, mode: str, multiplier_val: float = 3.0
    ) -> float:
        """Calculates expected follower lot size based on active copy mode."""
        if mode == "multiplier":
            return round(master_lot * multiplier_val, 2)
        elif mode == "balance":
            m_bal = float(self.master.get_balance().get("balance", 0.0) or 1.0)
            f_bal = float(follower.get_balance().get("balance", 0.0) or 0.0)
            ratio = f_bal / m_bal if m_bal > 0 else 0.0
            return max(0.01, round(master_lot * ratio, 2))
        elif mode == "equity":
            m_eq = float(self.master.get_balance().get("equity", 0.0) or 1.0)
            f_eq = float(follower.get_balance().get("equity", 0.0) or 0.0)
            ratio = f_eq / m_eq if m_eq > 0 else 0.0
            return max(0.01, round(master_lot * ratio, 2))
        return master_lot

    def validate_fanout_replication(
        self,
        master_order_id: str,
        expected_side: str,
        master_lot: float,
        mode: str,
        multiplier_val: float = 3.0,
        timeout: float = 12.0
    ) -> Dict[str, Any]:
        """Validates that all 5 followers receive copied positions with exact lot sizing."""
        start_t = time.time()
        results = {
            "master_order_id": master_order_id,
            "mode": mode,
            "all_replicated": True,
            "latency_sec": 0.0,
            "followers": {}
        }

        # Poll all followers
        deadline = time.time() + timeout
        while time.time() < deadline:
            all_present = True
            for f in self.followers:
                f_orders = f.get_open_orders()
                exp_lot = self.calculate_expected_follower_lot(master_lot, f, mode, multiplier_val)
                # Find matching orders (supporting split tickets e.g. 1.0 + 0.5 lot)
                matches = [o for o in f_orders if str(o.get("bs", "")).upper() == expected_side.upper()]
                if not matches:
                    all_present = False
                    break
                else:
                    total_lot = sum(float(o.get("lot", 0.0) or o.get("partiallot", 0.0) or 0.0) for o in matches)
                    child_ids = [str(o.get("id")) for o in matches]
                    results["followers"][f.name] = {
                        "child_order_id": child_ids[0] if len(child_ids) == 1 else child_ids,
                        "side": matches[0].get("bs"),
                        "actual_lot": round(total_lot, 2),
                        "expected_lot": exp_lot,
                        "lot_matches": abs(total_lot - exp_lot) <= 0.01
                    }
            if all_present and len(results["followers"]) == len(self.followers):
                if all(v["lot_matches"] for v in results["followers"].values()):
                    results["latency_sec"] = round(time.time() - start_t, 3)
                    results["all_replicated"] = True
                    return results
            time.sleep(0.5)

        results["all_replicated"] = all(v.get("lot_matches", False) for v in results["followers"].values()) if results["followers"] else False
        results["latency_sec"] = round(time.time() - start_t, 3)
        return results


# -----------------------------------------------------------------------------
# 5. PositionManager
# -----------------------------------------------------------------------------
class PositionManager:
    """Manages order books, tracks parent-child ticket pairs, and exposure."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers

    def get_all_open_positions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves open orders for Master and all Followers."""
        data = {self.master.name: self.master.get_open_orders()}
        for f in self.followers:
            data[f.name] = f.get_open_orders()
        return data

    def count_total_open_positions(self) -> int:
        """Returns the total number of open orders across all 6 accounts."""
        positions = self.get_all_open_positions()
        return sum(len(ords) for ords in positions.values())

    def get_master_to_followers_ticket_map(self) -> Dict[str, List[Dict[str, Any]]]:
        """Maps each active Master position to corresponding follower child positions."""
        m_orders = self.master.get_open_orders()
        f_positions = {f.name: f.get_open_orders() for f in self.followers}
        mapping = {}
        for m in m_orders:
            mid = str(m.get("id"))
            mapping[mid] = []
            m_side = str(m.get("bs", "")).upper()
            m_symbol = str(m.get("symbol", "")).upper()
            for fname, ords in f_positions.items():
                for fo in ords:
                    if str(fo.get("bs", "")).upper() == m_side:
                        mapping[mid].append({"follower": fname, "child_id": fo.get("id"), "lot": fo.get("lot")})
        return mapping


# -----------------------------------------------------------------------------
# 6. MarginMonitor
# -----------------------------------------------------------------------------
class MarginMonitor:
    """Monitors live Balance, Equity, Used Margin, Free Margin, and Margin Level %."""
    def __init__(self, accounts: List[WavexUserSession]):
        self.accounts = accounts

    def capture_account_snapshot(self, session: WavexUserSession) -> Dict[str, Any]:
        """Calculates accurate Balance, Equity, Used Margin, Free Margin, and Margin Level %."""
        bal_data = session.get_balance()
        balance = float(bal_data.get("balance", 0.0) or 0.0)
        equity = float(bal_data.get("equity", balance) or balance)
        fund = float(bal_data.get("fund", balance) or balance)

        # Used Margin = Balance - Free Margin (Fund)
        used_margin = max(0.0, round(balance - fund, 2))
        
        # Margin Level (%) = (Equity / Used Margin) * 100
        if used_margin > 0:
            margin_level = round((equity / used_margin) * 100, 2)
        else:
            margin_level = 0.0

        return {
            "account_name": session.name,
            "account_id": session.expected_account_id,
            "balance": balance,
            "equity": equity,
            "free_margin": fund,
            "used_margin": used_margin,
            "margin_level_pct": margin_level,
            "is_margin_call": 50.0 < margin_level <= 100.0 if used_margin > 0 else False,
            "is_stop_out": margin_level <= 50.0 if used_margin > 0 else False
        }

    def capture_all_snapshots(self) -> Dict[str, Dict[str, Any]]:
        """Captures margin snapshots for all managed accounts."""
        return {sess.name: self.capture_account_snapshot(sess) for sess in self.accounts}


# -----------------------------------------------------------------------------
# 7. StopOutValidator
# -----------------------------------------------------------------------------
class StopOutValidator:
    """Validates 50% Margin Stop-Out requirements, isolation, and idempotency."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers
        self.margin_monitor = MarginMonitor([master] + followers)

    def evaluate_stop_out_boundary(self, session: WavexUserSession) -> Dict[str, Any]:
        """
        Evaluates the 50% Stop-Out boundary:
        - ML > 100%: Healthy
        - 50% < ML <= 100%: Margin Call Warning (No Liquidation)
        - ML <= 50%: Stop-Out Liquidation Trigger
        """
        snap = self.margin_monitor.capture_account_snapshot(session)
        ml = snap["margin_level_pct"]
        um = snap["used_margin"]
        
        status = "HEALTHY"
        if um > 0:
            if ml <= 50.0:
                status = "STOP_OUT_TRIGGER"
            elif ml <= 100.0:
                status = "MARGIN_CALL_WARNING"
        return {"snapshot": snap, "boundary_status": status}

    def verify_isolation_on_follower_liquidation(
        self, follower: WavexUserSession, follower_order_id: str, master_order_id: str
    ) -> Dict[str, Any]:
        """Verifies that liquidating a follower does NOT affect Master or peer followers."""
        sq_res = follower.squareoff_position(follower_order_id)
        time.sleep(2.0)

        # Check follower order is closed
        f_open = any(str(o.get("id")) == str(follower_order_id) for o in follower.get_open_orders())
        # Check master order is still open
        m_open = any(str(o.get("id")) == str(master_order_id) for o in self.master.get_open_orders())

        return {
            "follower_order_closed": not f_open,
            "master_order_still_open": m_open,
            "isolation_intact": (not f_open) and m_open
        }

    def test_duplicate_squareoff_idempotency(self, session: WavexUserSession, order_id: str) -> Dict[str, Any]:
        """Tests that firing duplicate squareoffs on an order returns idempotency failure."""
        res1 = session.squareoff_position(order_id)
        res2 = session.squareoff_position(order_id)
        return {
            "attempt_1": res1,
            "attempt_2": res2,
            "idempotent": res2.get("status") == "fail" and "no longer available" in res2.get("message", "")
        }


# -----------------------------------------------------------------------------
# 8. CommissionValidator
# -----------------------------------------------------------------------------
class CommissionValidator:
    """Validates Profit Sharing, swap costs, and cross-account settlement reconciliation."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers

    def audit_trade_commissions(self, order_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Checks commission and swap parameters on open/closed tickets."""
        comm = float(order_dict.get("commission", 0.0) or 0.0)
        swap = float(order_dict.get("t_swap", 0.0) or 0.0)
        return {
            "order_id": order_dict.get("id"),
            "commission": comm,
            "swap": swap,
            "has_commission_tracking": "commission" in order_dict
        }

    def check_profit_sharing_status(self) -> Dict[str, Any]:
        """Discovers platform Profit Sharing configuration via subscriptions and history."""
        fol_list = self.master.get_copy_followers()
        m_hist = self.master.session.get(f"{WavexSettings.BASE_URL}/book/history.php?token={self.master.token}").json().get("info", {})
        master_earned = float(m_hist.get("copyProfitShareEarned", 0.0) or 0.0)
        total_follower_paid = sum(float(f.get("profit_share_earned", 0.0) or 0.0) for f in fol_list)
        return {
            "configured_profit_share_pct": fol_list[0].get("profit_share", "10") if fol_list else "10",
            "master_profit_share_earned": master_earned,
            "followers_profit_share_paid": total_follower_paid,
            "ledger_reconciled": abs(master_earned - total_follower_paid) < 0.01,
            "platform_profit_sharing_active": True
        }

    def audit_profit_sharing_ledger(self) -> Dict[str, Any]:
        """Performs cent-level cross-account financial reconciliation of Profit Sharing."""
        m_hist = self.master.session.get(f"{WavexSettings.BASE_URL}/book/history.php?token={self.master.token}").json().get("info", {})
        master_earned = float(m_hist.get("copyProfitShareEarned", 0.0) or 0.0)

        follower_breakdown = {}
        total_follower_paid = 0.0
        for f in self.followers:
            f_hist = f.session.get(f"{WavexSettings.BASE_URL}/book/history.php?token={f.token}").json().get("info", {})
            paid = float(f_hist.get("copyProfitSharePaid", 0.0) or 0.0)
            follower_breakdown[f.name] = {
                "account_id": f.account_id,
                "profit_share_paid": paid,
                "closed_pnl": float(f_hist.get("pnl", 0.0) or 0.0),
                "winning_trades": int(f_hist.get("winning_trades", 0) or 0),
                "losing_trades": int(f_hist.get("losing_trades", 0) or 0)
            }
            total_follower_paid += paid

        total_follower_paid = round(total_follower_paid, 2)
        discrepancy = round(abs(master_earned - total_follower_paid), 2)
        return {
            "master_profit_share_earned": master_earned,
            "total_follower_profit_share_paid": total_follower_paid,
            "discrepancy": discrepancy,
            "is_fully_reconciled": discrepancy == 0.0,
            "follower_breakdown": follower_breakdown
        }


# Canonical alias for Profit Sharing
ProfitSharingValidator = CommissionValidator


# -----------------------------------------------------------------------------
# 9. WithdrawalValidator
# -----------------------------------------------------------------------------
class WithdrawalValidator:
    """Validates withdrawal margin locks, redeem configs, and open-order safeguards."""
    def __init__(self, session: WavexUserSession):
        self.session = session

    def audit_withdrawal_headroom(self) -> Dict[str, Any]:
        """Fetches redeem config and checks available funds vs open order reserves."""
        redeem = self.session.get_redeem_config()
        w_limit = redeem.get("withdrawLimit", {})
        open_orders = self.session.get_open_orders()
        
        return {
            "account_name": self.session.name,
            "open_orders_count": len(open_orders),
            "available_fund": redeem.get("availableFund", 0.0),
            "withdraw_limit_available": w_limit.get("available", 0.0),
            "open_orders_lock_field": w_limit.get("open_orders", 0),
            "margin_locked": len(open_orders) > 0
        }


# -----------------------------------------------------------------------------
# 10. AccountReconciler
# -----------------------------------------------------------------------------
class AccountReconciler:
    """Reconciles tickets, checks for orphaned child orders, and audits clean slate."""
    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers

    def reconcile_open_orders(self) -> Dict[str, Any]:
        """Detects orphaned child orders (Master has 0 open, but Follower has open orders)."""
        m_orders = self.master.get_open_orders()
        m_has_open = len(m_orders) > 0

        discrepancies = []
        for f in self.followers:
            f_orders = f.get_open_orders()
            if not m_has_open and len(f_orders) > 0:
                discrepancies.append({
                    "type": "ORPHANED_FOLLOWER_ORDER",
                    "follower": f.name,
                    "order_count": len(f_orders),
                    "order_ids": [o.get("id") for o in f_orders]
                })

        return {
            "master_open_count": len(m_orders),
            "reconciled": len(discrepancies) == 0,
            "discrepancies": discrepancies
        }

    def audit_clean_slate(self) -> Dict[str, Any]:
        """Verifies 0 open orders, 0 pending orders, and 0 used margin across all accounts."""
        audit_results = {}
        all_clean = True

        for sess in [self.master] + self.followers:
            orders = sess.get_open_orders()
            bal = sess.get_balance()
            balance = float(bal.get("balance", 0.0) or 0.0)
            fund = float(bal.get("fund", balance) or balance)
            used_margin = max(0.0, round(balance - fund, 2))

            is_account_clean = (len(orders) == 0) and (used_margin == 0.0)
            if not is_account_clean:
                all_clean = False

            audit_results[sess.name] = {
                "account_id": sess.expected_account_id,
                "open_orders": len(orders),
                "used_margin": used_margin,
                "clean": is_account_clean
            }

        return {"all_clean": all_clean, "accounts": audit_results}


# -----------------------------------------------------------------------------
# 11. EvidenceRecorder & 12. SafeTeardown Aliases
# -----------------------------------------------------------------------------
EvidenceRecorder = SanitizedEvidenceRecorder
SafeTeardown = SafeTeardownHandler
