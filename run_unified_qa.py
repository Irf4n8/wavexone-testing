"""
WavexOne Unified Copy Trading Master QA Test Runner.
Senior QA Architect & Trading Systems Test Engineering Framework.

Usage:
    python run_unified_qa.py --mode=full         # Executes Full Regression Suite
    python run_unified_qa.py --mode=smoke        # Fast Sanity Smoke Tests (< 30s)
    python run_unified_qa.py --mode=risk         # Margin 50% Stop-Out & Liquidation Tests
    python run_unified_qa.py --mode=negative     # Negative Validation & OMS Idempotency
    python run_unified_qa.py --mode=e2e          # Canonical 20-Stage E2E Lifecycle Flow
    python run_unified_qa.py --mode=cleanup      # Safe Teardown & Clean-Slate Recovery
    python run_unified_qa.py --module=<name>     # Execute specific test class or module
"""

import sys
import argparse
import pytest
from datetime import datetime, timezone
from core.logger import logger


def parse_args():
    parser = argparse.ArgumentParser(description="WavexOne Unified Copy Trading Master Runner")
    parser.add_argument(
        "--mode",
        choices=["all", "full", "smoke", "risk", "negative", "e2e", "cleanup"],
        default="smoke",
        help="Test execution mode (default: smoke)"
    )
    parser.add_argument(
        "--module",
        type=str,
        default=None,
        help="Specific test class or module to execute (e.g. TestCopyTradingSmoke)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info(f"=== WavexOne Unified QA Runner Starting [Mode: {args.mode}] ===")

    pytest_args = ["-v", "-s"]

    if args.module:
        pytest_args.extend(["-k", args.module])
    elif args.mode == "smoke":
        pytest_args.extend(["-m", "smoke", "tests/test_copy_trading_regression.py"])
    elif args.mode == "risk":
        pytest_args.extend(["-m", "risk", "tests/test_copy_trading_regression.py"])
    elif args.mode == "negative":
        pytest_args.extend(["-m", "negative", "tests/test_copy_trading_regression.py"])
    elif args.mode == "cleanup":
        pytest_args.extend(["-m", "cleanup", "tests/test_copy_trading_regression.py"])
    elif args.mode == "e2e":
        pytest_args.append("tests/test_copy_trading_e2e.py")
    elif args.mode == "full":
        pytest_args.append("tests/test_copy_trading_regression.py")
    elif args.mode == "all":
        pytest_args.extend([
            "tests/test_copy_trading_e2e.py",
            "tests/test_copy_trading_regression.py",
            "tests/test_advanced_copy_trading_features.py",
            "tests/test_margin_stop_out.py",
        ])

    exit_code = pytest.main(pytest_args)
    logger.info(f"=== WavexOne Unified QA Runner Finished [Exit Code: {exit_code}] ===")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
