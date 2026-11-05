"""
Advanced Social Trading Test Suite for WavexOne.
Covers:
  1. Follower Manual Early Close (CT & MAM): Follower closes independently without affecting master or other followers.
  2. Follower Independent Order: Follower places trade; verifies it does NOT fan out to master or peers.
  3. Multi-Pair Concurrency & Stress: Rapid concurrent order placement across Forex, Gold, and Crypto.
"""
import time
import pytest
from typing import List, Dict, Any
from config.settings import WavexSettings
from core.client import WavexUserSession
from core.logger import logger


class TestAdvancedSocialTrading:

    @classmethod
    def setup_class(cls):
        logger.info("Initializing Advanced Social Trading Test Suite...")
        # CT Master & Followers
        ct_cfg = WavexSettings.MASTERS["copy_trading"]
        cls.ct_master = WavexUserSession(ct_cfg["email"], ct_cfg["password"], ct_cfg["name"])
        assert cls.ct_master.authenticate(), "CT Master auth failed"

        cls.ct_followers: List[WavexUserSession] = []
        for f in WavexSettings.COPY_FOLLOWERS:
            s = WavexUserSession(f["email"], f["password"], f["name"])
            assert s.authenticate(), f"CT Follower {f['name']} auth failed"
            cls.ct_followers.append(s)

        # MAM Master & Followers
        mam_cfg = WavexSettings.MASTERS["mam"]
        cls.mam_master = WavexUserSession(mam_cfg["email"], mam_cfg["password"], mam_cfg["name"])
        assert cls.mam_master.authenticate(), "MAM Master auth failed"

        cls.mam_followers: List[WavexUserSession] = []
        for f in WavexSettings.MAM_FOLLOWERS:
            s = WavexUserSession(f["email"], f["password"], f["name"])
            assert s.authenticate(), f"MAM Follower {f['name']} auth failed"
            cls.mam_followers.append(s)

        logger.info("All master and follower sessions authenticated.")

    @classmethod
    def teardown_class(cls):
        """Safety cleanup of all accounts."""
        for sess in [cls.ct_master, cls.mam_master] + cls.ct_followers + cls.mam_followers:
            open_ords = sess.get_open_orders()
            for o in open_ords:
                sess.squareoff_position(o["id"])

    def test_01_copy_trade_follower_manual_early_close(self):
        """Test that a follower closing early does NOT affect the master or peer followers."""
        logger.info("\n--- [ADVANCED TEST 1] Copy Trading: Follower Manual Early Close ---")
        sym = "C:EURUSD"
        master_lot = 0.01
        expected_follower_lot = 0.03

        # 1. Master places order
        res = self.ct_master.place_order(symbol=sym, side="buy", lot=master_lot)
        assert res.get("status") == "success", f"Master order failed: {res}"
        master_oid = str(res["data"]["orderId"])
        logger.info(f"[OK] CT Master placed BUY {master_lot} {sym} (ID={master_oid})")

        time.sleep(2.5)

        # 2. Verify all 5 followers received the order
        f_order_ids = {}
        for f in self.ct_followers:
            orders = f.get_open_orders()
            matched = [o for o in orders if o.get("symbol") == sym and o.get("bs", "").upper() == "BUY"]
            assert len(matched) > 0, f"Follower {f.name} missing copied order"
            f_order_ids[f.name] = matched[0]["id"]
            logger.info(f"  Follower {f.name} confirmed copied ID={matched[0]['id']}, Lot={matched[0]['lot']}")

        # 3. Follower 1 (ctf1) closes their order independently
        early_closer = self.ct_followers[0]
        f1_oid = f_order_ids[early_closer.name]
        c_res = early_closer.squareoff_position(f1_oid)
        assert c_res.get("status") == "success", f"Follower early close failed: {c_res}"
        logger.info(f"[ACTION] Follower {early_closer.name} manually closed order {f1_oid}")

        time.sleep(2.0)

        # 4. Assert Follower 1 is closed, but Master and Followers 2-5 remain OPEN
        f1_orders = early_closer.get_open_orders()
        assert not any(o["id"] == f1_oid for o in f1_orders), f"{early_closer.name} order still open after manual close!"
        logger.info(f"  [VERIFIED] Follower {early_closer.name} position is closed.")

        m_orders = self.ct_master.get_open_orders()
        assert any(o["id"] == master_oid for o in m_orders), "Master order was unexpectedly affected by follower close!"
        logger.info(f"  [VERIFIED] Master order {master_oid} remains OPEN and unaffected.")

        for peer in self.ct_followers[1:]:
            peer_orders = peer.get_open_orders()
            assert any(o["id"] == f_order_ids[peer.name] for o in peer_orders), f"Peer {peer.name} was unexpectedly closed!"
        logger.info("  [VERIFIED] Peers ctf2-ctf5 remain OPEN and unaffected.")

        # 5. Master closes order
        m_close = self.ct_master.squareoff_position(master_oid)
        assert m_close.get("status") == "success", f"Master squareoff failed: {m_close}"
        logger.info(f"[ACTION] Master position {master_oid} closed.")

        time.sleep(3.0)

        # 6. Verify peers are now closed
        for peer in self.ct_followers[1:]:
            p_orders = peer.get_open_orders()
            assert not any(o["id"] == f_order_ids[peer.name] for o in p_orders), f"Peer {peer.name} order not closed after master squareoff!"
        logger.info("  [VERIFIED] All peers closed cleanly after master squareoff.")

    def test_02_follower_independent_order_placement(self):
        """Test that a follower placing their own trade does NOT copy to master or peers."""
        logger.info("\n--- [ADVANCED TEST 2] Follower Independent Order Placement ---")
        f_user = self.ct_followers[0]
        sym = "C:GBPUSD"
        lot = 0.01

        # 1. Follower places an independent order
        res = f_user.place_order(symbol=sym, side="buy", lot=lot)
        assert res.get("status") == "success", f"Follower order failed: {res}"

        time.sleep(1.5)

        # 2. Verify order is in follower's book and retrieve order ID
        f_orders = f_user.get_open_orders()
        matched = [o for o in f_orders if o.get("symbol") == sym and o.get("bs", "").upper() == "BUY"]
        assert len(matched) > 0, f"Independent order not found in follower book: {f_orders}"
        f_oid = matched[0]["id"]
        logger.info(f"[OK] Follower {f_user.name} placed independent BUY {lot} {sym} (Confirmed in book ID={f_oid})")

        # 3. Verify order did NOT copy to Master
        m_orders = self.ct_master.get_open_orders()
        assert len(m_orders) == 0, f"Master book unexpectedly polluted with follower trade: {m_orders}"
        logger.info("  [VERIFIED] Master book remains completely clean (0 open orders).")

        # 4. Verify order did NOT copy to other followers
        for peer in self.ct_followers[1:]:
            p_orders = peer.get_open_orders()
            assert len(p_orders) == 0, f"Peer {peer.name} unexpectedly received follower trade: {p_orders}"
        logger.info("  [VERIFIED] All other followers remain completely clean.")

        # 5. Clean up follower order
        c_res = f_user.squareoff_position(f_oid)
        assert c_res.get("status") == "success", f"Follower close failed: {c_res}"
        time.sleep(2.0)
        assert len(f_user.get_open_orders()) == 0
        logger.info(f"  [VERIFIED] Follower {f_user.name} closed independent order cleanly.")

    def test_03_mam_follower_manual_early_close(self):
        """Test that a MAM follower closing early does NOT affect the MAM master or peers."""
        logger.info("\n--- [ADVANCED TEST 3] MAM: Follower Manual Early Close ---")
        sym = "C:USDJPY"
        master_lot = 0.02

        # 1. MAM Master places order
        res = self.mam_master.place_order(symbol=sym, side="buy", lot=master_lot)
        assert res.get("status") == "success", f"MAM Master order failed: {res}"
        master_oid = str(res["data"]["orderId"])
        logger.info(f"[OK] MAM Master placed BUY {master_lot} {sym} (ID={master_oid})")

        time.sleep(2.5)

        # 2. Verify all 5 MAM followers received allocated order
        f_order_ids = {}
        for f in self.mam_followers:
            orders = f.get_open_orders()
            matched = [o for o in orders if o.get("symbol") == sym and o.get("bs", "").upper() == "BUY"]
            assert len(matched) > 0, f"MAM Follower {f.name} missing allocated order"
            f_order_ids[f.name] = matched[0]["id"]
            logger.info(f"  MAM Follower {f.name} allocated ID={matched[0]['id']}, Lot={matched[0]['lot']}")

        # 3. Follower 1 (mamf1) closes their order independently
        early_closer = self.mam_followers[0]
        f1_oid = f_order_ids[early_closer.name]
        c_res = early_closer.squareoff_position(f1_oid)
        assert c_res.get("status") == "success", f"MAM follower early close failed: {c_res}"
        logger.info(f"[ACTION] MAM Follower {early_closer.name} manually closed order {f1_oid}")

        time.sleep(2.0)

        # 4. Verify early closer is closed, master and peers remain open
        assert not any(o["id"] == f1_oid for o in early_closer.get_open_orders())
        logger.info(f"  [VERIFIED] MAM Follower {early_closer.name} position is closed.")

        m_orders = self.mam_master.get_open_orders()
        assert any(o["id"] == master_oid for o in m_orders), "MAM Master order was affected by follower close!"
        logger.info(f"  [VERIFIED] MAM Master order {master_oid} remains OPEN.")

        for peer in self.mam_followers[1:]:
            peer_orders = peer.get_open_orders()
            assert any(o["id"] == f_order_ids[peer.name] for o in peer_orders)
        logger.info("  [VERIFIED] MAM Peers mamf2-mamf5 remain OPEN.")

        # 5. Master closes order
        m_close = self.mam_master.squareoff_position(master_oid)
        assert m_close.get("status") == "success", f"MAM master squareoff failed: {m_close}"
        logger.info(f"[ACTION] MAM Master position {master_oid} closed.")

        time.sleep(3.0)

        for peer in self.mam_followers[1:]:
            p_orders = peer.get_open_orders()
            assert not any(o["id"] == f_order_ids[peer.name] for o in p_orders)
        logger.info("  [VERIFIED] All MAM peers closed cleanly.")

    def test_04_multi_pair_concurrency_stress(self):
        """Test rapid concurrent order placement across 3 different asset classes."""
        logger.info("\n--- [ADVANCED TEST 4] Multi-Pair Concurrency & Stress Fanout ---")
        test_instruments = [
            {"symbol": "C:EURUSD", "side": "buy", "lot": 0.01},
            {"symbol": "C:XAUUSD", "side": "buy", "lot": 0.01},
            {"symbol": "X:BTCUSD", "side": "buy", "lot": 0.01},
        ]

        # 1. Rapidly place 3 orders on CT Master
        master_order_ids = []
        for inst in test_instruments:
            res = self.ct_master.place_order(symbol=inst["symbol"], side=inst["side"], lot=inst["lot"])
            assert res.get("status") == "success", f"Failed placing {inst['symbol']}: {res}"
            oid = str(res["data"]["orderId"])
            master_order_ids.append((inst["symbol"], oid))
            logger.info(f"[OK] Master opened concurrent order {inst['symbol']}: ID={oid}")

        logger.info("Waiting 3.5s for replication engine to fan out 15 sub-orders...")
        time.sleep(3.5)

        # 2. Verify all 5 followers received ALL 3 orders (Total 15 follower orders)
        total_replicated = 0
        follower_orders_map = {f.name: [] for f in self.ct_followers}

        for f in self.ct_followers:
            f_open = f.get_open_orders()
            for sym, _ in master_order_ids:
                matched = [o for o in f_open if o.get("symbol") == sym]
                assert len(matched) > 0, f"Follower {f.name} missing order for {sym}!"
                follower_orders_map[f.name].append(matched[0]["id"])
                total_replicated += 1

        assert total_replicated == 15, f"Expected 15 replicated orders across 5 followers, got {total_replicated}"
        logger.info(f"  [VERIFIED] All 15 concurrent follower positions opened successfully (5 followers x 3 pairs).")

        # 3. Squareoff all 3 master positions in rapid succession
        for sym, m_oid in master_order_ids:
            c_res = self.ct_master.squareoff_position(m_oid)
            assert c_res.get("status") == "success", f"Failed closing {m_oid}: {c_res}"
            logger.info(f"[ACTION] Master closed {sym} (ID={m_oid})")

        logger.info("Waiting 4s for settlement fanout across all 15 positions...")
        time.sleep(4.0)

        # 4. Verify all 15 positions are closed
        for f in self.ct_followers:
            f_open_after = f.get_open_orders()
            for f_oid in follower_orders_map[f.name]:
                assert not any(o["id"] == f_oid for o in f_open_after), f"Follower {f.name} order {f_oid} remained open!"
        logger.info("  [VERIFIED] All 15 follower positions closed cleanly. Zero lingering orders.")

