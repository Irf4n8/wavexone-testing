"""
Live Flow Diagnostic: Balance Mode & Equity Mode Copy Trading
Exclusively tests Balance-Based and Equity-Based Copy Trading across:
Master (11060) and All 5 Followers (11041, 11043, 11045, 11048, 11050).
"""

import sys
sys.path.insert(0, ".")
import time
import json
from datetime import datetime
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger


def extract_order_id(resp):
    if not isinstance(resp, dict):
        return ""
    d = resp.get("data", {})
    if isinstance(d, dict):
        return str(d.get("orderId", ""))
    elif isinstance(d, list) and len(d) > 0:
        if isinstance(d[0], dict):
            return str(d[0].get("orderId", "") or d[0].get("id", ""))
        return str(d[0])
    return str(resp.get("orderId", ""))


def run_balance_and_equity_audit():
    print("=" * 85)
    print("STARTING DEDICATED BALANCE-BASED & EQUITY-BASED COPY TRADING LIVE FLOW AUDIT")
    print(f"Timestamp: {datetime.now().isoformat()} | Target: {WavexSettings.BASE_URL}")
    print("=" * 85)

    # 1. Authenticate Sessions
    m_cfg = WavexSettings.MASTERS["copy_trading"]
    master = WavexUserSession(m_cfg["email"], m_cfg["password"], "ctmaster", m_cfg["account_id"])
    assert master.authenticate(), "Master auth failed"

    followers = []
    for f_cfg in WavexSettings.COPY_FOLLOWERS:
        f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"], f_cfg["expected_account_id"])
        assert f_sess.authenticate(), f"Follower {f_cfg['name']} auth failed"
        followers.append(f_sess)

    # Clean pre-check
    for sess in [master] + followers:
        for o in sess.get_open_orders():
            sess.squareoff_position(o["id"])

    # Fetch live balances and equities
    m_bal = master.get_balance()
    m_balance = float(m_bal.get("balance", 0))
    m_equity = float(m_bal.get("equity", 0))

    print(f"\n[MASTER ACCOUNT 11060] Balance: ${m_balance:,.2f} | Equity: ${m_equity:,.2f}")

    follower_metrics = {}
    for f in followers:
        b_info = f.get_balance()
        b = float(b_info.get("balance", 0))
        eq = float(b_info.get("equity", 0))
        bal_ratio = b / m_balance if m_balance > 0 else 0
        exp_bal_lot = round(1.00 * bal_ratio, 2)
        follower_metrics[f.name] = {
            "balance": b,
            "equity": eq,
            "bal_ratio": bal_ratio,
            "exp_bal_lot": exp_bal_lot
        }
        print(f"  -> Follower {f.name} ({f.account_id}): Balance: ${b:,.2f} | Equity: ${eq:,.2f} | Ratio: {bal_ratio:.4f} -> Expected Balance Lot: {exp_bal_lot}")

    # =========================================================================
    # PART 1: BALANCE-BASED COPY TRADING TEST
    # =========================================================================
    print("\n" + "=" * 85)
    print("PART 1: TESTING BALANCE-BASED COPY TRADING ACROSS ALL 5 FOLLOWERS")
    print("=" * 85)

    # Switch all followers to 'balance'
    print("\n[Step 1.1] Switching All 5 Followers to Method: 'balance'...")
    for f in followers:
        res = f.update_copy_trading_method(master_uid="1060", method="balance")
        subs = f.get_copy_following()
        current_method = subs[0].get("trade_method") if subs else "unknown"
        print(f"  -> {f.name}: Update Response = {res.get('status')} | Active Method on Platform = '{current_method}'")

    time.sleep(2.0)

    # Place 1.00 lot on Master
    print("\n[Step 1.2] Master 1060 Placing 1.00 Whole Lot Market BUY...")
    t_order_sent = time.time()
    m_res = master.place_order(symbol="X:BTCUSD", side="buy", lot=1.00)
    m_oid = extract_order_id(m_res)
    print(f"  -> Master Order Placed: ID={m_oid} (1.00 Lot) in {(time.time() - t_order_sent)*1000:.1f}ms")

    # Monitor replication across all 5 followers
    print("\n[Step 1.3] Polling All 5 Followers for Balance-Based Replication (~0.11 Lots)...")
    replicated_bal = {}
    t_start_poll = time.time()
    while time.time() - t_start_poll < 12.0 and len(replicated_bal) < len(followers):
        for f in followers:
            if f.name in replicated_bal:
                continue
            orders = f.get_open_orders()
            match = [o for o in orders if o.get("symbol") == "X:BTCUSD" and o.get("bs", "").upper() == "BUY"]
            if match:
                f_lot = float(match[0].get("lot", 0))
                exp_lot = follower_metrics[f.name]["exp_bal_lot"]
                dur = time.time() - t_order_sent
                replicated_bal[f.name] = match[0]
                is_correct = abs(f_lot - exp_lot) <= 0.01
                print(f"  -> [BALANCE REPLICATION] {f.name}: Order={match[0].get('id')} | Replicated Lot={f_lot} (Expected: {exp_lot}) | Match: {is_correct} | Time: {dur:.2f}s")
        time.sleep(0.4)

    print(f"\n  Balance Replication Summary: {len(replicated_bal)} / {len(followers)} followers replicated.")

    # Square off Master to trigger auto square-off fanout
    print("\n[Step 1.4] Squaring off Master to test Balance Mode Auto Square-off Fanout...")
    if m_oid:
        sq = master.squareoff_position(m_oid)
        master.wait_for_order_closure(m_oid, timeout=8.0)
        time.sleep(2.0)
        for f in followers:
            f_oid = replicated_bal.get(f.name, {}).get("id")
            if f_oid:
                c = f.wait_for_order_closure(f_oid, timeout=8.0)
                print(f"  -> Follower {f.name} Position {f_oid} Auto-Closed via Fanout: {c}")

    time.sleep(3.0)

    # =========================================================================
    # PART 2: EQUITY-BASED COPY TRADING TEST
    # =========================================================================
    print("\n" + "=" * 85)
    print("PART 2: TESTING EQUITY-BASED COPY TRADING ACROSS ALL 5 FOLLOWERS")
    print("=" * 85)

    # Switch all followers to 'equity'
    print("\n[Step 2.1] Switching All 5 Followers to Method: 'equity'...")
    for f in followers:
        res = f.update_copy_trading_method(master_uid="1060", method="equity")
        subs = f.get_copy_following()
        current_method = subs[0].get("trade_method") if subs else "unknown"
        print(f"  -> {f.name}: Update Response = {res.get('status')} | Active Method on Platform = '{current_method}'")

    time.sleep(2.0)

    # Place 1.00 lot on Master under Equity Mode
    print("\n[Step 2.2] Master 1060 Placing 1.00 Whole Lot Market BUY under Equity Mode...")
    t_order_sent = time.time()
    m_res2 = master.place_order(symbol="X:BTCUSD", side="buy", lot=1.00)
    m_oid2 = extract_order_id(m_res2)
    print(f"  -> Master Order Placed: ID={m_oid2} (1.00 Lot) in {(time.time() - t_order_sent)*1000:.1f}ms")

    # Monitor replication across all 5 followers
    print("\n[Step 2.3] Polling All 5 Followers for Equity-Based Replication...")
    replicated_eq = {}
    t_start_poll = time.time()
    while time.time() - t_start_poll < 12.0 and len(replicated_eq) < len(followers):
        for f in followers:
            if f.name in replicated_eq:
                continue
            orders = f.get_open_orders()
            match = [o for o in orders if o.get("symbol") == "X:BTCUSD" and o.get("bs", "").upper() == "BUY"]
            if match:
                f_lot = float(match[0].get("lot", 0))
                dur = time.time() - t_order_sent
                replicated_eq[f.name] = match[0]
                print(f"  -> [EQUITY REPLICATION] {f.name}: Order={match[0].get('id')} | Replicated Lot={f_lot} | Time: {dur:.2f}s")
        time.sleep(0.4)

    print(f"\n  Equity Replication Summary: {len(replicated_eq)} / {len(followers)} followers replicated.")

    # Square off Master
    print("\n[Step 2.4] Squaring off Master to test Equity Mode Auto Square-off Fanout...")
    if m_oid2:
        sq = master.squareoff_position(m_oid2)
        master.wait_for_order_closure(m_oid2, timeout=8.0)
        time.sleep(2.0)
        for f in followers:
            f_oid = replicated_eq.get(f.name, {}).get("id")
            if f_oid:
                c = f.wait_for_order_closure(f_oid, timeout=8.0)
                print(f"  -> Follower {f.name} Position {f_oid} Auto-Closed via Fanout: {c}")

    # =========================================================================
    # PART 3: RESTORE FOLLOWERS TO MULTIPLIER 3.0X
    # =========================================================================
    print("\n" + "=" * 85)
    print("PART 3: TEARDOWN & RESTORING ALL 5 FOLLOWERS TO MULTIPLIER 3.0X")
    print("=" * 85)
    for f in followers:
        f.update_copy_trading_method(master_uid="1060", method="multiplier", value="3.0")
        subs = f.get_copy_following()
        sub = subs[0] if subs else {}
        print(f"  -> Follower {f.name}: Restored to {sub.get('trade_method')} at {sub.get('multiplier_value')}x")

    # Clean check
    for sess in [master] + followers:
        for o in sess.get_open_orders():
            sess.squareoff_position(o["id"])

    print("\n" + "=" * 85)
    print("LIVE AUDIT FOR BALANCE & EQUITY MODES COMPLETE")
    print("=" * 85)


if __name__ == "__main__":
    run_balance_and_equity_audit()
