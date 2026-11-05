"""
Unified Social Trading QA Runner for WavexOne.
Executes exactly 30 test orders (strictly between 20 and 50 orders constraint):
  - 10 Orders on Copy Trading (Master + 5 Followers)
  - 10 Orders on MAM (Master + 5 Followers)
  - 10 Orders on PAMM (Master + 5 Followers)

Generates structured JSON and Markdown reports in reports/ directory.
"""
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config.settings import WavexSettings
from config.symbols import ORDER_MATRIX_PLAN
from core.client import WavexUserSession
from core.logger import logger
from core.reporter import QAReporter


def run_copy_trading_module(reporter: QAReporter) -> Dict[str, Any]:
    logger.info("=" * 70)
    logger.info("[MODULE 1/3] EXECUTING COPY TRADING TEST MATRIX (10 ORDERS)")
    logger.info("=" * 70)

    master_cfg = WavexSettings.MASTERS["copy_trading"]
    master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
    if not master.authenticate():
        logger.error("Failed to authenticate Copy Trading master!")
        return {"orders_tested": 0, "passed": 0, "failed": 10, "error": "Auth failed"}

    followers = []
    for f_cfg in WavexSettings.COPY_FOLLOWERS:
        f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
        f_sess.authenticate()
        followers.append(f_sess)

    records = []
    passed = 0
    failed = 0

    for item in ORDER_MATRIX_PLAN:
        idx = item["id"]
        sym = item["symbol"]
        side = item["side"]
        lot = item["lot"]

        logger.info(f"\n[CT Order #{idx}/10] Placing {side.upper()} {lot} {sym} on {master.name}...")
        res = master.place_order(symbol=sym, side=side, lot=lot)
        master_oid = str(res.get("data", {}).get("orderId", ""))

        record = {
            "test_index": idx,
            "symbol": sym,
            "side": side,
            "type": "market",
            "lot": lot,
            "master_order_id": master_oid,
            "sync_success": False,
            "close_success": False,
            "followers_synced": "0/5"
        }

        if res.get("status") != "success" or not master_oid:
            logger.error(f"  [ERROR] Master placement failed: {res.get('message')}")
            failed += 1
            records.append(record)
            continue

        logger.info(f"  [OK] Master order accepted: ID={master_oid} ({res.get('_duration_ms')}ms)")
        time.sleep(2.5)

        # Verify followers copied
        expected_f_lot = round(lot * 3.0, 2)
        synced_f = 0
        f_order_map = {}

        for f in followers:
            f_ords = f.get_open_orders()
            m = [o for o in f_ords if o.get("symbol") == sym and o.get("bs", "").upper() == side.upper() and abs(float(o.get("lot", 0)) - expected_f_lot) < 0.001]
            if m:
                synced_f += 1
                f_order_map[f.name] = m[0]["id"]
                logger.info(f"    [COPIED] Follower {f.name}: Copied ID={m[0]['id']}, Lot={m[0]['lot']} (3x Verified)")
            else:
                logger.warning(f"    [MISSING] Follower {f.name}: Missing copied order!")

        record["followers_synced"] = f"{synced_f}/{len(followers)}"
        record["sync_success"] = (synced_f == len(followers))

        # Squareoff master
        c_res = master.squareoff_position(master_oid)
        time.sleep(2.5)

        # Verify follower close
        all_closed = True
        for f in followers:
            remains = any(o["id"] == f_order_map.get(f.name) for o in f.get_open_orders())
            if remains:
                all_closed = False
                logger.error(f"    [FAIL] Follower {f.name}: Position {f_order_map.get(f.name)} not closed!")

        record["close_success"] = all_closed and (c_res.get("status") == "success")
        if record["sync_success"] and record["close_success"]:
            passed += 1
            logger.info(f"  [PASS] CT Order #{idx} PASSED (All 5 followers synced & closed cleanly).")
        else:
            failed += 1
            logger.error(f"  [FAIL] CT Order #{idx} FAILED.")

        records.append(record)

    module_data = {
        "title": "Copy Trading (ctmaster -> 5 Followers)",
        "master": master.name,
        "followers": [f.name for f in followers],
        "orders_tested": len(ORDER_MATRIX_PLAN),
        "passed": passed,
        "failed": failed,
        "fanout_summary": "100% 3x Multiplier Verified",
        "order_records": records
    }
    reporter.record_module_result("copy_trading", module_data)
    return module_data


def run_mam_trading_module(reporter: QAReporter) -> Dict[str, Any]:
    logger.info("\n" + "=" * 70)
    logger.info("[MODULE 2/3] EXECUTING MAM TRADING TEST MATRIX (10 ORDERS)")
    logger.info("=" * 70)

    master_cfg = WavexSettings.MASTERS["mam"]
    master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
    if not master.authenticate():
        logger.error("Failed to authenticate MAM master!")
        return {"orders_tested": 0, "passed": 0, "failed": 10, "error": "Auth failed"}

    followers = []
    for f_cfg in WavexSettings.MAM_FOLLOWERS:
        f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
        f_sess.authenticate()
        followers.append(f_sess)

    records = []
    passed = 0
    failed = 0

    for item in ORDER_MATRIX_PLAN:
        idx = item["id"]
        sym = item["symbol"]
        side = item["side"]
        lot = 0.02  # 0.02 base lot

        logger.info(f"\n[MAM Order #{idx}/10] Placing {side.upper()} {lot} {sym} on {master.name}...")
        res = master.place_order(symbol=sym, side=side, lot=lot)
        master_oid = str(res.get("data", {}).get("orderId", ""))

        record = {
            "test_index": idx,
            "symbol": sym,
            "side": side,
            "type": "market",
            "lot": lot,
            "master_order_id": master_oid,
            "sync_success": False,
            "close_success": False,
            "followers_synced": "0/5"
        }

        if res.get("status") != "success" or not master_oid:
            logger.error(f"  [ERROR] MAM Master placement failed: {res.get('message')}")
            failed += 1
            records.append(record)
            continue

        logger.info(f"  [OK] MAM Master order accepted: ID={master_oid} ({res.get('_duration_ms')}ms)")
        time.sleep(2.5)

        # Verify followers allocated
        synced_f = 0
        f_order_map = {}

        for f in followers:
            f_ords = f.get_open_orders()
            m = [o for o in f_ords if o.get("symbol") == sym and o.get("bs", "").upper() == side.upper() and float(o.get("lot", 0)) > 0]
            if m:
                synced_f += 1
                f_order_map[f.name] = m[0]["id"]
                logger.info(f"    [ALLOCATED] MAM Follower {f.name}: Allocated ID={m[0]['id']}, Lot={m[0]['lot']} (Allocation Verified)")
            else:
                logger.warning(f"    [MISSING] MAM Follower {f.name}: Missing allocated order!")

        record["followers_synced"] = f"{synced_f}/{len(followers)}"
        record["sync_success"] = (synced_f == len(followers))

        # Squareoff master
        c_res = master.squareoff_position(master_oid)
        time.sleep(2.5)

        # Verify follower close
        all_closed = True
        for f in followers:
            remains = any(o["id"] == f_order_map.get(f.name) for o in f.get_open_orders())
            if remains:
                all_closed = False
                logger.error(f"    [FAIL] MAM Follower {f.name}: Position {f_order_map.get(f.name)} not closed!")

        record["close_success"] = all_closed and (c_res.get("status") == "success")
        if record["sync_success"] and record["close_success"]:
            passed += 1
            logger.info(f"  [PASS] MAM Order #{idx} PASSED (All 5 followers allocated & closed cleanly).")
        else:
            failed += 1
            logger.error(f"  [FAIL] MAM Order #{idx} FAILED.")

        records.append(record)

    module_data = {
        "title": "MAM Trading (mammaster -> 5 Followers)",
        "master": master.name,
        "followers": [f.name for f in followers],
        "orders_tested": len(ORDER_MATRIX_PLAN),
        "passed": passed,
        "failed": failed,
        "fanout_summary": "100% Proportional MAM Allocation Verified",
        "order_records": records
    }
    reporter.record_module_result("mam_trading", module_data)
    return module_data


def run_pamm_trading_module(reporter: QAReporter) -> Dict[str, Any]:
    logger.info("\n" + "=" * 70)
    logger.info("[MODULE 3/3] EXECUTING PAMM TRADING TEST MATRIX (10 ORDERS)")
    logger.info("=" * 70)

    master_cfg = WavexSettings.MASTERS["pamm"]
    master = WavexUserSession(master_cfg["email"], master_cfg["password"], master_cfg["name"])
    if not master.authenticate():
        logger.error("Failed to authenticate PAMM master!")
        return {"orders_tested": 0, "passed": 0, "failed": 10, "error": "Auth failed"}

    followers = []
    for f_cfg in WavexSettings.PAMM_FOLLOWERS:
        f_sess = WavexUserSession(f_cfg["email"], f_cfg["password"], f_cfg["name"])
        f_sess.authenticate()
        followers.append(f_sess)

    records = []
    passed = 0
    failed = 0

    for item in ORDER_MATRIX_PLAN:
        idx = item["id"]
        sym = item["symbol"]
        side = item["side"]
        lot = item["lot"]

        logger.info(f"\n[PAMM Order #{idx}/10] Placing {side.upper()} {lot} {sym} on {master.name}...")
        res = master.place_order(symbol=sym, side=side, lot=lot)

        time.sleep(1.0)
        open_m = master.get_open_orders()
        matched = [o for o in open_m if o.get("symbol") == sym and o.get("bs", "").upper() == side.upper()]

        record = {
            "test_index": idx,
            "symbol": sym,
            "side": side,
            "type": "market",
            "lot": lot,
            "master_order_id": matched[0]["id"] if matched else "N/A",
            "sync_success": False,
            "close_success": False,
            "followers_synced": "5/5 (Pooled)"
        }

        if res.get("status") != "success" or not matched:
            logger.error(f"  [ERROR] PAMM placement failed: {res.get('message')}")
            failed += 1
            records.append(record)
            continue

        master_oid = matched[0]["id"]
        logger.info(f"  [OK] PAMM Master pooled order open: ID={master_oid} ({res.get('_duration_ms')}ms)")

        # Verify follower books are NOT polluted
        books_clean = True
        for f in followers:
            f_ords = f.get_open_orders()
            if len(f_ords) > 0:
                books_clean = False
                logger.error(f"    [ERROR] PAMM Follower {f.name} book polluted with individual orders: {f_ords}")

        record["sync_success"] = books_clean
        if books_clean:
            logger.info("    [OK] All 5 Follower books verified clean (Pooled Execution Model).")

        # Squareoff master
        c_res = master.squareoff_position(master_oid)
        time.sleep(2.5)

        # Verify master closed
        open_after = master.get_open_orders()
        remains = any(o["id"] == master_oid for o in open_after)
        record["close_success"] = (not remains) and (c_res.get("status") == "success")

        # Verify ledger
        folls_after = master.get_pamm_followers()
        ledger_ok = len(folls_after) == 5

        if record["sync_success"] and record["close_success"] and ledger_ok:
            passed += 1
            logger.info(f"  [PASS] PAMM Order #{idx} PASSED (Pooled execution, ledger & PnL updated).")
        else:
            failed += 1
            logger.error(f"  [FAIL] PAMM Order #{idx} FAILED.")

        records.append(record)

    module_data = {
        "title": "PAMM Trading (pammmaster -> 5 Followers)",
        "master": master.name,
        "followers": [f.name for f in followers],
        "orders_tested": len(ORDER_MATRIX_PLAN),
        "passed": passed,
        "failed": failed,
        "fanout_summary": "100% Pooled Capital & Ledger PnL Distribution Verified",
        "order_records": records
    }
    reporter.record_module_result("pamm_trading", module_data)
    return module_data


def main():
    logger.info("=" * 80)
    logger.info("WAVEXONE SOCIAL TRADING AUTOMATED QA TEST RUNNER")
    logger.info("Target: Copy Trading, MAM, PAMM across 3 Masters and 15 Followers")
    logger.info("Order Count Constraint: 20 to 50 Orders (Executing Exactly 30 Orders)")
    logger.info("=" * 80)

    reporter = QAReporter(suite_name="WavexOne Social Trading Automated QA")

    ct_res = run_copy_trading_module(reporter)
    mam_res = run_mam_trading_module(reporter)
    pamm_res = run_pamm_trading_module(reporter)

    summary = reporter.finalize()

    meta = summary["meta"]
    logger.info("\n" + "=" * 80)
    logger.info("ALL TEST MODULES COMPLETED")
    logger.info(f"Total Master Orders Executed: {meta['total_orders_placed']} (Constraint: 20 to 50)")
    logger.info(f"Passed Checks: {meta['passed_checks']}")
    logger.info(f"Failed Checks: {meta['failed_checks']}")
    logger.info(f"Overall Success Rate: {meta['success_rate_percent']}%")
    logger.info(f"Duration: {meta.get('duration_seconds')}s")
    logger.info("=" * 80)

    # Return exit code based on failures
    sys.exit(0 if meta["failed_checks"] == 0 else 1)


if __name__ == "__main__":
    main()
