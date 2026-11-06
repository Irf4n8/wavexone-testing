"""
Master CLI Runner for WavexOne Copy Trading All Modes & All Order Types.
Sequential Execution Order:
  Phase 1: Multiplier Mode (3.0x Multiplier -> 1.50 Lots)
  Phase 2: Balance-Based Mode (Dynamic Ratio -> ~0.05 Lots)
  Phase 3: Equity-Based Mode (Dynamic Ratio -> ~0.05 Lots)
"""
import sys
import subprocess
import time


def main():
    print("================================================================================")
    print("   WAVEXONE COPY TRADING: COMPLETE MULTI-MODE & ALL ORDER TYPES TEST SUITE")
    print("================================================================================")
    print("Sequence:")
    print("  1. MULTIPLIER MODE (14 Scenarios: Market, Limit, Stop HFT w/ and w/o TP/SL)")
    print("  2. BALANCE-BASED MODE (14 Scenarios: Market, Limit, Stop HFT w/ and w/o TP/SL)")
    print("  3. EQUITY-BASED MODE (14 Scenarios: Market, Limit, Stop HFT w/ and w/o TP/SL)")
    print("Master Sizing: 0.50 Lot Strictly | Automatic Clean Slate Teardown Enforced")
    print("================================================================================\n")

    cmd = [sys.executable, "-m", "pytest", "tests/test_all_order_types_copy_trading.py", "-v", "-s"]
    t0 = time.time()
    res = subprocess.run(cmd)
    dur = round(time.time() - t0, 2)

    print("\n" + "=" * 80)
    print(f"RUN FINISHED IN {dur}s WITH EXIT CODE: {res.returncode}")
    print("=" * 80)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()

