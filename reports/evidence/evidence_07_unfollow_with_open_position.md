# Evidence Report: Copy Trading: Unfollow While Trade Position is Open (✅ PASS)

**Test Identifier:** `evidence_07_unfollow_with_open_position`  
**Objective:** Verify and record platform behavior when a follower unfollows master with an active open trade. Tagged UNVERIFIED vs spec.  
**Target Staging Engine:** `https://stage.wavexone.com`  
**Execution Timestamp:** `2026-11-05T17:00:57.605578` $\rightarrow$ `2026-11-05T17:01:09.512170` (11.91s)  
**Overall Verification Status:** **✅ PASS**  

---

## 📊 Verification Assertions (2/2 Passed)

| # | Assertion Check | Expected Value | Actual Value Observed | Result | Notes |
| :-: | :--- | :--- | :--- | :---: | :--- |
| 1 | **Observed Behavior: Follower Position on Unfollow** | `UNVERIFIED vs spec` | `Position REMAINED OPEN after unfollow` | ✅ PASS | Tagged UNVERIFIED vs spec pending dev spec confirmation |
| 2 | **Observed Behavior: Master Squareoff after Unfollow** | `UNVERIFIED vs spec` | `Follower position CLOSED with master squareoff` | ✅ PASS | Tagged UNVERIFIED vs spec (Suspected Engine Bug: unfollowed user still closes on master squareoff) |

---

## 📜 Chronological Execution Steps & Telemetry

---

## 🛡️ Account Reconciliation
Verified 0 lingering open orders across master and followers post-execution.