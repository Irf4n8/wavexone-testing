"""
Playwright Page Object Model for WavexOne Copy Trading.
Handles browser automation, login, account verification, trade placement,
order book inspection, and evidence screenshots via Playwright Chromium.
"""
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config.settings import WavexSettings
from core.logger import logger

SCREENSHOTS_DIR = Path("reports/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


class WavexPlaywrightSession:
    """Manages a dedicated browser context and page for an account."""

    def __init__(self, browser: Browser, name: str, email: str, password: str, account_id: str):
        self.browser = browser
        self.name = name
        self.email = email
        self.password = password
        self.account_id = account_id
        self.context: BrowserContext = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        self.page: Page = self.context.new_page()

    def navigate_login(self) -> None:
        """Navigate to login page."""
        logger.info(f"[{self.name}] Navigating to {WavexSettings.LOGIN_URL}...")
        self.page.goto(WavexSettings.LOGIN_URL, wait_until="domcontentloaded", timeout=25000)

    def login(self) -> bool:
        """Perform UI authentication."""
        self.navigate_login()
        self.page.fill("input#email", self.email)
        self.page.fill("input#password", self.password)
        self.page.click("button.xn-btn-login")

        # Wait for redirect to dashboard
        try:
            self.page.wait_for_url("**/dashboard/**", timeout=25000)
            logger.info(f"[{self.name}] Successfully logged in to Dashboard UI.")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Login timeout or failure: {e}")
            return False

    def verify_account_id(self) -> str:
        """Verify the active account ID displayed on the UI top navigation bar."""
        try:
            self.page.wait_for_selector("#xnAccountCurrent", state="attached", timeout=12000)
            displayed_id = self.page.locator("#xnAccountCurrent").text_content() or ""
            displayed_id = displayed_id.strip()
            logger.info(f"[{self.name}] UI Attached Account ID: '{displayed_id}' (Expected: '{self.account_id}')")
            return displayed_id
        except Exception as e:
            logger.error(f"[{self.name}] Failed to read account ID from UI: {e}")
            return ""

    def get_open_positions_from_ui(self) -> List[Dict[str, str]]:
        """Extract open positions rows from the UI openpending table."""
        positions = []
        try:
            # Table with open positions has class 'openpending'
            rows = self.page.query_selector_all("table.openpending tbody tr")
            for r in rows:
                txt = r.inner_text().lower()
                if any(s in txt for s in ["no data", "closed", "cancelled"]):
                    continue
                cells = r.query_selector_all("td")
                if len(cells) >= 5:
                    pos = {
                        "id": cells[0].inner_text().strip(),
                        "time": cells[1].inner_text().strip(),
                        "symbol": cells[2].inner_text().strip(),
                        "order": cells[3].inner_text().strip(),
                        "lot": cells[4].inner_text().strip(),
                    }
                    if len(cells) >= 8:
                        pos["sl"] = cells[7].inner_text().strip()
                    if len(cells) >= 9:
                        pos["tp"] = cells[8].inner_text().strip()
                    positions.append(pos)
        except Exception as e:
            logger.warning(f"[{self.name}] Error reading positions table from UI: {e}")
        return positions

    def clear_ui_toasts(self) -> None:
        """Clear any pre-existing toasts from the DOM."""
        try:
            self.page.evaluate('() => document.querySelectorAll(".toast").forEach(t => t.remove())')
        except Exception:
            pass

    def wait_for_ui_position(self, symbol: str, expected_lot: Optional[float] = None, timeout: float = 12.0) -> Optional[Dict[str, Any]]:
        """Wait until a position notification or table row appears in the UI."""
        clean_sym = symbol.replace("X:", "").replace("C:", "").upper()
        start = time.time()
        while time.time() - start < timeout:
            # 1. Check live toast notifications
            try:
                toasts = self.page.locator(".toast-message").all()
                for t in toasts:
                    txt = t.inner_text().strip()
                    if clean_sym in txt.upper():
                        # Example: "#74379 · BTCUSD · BUY · 0.5 lots @ 75603.8"
                        parts = [p.strip() for p in txt.split("·")]
                        lot_val = None
                        for p in parts:
                            if "lot" in p:
                                try:
                                    lot_str = p.split("@")[0].replace("lots", "").replace("lot", "").strip()
                                    lot_val = float(lot_str)
                                except ValueError:
                                    pass
                        if expected_lot is not None:
                            if lot_val is None or abs(lot_val - expected_lot) > 0.001:
                                continue
                        return {
                            "source": "toast",
                            "text": txt,
                            "lot": lot_val,
                            "order_id": parts[0].replace("#", "").strip() if len(parts) > 0 else ""
                        }
            except Exception:
                pass

            # 2. Check open positions table rows across all tables (ignore closed/cancelled history)
            try:
                rows = self.page.query_selector_all("tbody tr")
                for r in rows:
                    txt = r.inner_text().strip()
                    txt_lower = txt.lower()
                    if any(s in txt_lower for s in ["closed", "cancelled", "rejected", "no data"]):
                        continue  # Skip historical closed/cancelled trades and empty placeholders
                    if clean_sym in txt.upper() and ("BUY" in txt or "SELL" in txt):
                        cells = r.query_selector_all("td")
                        row_lot = None
                        row_oid = ""
                        if len(cells) >= 5:
                            row_oid = cells[0].inner_text().strip()
                            try:
                                row_lot = float(cells[4].inner_text().strip())
                            except (ValueError, IndexError):
                                pass
                        if row_lot is None:
                            for token in txt.split():
                                try:
                                    val = float(token)
                                    if expected_lot is not None and abs(val - expected_lot) < 0.001:
                                        row_lot = val
                                        break
                                except ValueError:
                                    pass
                        if expected_lot is not None and row_lot is not None:
                            if abs(row_lot - expected_lot) > 0.001:
                                continue
                        return {
                            "source": "table",
                            "text": txt,
                            "lot": row_lot if row_lot is not None else expected_lot,
                            "order_id": row_oid
                        }
            except Exception:
                pass

            time.sleep(0.4)
        return None

    def wait_for_ui_positions_cleared(self, timeout: float = 10.0) -> bool:
        """Wait until 0 open positions remain in the UI table."""
        start = time.time()
        while time.time() - start < timeout:
            positions = self.get_open_positions_from_ui()
            if len(positions) == 0:
                return True
            time.sleep(0.5)
        try:
            self.page.reload(wait_until="domcontentloaded")
            time.sleep(1.5)
            return len(self.get_open_positions_from_ui()) == 0
        except Exception:
            return False

    def place_market_order_ui(self, lot: float = 0.50, side: str = "buy") -> bool:
        """Place a market order using the UI trading form."""
        try:
            logger.info(f"[{self.name}] Placing {side.upper()} {lot:.2f} lot via UI...")
            # Set lot size input
            self.page.fill("input#lotsizem", f"{lot:.2f}")
            time.sleep(0.2)
            
            if side.lower() == "buy":
                self.page.click("button#buy_symbol")
            else:
                self.page.click("button#sell_symbol")
                
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Error placing order via UI: {e}")
            return False

    def capture_screenshot(self, filename: str) -> str:
        """Capture screenshot as test evidence."""
        filepath = str(SCREENSHOTS_DIR / filename)
        try:
            self.page.screenshot(path=filepath, full_page=False)
            logger.info(f"[{self.name}] Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[{self.name}] Screenshot failed: {e}")
            return ""

    def close(self) -> None:
        """Close browser context."""
        try:
            self.context.close()
        except Exception:
            pass
