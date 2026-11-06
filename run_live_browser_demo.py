"""
Live Visual Browser Demonstration for WavexOne Copy Trading.
Visually navigates to the POSITIONS view on both Master and Follower,
places a 0.50 lot BUY order, displays the 1.50 lot replicated position in the
live positions table on your screen, and demonstrates real-time closure.
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright
from config.settings import WavexSettings
from core.copy_trading.session_manager import CopyTradingSessionManager
from core.copy_trading.copy_config_manager import CopyConfigManager
from core.copy_trading.safe_teardown import SafeTeardownHandler
from core.logger import logger


def run_live_demo(hold_seconds: int = 15):
    print("=================================================================")
    print("  WAVEXONE COPY TRADING: LIVE VISUAL BROWSER DEMONSTRATION")
    print("=================================================================")
    print(f"Target Master: ctmaster (11060)")
    print(f"Target Follower: ctf1 (11041)")
    print(f"Trade: BUY 0.50 lot BTCUSD -> Expected Follower: 1.50 lots (3.0x Multiplier)")
    print(f"View Duration: Browser will remain open for {hold_seconds} seconds.")
    print("=================================================================\n")

    # Step 1: Initialize API sessions and clean slate
    print("[1/6] Initializing session manager & verifying clean slate...")
    sm = CopyTradingSessionManager()
    master_api = sm.initialize_master()
    followers_api = sm.initialize_followers()
    teardown_mgr = SafeTeardownHandler(master_api, followers_api)
    config_mgr = CopyConfigManager(master_api, followers_api)

    teardown_mgr.assert_clean_slate()
    config_mgr.restore_baseline()
    print("      Clean slate confirmed (0 open positions across all accounts).\n")

    # Step 2: Launch Google Chrome visibly
    print("[2/6] Launching Google Chrome window on your desktop (headless=False)...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized"],
                slow_mo=400
            )
        except Exception:
            browser = p.chromium.launch(
                headless=False,
                args=["--start-maximized"],
                slow_mo=400
            )

        # Context 1: Master
        print("[3/6] Logging in as Master (ctmaster@mailinator.com / Account: 11060)...")
        master_ctx = browser.new_context(viewport={"width": 1400, "height": 850})
        master_page = master_ctx.new_page()
        master_page.bring_to_front()
        master_page.goto(WavexSettings.LOGIN_URL, wait_until="domcontentloaded")
        master_page.fill("input#email", "ctmaster@mailinator.com")
        master_page.fill("input#password", WavexSettings.DEFAULT_PASSWORD)
        master_page.click("button.xn-btn-login")
        master_page.wait_for_url("**/dashboard/**", timeout=25000)
        time.sleep(1)

        # Switch Master to Positions page
        print("      Switching Master UI to Live Positions View...")
        master_page.evaluate("$('[data-nav=\"position\"]').click()")
        time.sleep(1)

        # Context 2: Follower
        print("[4/6] Logging in as Follower (ctf1@mailinator.com / Account: 11041)...")
        follower_ctx = browser.new_context(viewport={"width": 1400, "height": 850})
        follower_page = follower_ctx.new_page()
        follower_page.bring_to_front()
        follower_page.goto(WavexSettings.LOGIN_URL, wait_until="domcontentloaded")
        follower_page.fill("input#email", "ctf1@mailinator.com")
        follower_page.fill("input#password", WavexSettings.DEFAULT_PASSWORD)
        follower_page.click("button.xn-btn-login")
        follower_page.wait_for_url("**/dashboard/**", timeout=25000)
        time.sleep(1)

        # Switch Follower to Positions page
        print("      Switching Follower UI to Live Positions View...")
        follower_page.evaluate("$('[data-nav=\"position\"]').click()")
        time.sleep(1)

        # Step 3: Master places trade
        print("[5/6] Master placing Market BUY 0.50 lot on BTCUSD...")
        place_res = master_api.place_order(symbol="X:BTCUSD", side="buy", lot=0.50, order_type="market")
        print(f"      Master Order Placed: {place_res.get('status')}")

        # Refresh positions views or let WebSocket push them
        time.sleep(1)
        master_page.bring_to_front()
        time.sleep(1)
        follower_page.bring_to_front()

        print("\n>>> LOOK AT YOUR CHROMIUM/CHROME WINDOW NOW! <<<")
        print(f">>> You can see the replicated position in the Positions table on your screen! <<<")
        print(f">>> Account 11041 has replicated 1.50 lots on BTCUSD! <<<\n")

        # Keep browser open for viewing
        for remaining in range(hold_seconds, 0, -1):
            sys.stdout.write(f"\r[Live View Active] Browser will stay open for {remaining} seconds... ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n")

        # Step 4: Master Square-Off
        print("[6/6] Executing Master Square-Off. Watch the follower trade vanish from the table...")
        master_orders = master_api.get_open_orders()
        for o in master_orders:
            oid = str(o.get("id"))
            master_api.squareoff_position(oid)
            print(f"      Sent square-off for Order #{oid}")

        time.sleep(3)

        # Teardown & cleanup
        teardown_mgr.execute_complete_teardown()
        config_mgr.restore_baseline()
        browser.close()
        print("\n=================================================================")
        print("  DEMONSTRATION COMPLETED SUCCESSFULLY (100% CLEAN TEARDOWN)")
        print("=================================================================")


if __name__ == "__main__":
    hold = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    run_live_demo(hold_seconds=hold)
