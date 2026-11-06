"""
Session and Account Manager for WavexOne Copy Trading.
Enforces strict staging account ID validation, environment safety checks,
and multi-account session management.
"""
import os
from typing import Dict, List, Optional
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger

# Approved Staging Boundary Definitions
APPROVED_STAGING_HOST = "stage.wavexone.com"
APPROVED_MASTER_ACCOUNT_ID = "11060"
APPROVED_MASTER_UID = "1060"
APPROVED_FOLLOWER_ACCOUNT_IDS = {
    "ctf1": "11041",
    "ctf2": "11043",
    "ctf3": "11045",
    "ctf4": "11048",
    "ctf5": "11050"
}


class SecurityBoundaryException(Exception):
    """Raised when an execution violates environment or account safety boundaries."""
    pass


class CopyTradingSessionManager:
    """Manages authenticated sessions across Master and 5 Follower accounts with strict validation."""

    def __init__(self):
        self._validate_environment()
        self.master_session: Optional[WavexUserSession] = None
        self.follower_sessions: Dict[str, WavexUserSession] = {}
        self.all_sessions: List[WavexUserSession] = []

    def _validate_environment(self):
        """Ensure execution is strictly targeted to approved Staging domain."""
        base_url = WavexSettings.BASE_URL.lower()
        if APPROVED_STAGING_HOST not in base_url:
            err = (
                f"FATAL SECURITY VIOLATION: Execution domain '{base_url}' is not an approved "
                f"staging host ({APPROVED_STAGING_HOST})! Halting execution immediately."
            )
            logger.critical(err)
            raise SecurityBoundaryException(err)

    def initialize_master(self) -> WavexUserSession:
        """Authenticate and validate the Master trading session."""
        m_cfg = WavexSettings.MASTERS["copy_trading"]
        expected_acc = str(m_cfg.get("account_id", APPROVED_MASTER_ACCOUNT_ID))

        if expected_acc != APPROVED_MASTER_ACCOUNT_ID:
            raise SecurityBoundaryException(
                f"FATAL: Master account ID '{expected_acc}' does not match approved staging ID '{APPROVED_MASTER_ACCOUNT_ID}'."
            )

        master = WavexUserSession(
            email=m_cfg["email"],
            password=m_cfg["password"],
            name="ctmaster",
            expected_account_id=expected_acc
        )
        if not master.authenticate():
            raise RuntimeError("Failed to authenticate Master account.")

        if str(master.account_id) != APPROVED_MASTER_ACCOUNT_ID:
            raise SecurityBoundaryException(
                f"Master live account ID '{master.account_id}' does not match approved staging ID '{APPROVED_MASTER_ACCOUNT_ID}'."
            )

        self.master_session = master
        return master

    def initialize_followers(self) -> List[WavexUserSession]:
        """Authenticate and validate all 5 follower trading sessions."""
        self.follower_sessions.clear()
        followers_list = []

        for f_cfg in WavexSettings.COPY_FOLLOWERS:
            name = f_cfg["name"]
            expected_acc = APPROVED_FOLLOWER_ACCOUNT_IDS.get(name)
            if not expected_acc:
                raise SecurityBoundaryException(f"Unauthorized follower '{name}' detected! Halting immediately.")

            sess = WavexUserSession(
                email=f_cfg["email"],
                password=f_cfg["password"],
                name=name,
                expected_account_id=expected_acc
            )
            if not sess.authenticate():
                raise RuntimeError(f"Failed to authenticate Follower '{name}'.")

            if str(sess.account_id) != expected_acc:
                raise SecurityBoundaryException(
                    f"Follower {name} live account ID '{sess.account_id}' does not match approved staging ID '{expected_acc}'."
                )

            self.follower_sessions[name] = sess
            followers_list.append(sess)

        return followers_list

    def initialize_all(self) -> Dict[str, WavexUserSession]:
        """Initialize both Master and all 5 Followers with full safety verification."""
        self.initialize_master()
        followers = self.initialize_followers()
        self.all_sessions = [self.master_session] + followers

        logger.info(
            f"Successfully authenticated and verified 6 Staging accounts: "
            f"Master={self.master_session.account_id}, "
            f"Followers={[f.account_id for f in followers]}"
        )
        return {
            "master": self.master_session,
            **self.follower_sessions
        }

    def get_master(self) -> WavexUserSession:
        if not self.master_session:
            return self.initialize_master()
        return self.master_session

    def get_followers(self) -> List[WavexUserSession]:
        if not self.follower_sessions or len(self.follower_sessions) < 5:
            return self.initialize_followers()
        return list(self.follower_sessions.values())

    def get_follower(self, name: str) -> WavexUserSession:
        if name not in self.follower_sessions:
            self.initialize_followers()
        return self.follower_sessions[name]

