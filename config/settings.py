"""
WavexOne Automated Testing Configuration Settings.
Loads credentials securely from .env and defines endpoints, account mappings,
and test matrix parameters.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")


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
    MODIFY_ORDER_ENDPOINT = f"{BASE_URL}/book/modify.php"
    BALANCE_ENDPOINT = f"{BASE_URL}/book/balance.php"
    CREATE_FINGERPRINT_ENDPOINT = f"{BASE_URL}/dashboard/api/create_fingerprint.php"
    ACCOUNT_LIST_ENDPOINT = f"{BASE_URL}/dashboard/api/accountList.php"

    # Social Trading Endpoints
    COPY_FOLLOW_ENDPOINT = f"{BASE_URL}/user/follow.php"
    UPDATE_COPY_METHOD_ENDPOINT = f"{BASE_URL}/user/updateCopyTradingMethod.php"
    COPY_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/copyFollowingList.php"
    COPY_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userCopyFollowers.php"
    MAM_FOLLOW_ENDPOINT = f"{BASE_URL}/user/mamfollow.php"
    MAM_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userMamFollowers.php"
    PAMM_FOLLOW_ENDPOINT = f"{BASE_URL}/user/pammFollow.php"
    PAMM_MASTER_FOLLOWERS_ENDPOINT = f"{BASE_URL}/user/userPammFollowers.php"
    PAMM_WITHDRAW_ENDPOINT = f"{BASE_URL}/user/withdrawPammAmount.php"

    # Client Portal & Wallet / Withdrawal Endpoints
    PORTAL_SESSION_ENDPOINT = f"{BASE_URL}/client-portal/ClientPortal/setPortalSession"
    PORTAL_BOOTSTRAP_ENDPOINT = f"{BASE_URL}/client-portal/apiBootstrap"
    PORTAL_REDEEM_CONFIG_ENDPOINT = f"{BASE_URL}/client-portal/apiRedeemConfig"
    PORTAL_SEND_OTP_ENDPOINT = f"{BASE_URL}/client-portal/apiSendWithdrawOtp"
    PORTAL_SUBMIT_WITHDRAW_ENDPOINT = f"{BASE_URL}/client-portal/apiSubmitWithdraw"

    # Common Password
    DEFAULT_PASSWORD = DEFAULT_PASSWORD
    PASSWORD = DEFAULT_PASSWORD

    # Master Accounts
    MASTERS = {
        "copy_trading": {
            "name": "ctmaster",
            "email": os.getenv("CT_MASTER_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "account_id": os.getenv("CT_MASTER_ACCOUNT_ID", "11060"),
            "uid": os.getenv("CT_MASTER_UID", "1060")
        },
        "mam": {
            "name": "mammaster",
            "email": os.getenv("MAM_MASTER_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "account_id": os.getenv("MAM_MASTER_ACCOUNT_ID", "11056"),
            "uid": os.getenv("MAM_MASTER_UID", "1056")
        },
        "pamm": {
            "name": "pammmaster",
            "email": os.getenv("PAMM_MASTER_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "account_id": os.getenv("PAMM_MASTER_ACCOUNT_ID", "11054"),
            "uid": os.getenv("PAMM_MASTER_UID", "1054")
        }
    }

    # Follower Accounts with real verified account IDs
    COPY_FOLLOWERS = [
        {
            "name": f"ctf{i}",
            "email": os.getenv(f"CT_FOLLOWER_{i}_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "expected_account_id": os.getenv(f"CT_FOLLOWER_{i}_ACCOUNT_ID", ["11041", "11043", "11045", "11048", "11050"][i - 1]),
            "expected_multiplier": 3.0
        }
        for i in range(1, 6)
    ]

    MAM_FOLLOWERS = [
        {
            "name": f"mamf{i}",
            "email": os.getenv(f"MAM_FOLLOWER_{i}_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "expected_account_id": os.getenv(f"MAM_FOLLOWER_{i}_ACCOUNT_ID", ["11058", "11062", "11064", "11088", "11066"][i - 1]),
            "expected_share": 50.0
        }
        for i in range(1, 6)
    ]

    PAMM_FOLLOWERS = [
        {
            "name": f"pammf{i}",
            "email": os.getenv(f"PAMM_FOLLOWER_{i}_EMAIL", ""),
            "password": DEFAULT_PASSWORD,
            "expected_account_id": os.getenv(f"PAMM_FOLLOWER_{i}_ACCOUNT_ID", ["11078", "11080", "11082", "11084", "11086"][i - 1]),
            "expected_investment": 1000000.0
        }
        for i in range(1, 6)
    ]

    # Directories
    REPORTS_DIR = BASE_DIR / "reports"
    LOGS_DIR = BASE_DIR / "logs"

    # Testing symbol & default test lot
    DEFAULT_SYMBOL = "X:BTCUSD"
    DEFAULT_LOT = 1.00


# Ensure directories exist
WavexSettings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
WavexSettings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
