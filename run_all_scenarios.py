"""
Master Runner for Copy Trading All Scenarios (1 Lot, Easy-to-Hit TP/SL, Auto-Exit Only)
Executes all 21 scenarios across Multiplier, Balance, and Equity modes sequentially,
collects live telemetry, updates reports, and produces a complete final summary.
"""
import time
import json
import pytest
from datetime import datetime
from tests.test_copy_trading_all_scenarios import TestCopyTradingAllScenariosSuite


def main():
    print("=" * 90)
    print("STARTING COMPLETE COPY TRADING AUTOMATION: MULTIPLIER, BALANCE & EQUITY MODES")
    print("All Buying/Selling Scenarios | 1.00 Lot Strictly | Automatic Exit on TP/SL Hit")
    print("=" * 90)

    suite = TestCopyTradingAllScenariosSuite()
    suite.setup_class()

    all_tests = [
        # --- Multiplier Mode (3.0x Multiplier) ---
        ("M-01", "Multiplier Market BUY 1.00 Lot", "multiplier", suite.test_01_mult_market_buy_1lot_auto_exit),
        ("M-02", "Multiplier Market SELL 1.00 Lot", "multiplier", suite.test_02_mult_market_sell_1lot_auto_exit),
        ("M-03", "Multiplier Limit BUY 1.00 Lot", "multiplier", suite.test_03_mult_limit_buy_1lot_auto_exit),
        ("M-04", "Multiplier Limit SELL 1.00 Lot", "multiplier", suite.test_04_mult_limit_sell_1lot_auto_exit),
        ("M-05", "Multiplier Stop HFT BUY 1.00 Lot", "multiplier", suite.test_05_mult_stop_buy_1lot_auto_exit),
        ("M-06", "Multiplier Stop HFT SELL 1.00 Lot", "multiplier", suite.test_06_mult_stop_sell_1lot_auto_exit),
        ("M-07", "Multiplier Stop HFT BOTH 1.00 Lot", "multiplier", suite.test_07_mult_stop_both_1lot_auto_exit),

        # --- Balance Mode (Proportional) ---
        ("B-08", "Balance Market BUY 1.00 Lot", "balance", suite.test_08_bal_market_buy_1lot_auto_exit),
        ("B-09", "Balance Market SELL 1.00 Lot", "balance", suite.test_09_bal_market_sell_1lot_auto_exit),
        ("B-10", "Balance Limit BUY 1.00 Lot", "balance", suite.test_10_bal_limit_buy_1lot_auto_exit),
        ("B-11", "Balance Limit SELL 1.00 Lot", "balance", suite.test_11_bal_limit_sell_1lot_auto_exit),
        ("B-12", "Balance Stop HFT BUY 1.00 Lot", "balance", suite.test_12_bal_stop_buy_1lot_auto_exit),
        ("B-13", "Balance Stop HFT SELL 1.00 Lot", "balance", suite.test_13_bal_stop_sell_1lot_auto_exit),
        ("B-14", "Balance Stop HFT BOTH 1.00 Lot", "balance", suite.test_14_bal_stop_both_1lot_auto_exit),

        # --- Equity Mode (Proportional & Guarded) ---
        ("E-15", "Equity Market BUY 1.00 Lot", "equity", suite.test_15_eq_market_buy_1lot_auto_exit),
        ("E-16", "Equity Market SELL 1.00 Lot", "equity", suite.test_16_eq_market_sell_1lot_auto_exit),
        ("E-17", "Equity Limit BUY 1.00 Lot", "equity", suite.test_17_eq_limit_buy_1lot_auto_exit),
        ("E-18", "Equity Limit SELL 1.00 Lot", "equity", suite.test_18_eq_limit_sell_1lot_auto_exit),
        ("E-19", "Equity Stop HFT BUY 1.00 Lot", "equity", suite.test_19_eq_stop_buy_1lot_auto_exit),
        ("E-20", "Equity Stop HFT SELL 1.00 Lot", "equity", suite.test_20_eq_stop_sell_1lot_auto_exit),
        ("E-21", "Equity Stop HFT BOTH 1.00 Lot", "equity", suite.test_21_eq_stop_both_1lot_auto_exit),

        # --- Dedicated Auto Squareoff Tests ---
        ("AS-22", "Auto Squareoff: TP Hit BUY (All 5 Followers)", "multiplier", suite.test_22_auto_squareoff_take_profit_hit_all_followers),
        ("AS-23", "Auto Squareoff: SL Hit BUY (All 5 Followers)", "multiplier", suite.test_23_auto_squareoff_stop_loss_hit_all_followers),
        ("AS-24", "Auto Squareoff: Master Squareoff Fanout (All 5 Followers)", "multiplier", suite.test_24_master_manual_squareoff_fans_out_auto_squareoff_to_all_followers),
        ("AS-25", "Auto Squareoff: TP Hit SELL (All 5 Followers)", "multiplier", suite.test_25_auto_squareoff_take_profit_hit_sell_all_followers),
        ("AS-26", "Auto Squareoff: SL Hit SELL (All 5 Followers)", "multiplier", suite.test_26_auto_squareoff_stop_loss_hit_sell_all_followers),
        ("AS-27", "Auto Squareoff: Partial Close Proportional Reduction", "multiplier", suite.test_27_partial_auto_squareoff_follower_proportional_reduction),
        ("AS-28", "Auto Squareoff: Batch Concurrent Squareoff (All 5 Followers)", "multiplier", suite.test_28_batch_concurrent_auto_squareoff_all_followers),
    ]

    results = []

    for code, name, mode, test_func in all_tests:
        print(f"\n>>> [{code}] Running {name} (Mode: {mode.upper()})...")
        start_t = time.time()
        status = "UNKNOWN"
        notes = ""
        try:
            test_func()
            status = "PASS"
            dur = round(time.time() - start_t, 2)
            print(f"  [RESULT] {code} - {name}: PASSED in {dur}s (Auto-Exited via TP/SL)")
        except pytest.skip.Exception as e:
            status = "INCONCLUSIVE"
            notes = str(e)
            dur = round(time.time() - start_t, 2)
            print(f"  [RESULT] {code} - {name}: INCONCLUSIVE in {dur}s: {e}")
        except AssertionError as e:
            status = "FAIL"
            notes = str(e)
            dur = round(time.time() - start_t, 2)
            print(f"  [RESULT] {code} - {name}: FAILED in {dur}s: {e}")
        except Exception as e:
            status = "ERROR"
            notes = str(e)
            dur = round(time.time() - start_t, 2)
            print(f"  [RESULT] {code} - {name}: ERROR in {dur}s: {e}")
        finally:
            suite.teardown_method(test_func)
            results.append({
                "code": code,
                "name": name,
                "mode": mode,
                "status": status,
                "duration": round(time.time() - start_t, 2),
                "notes": notes
            })
            time.sleep(2.5)

    suite.teardown_class()

    # Summary calculation
    pass_cnt = sum(1 for r in results if r["status"] == "PASS")
    fail_cnt = sum(1 for r in results if r["status"] == "FAIL")
    incon_cnt = sum(1 for r in results if r["status"] == "INCONCLUSIVE")
    err_cnt = sum(1 for r in results if r["status"] == "ERROR")

    print("\n" + "=" * 90)
    print("FINAL EXECUTION SUMMARY ACROSS ALL 3 MODES (MULTIPLIER, BALANCE, EQUITY)")
    print("=" * 90)
    print(f"TOTAL: {len(results)} | PASS: {pass_cnt} | FAIL: {fail_cnt} | INCONCLUSIVE: {incon_cnt} | ERROR: {err_cnt}")
    print("-" * 90)
    print(f"{'Code':<6} | {'Mode':<10} | {'Status':<14} | {'Duration':<8} | {'Scenario Name'}")
    print("-" * 90)
    for r in results:
        print(f"{r['code']:<6} | {r['mode']:<10} | {r['status']:<14} | {r['duration']:>6.2f}s | {r['name']}")
    print("=" * 90)

    # Save summary json
    summary_path = "reports/copy_trading_all_scenarios_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "pass_count": pass_cnt,
            "fail_count": fail_cnt,
            "inconclusive_count": incon_cnt,
            "error_count": err_cnt,
            "results": results
        }, f, indent=2)
    print(f"Detailed run summary saved to {summary_path}")


if __name__ == "__main__":
    main()
