"""
Copy Trading Configuration Manager.
Handles follow/unfollow lifecycle, copy sizing modes (multiplier, balance, equity),
subscription verification, and baseline state restoration.
"""
from typing import Dict, List, Any, Optional
from core.client import WavexUserSession
from core.logger import logger

BASELINE_COPY_METHOD = "multiplier"
BASELINE_MULTIPLIER_VALUE = "3.0"
MASTER_UID = "1060"


class CopyConfigManager:
    """Manages Copy Trading configuration, mode switches, and baseline restoration."""

    def __init__(self, master: WavexUserSession, followers: List[WavexUserSession]):
        self.master = master
        self.followers = followers
        self.master_uid = str(master.user_id or MASTER_UID)

    def get_master_followers_list(self) -> List[Dict[str, Any]]:
        """Query followers subscribed to this Master via /user/userCopyFollowers.php."""
        return self.master.get_copy_followers()

    def get_follower_subscriptions(self, follower: WavexUserSession) -> List[Dict[str, Any]]:
        """Query active subscriptions for a follower via /user/userCopyFollowers.php."""
        return follower.get_copy_following()

    def verify_all_subscribed(self) -> Dict[str, Any]:
        """Verify that all 5 followers are actively subscribed to the Master."""
        master_followers = self.get_master_followers_list()
        subscribed_accs = {str(f.get("account_id")) for f in master_followers}
        subscribed_names = {str(f.get("name")) for f in master_followers}

        results = {}
        all_active = True

        for f in self.followers:
            is_in_master_list = (str(f.account_id) in subscribed_accs) or (str(f.name) in subscribed_names)
            f_subs = self.get_follower_subscriptions(f)
            is_in_follower_list = any(
                str(s.get("manager_id")) == self.master_uid or str(s.get("account_id")) == str(self.master.account_id)
                for s in f_subs
            )

            status = is_in_master_list and is_in_follower_list
            if not status:
                all_active = False

            results[f.name] = {
                "account_id": f.account_id,
                "user_id": f.user_id,
                "in_master_list": is_in_master_list,
                "in_follower_list": is_in_follower_list,
                "is_active": status
            }

        return {
            "all_active": all_active,
            "details": results,
            "total_followers_count": len(master_followers)
        }

    def set_follower_mode(self, follower: WavexUserSession, method: str, value: str = "") -> Dict[str, Any]:
        """Update copy trading method (multiplier, balance, equity) for a follower."""
        val = str(value) if method == "multiplier" else ""
        res = follower.update_copy_trading_method(master_uid=self.master_uid, method=method, value=val)
        logger.info(f"[{follower.name}] Updated copy mode to '{method}' (value='{val}'): {res.get('status')}")
        return res

    def set_all_followers_mode(self, method: str, value: str = "") -> bool:
        """Update copy trading method for all 5 followers."""
        success = True
        for f in self.followers:
            res = self.set_follower_mode(f, method=method, value=value)
            if res.get("status") != "success":
                success = False
        return success

    def restore_baseline(self) -> bool:
        """Restore all 5 followers to baseline: method='multiplier', value='3.0'."""
        logger.info("Restoring all followers to baseline configuration (multiplier 3.0x)...")
        # Ensure everyone is following master
        for f in self.followers:
            try:
                f.follow_copy_master(master_uid=self.master_uid, method=BASELINE_COPY_METHOD, value=BASELINE_MULTIPLIER_VALUE)
            except Exception as e:
                logger.warning(f"Error ensuring follow for {f.name}: {e}")

        return self.set_all_followers_mode(method=BASELINE_COPY_METHOD, value=BASELINE_MULTIPLIER_VALUE)
