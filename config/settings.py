"""
WavexOne Automated Testing Configuration Settings.
Defines endpoints, accounts, credentials, and test matrix thresholds.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PASSWORD = "123"

class WavexSettings:
    # Target Environment
    BASE_URL = os.getenv("WAVEX_BASE_URL", "https://stage.wavexone.com").rstrip("/")
    LOGIN_URL = f"{BASE_URL}/login/"
    DASHBOARD_URL = f"{BASE_URL}/dashboard/"
    CLIENT_PORTAL_URL = f"{BASE_URL}/client-portal/"

    # API Endpoints
    LOGIN_CHECK_ENDPOINT = f"{BASE_URL}/login/check.php"
    PLACE_ORDER_ENDPOINT = f"{BASE_URL}/trade/placeorder.php"
    ORDERS_SNAPSHOT_ENDPOINT = f"{BASE_URL}/book/orders.php"
    SQUAREOFF_ENDPOINT = f"{BASE_URL}/book/squareoff.php"
    CANCEL_ORDER_ENDPOINT = f"{BASE_URL}/book/cancel.php"
    BALANCE_ENDPOINT = f"{BASE_URL}/book/balance.php"
    CREATE_FINGERPRINT_ENDPOINT = f"{BASE_URL}/dashboard/api/create_fingerprint.php"
    ACCOUNT_LIST_ENDPOINT = f"{BASE_URL}/dashboard/api/accountList.php"

    # Social Trading Endpoints
    COPY_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/copyFollowingList.php"
    COPY_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userCopyFollowers.php"
    MAM_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userMamFollowers.php"
    PAMM_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userPammFollowers.php"

    # Common Password
    DEFAULT_PASSWORD = DEFAULT_PASSWORD
    PASSWORD = DEFAULT_PASSWORD

    # Master Accounts
    MASTERS = {
        "copy_trading": {
            "name": "ctmaster",
            "email": "ctmaster@mailinator.com",
            "password": DEFAULT_PASSWORD,
            "account_id": "11060"
        },
        "mam": {
            "name": "mammaster",
            "email": "mammaster@mailinator.com",
            "password": DEFAULT_PASSWORD,
            "account_id": "11056"
        },
        "pamm": {
            "name": "pammmaster",
            "email": "pammmaster@mailinator.com",
            "password": DEFAULT_PASSWORD,
            "account_id": "11054"
        }
    }

    # Follower Accounts
    COPY_FOLLOWERS = [
        {"name": f"ctf{i}", "email": f"ctf{i}@mailinator.com", "password": DEFAULT_PASSWORD, "expected_multiplier": 3.0}
        for i in range(1, 6)
    ]

    MAM_FOLLOWERS = [
        {"name": f"mamf{i}", "email": f"mamf{i}@mailinator.com", "password": DEFAULT_PASSWORD, "expected_share": 50.0}
        for i in range(1, 6)
    ]

    PAMM_FOLLOWERS = [
        {"name": f"pammf{i}", "email": f"pammf{i}@mailinator.com", "password": DEFAULT_PASSWORD, "expected_investment": 1000000.0}
        for i in range(1, 6)
    ]

    # Directories
    REPORTS_DIR = BASE_DIR / "reports"
    LOGS_DIR = BASE_DIR / "logs"

    # Test Matrix Limits (Strictly 20 to 50 orders)
    ORDERS_PER_SUITE = 10  # 10 Copy Trading + 10 MAM + 10 PAMM = 30 Orders Total
    MIN_ORDERS_TOTAL = 20
    MAX_ORDERS_TOTAL = 50

# Ensure directories exist
WavexSettings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
WavexSettings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
