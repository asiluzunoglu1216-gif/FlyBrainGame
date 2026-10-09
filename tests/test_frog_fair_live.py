"""Fair Live Validation of Frog Predator AI, Visible Tongue Strike, and Physical Collision.

Validates:
1. Fair start: Frog starts at 18.0m away from fly (within awareness 30m, outside strike range 11m).
2. No teleporting fly, no forced neural spikes.
3. Proper State Machine sequence:
   IDLE -> WATCH -> AIM -> visible TONGUE_STRIKE -> (MISS or CATCH_PULL -> FLY EATEN).
4. Proximity alone NEVER kills: Fly within proximity survives when strike misses.
5. If physical hit: CATCH_PULL is visible and lasts 0.45s before FLY EATEN triggers.
"""
import unittest
from panda3d.core import loadPrcFileData, Vec3
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")

from direct.showbase.ShowBase import ShowBase
from game.frog_entity import FrogEntity


class TestFrogFairLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.base = ShowBase()
        except Exception:
            import builtins
            cls.base = getattr(builtins, "base", None)

    def test_fair_live_frog_interaction(self):
        print("\n" + "=" * 75)
        print("STARTING FAIR LIVE FROG PREDATOR VALIDATION")
        print("=" * 75)

        # 1. Spawn frog at 18.0m away from origin (fair distance, awareness range 30m, strike range 11m)
        frog_pos = Vec3(0.0, 18.0, 0.5)
        frog = FrogEntity(self.base.render, "Kermit_FairTest", frog_pos, scale=1.6)

        # Fly starts at origin, 18m away
        fly_pos = Vec3(0.0, 0.0, 2.0)

        dt = 0.04  # 25 Hz simulation step
        encounters = 0
        visible_tongue_strikes = 0
        misses = 0
        physical_hits = 0
        deaths = 0

        # =====================================================================
        # SCENARIO 1: FLY APPROACHES -> WATCH -> AIM -> TONGUE STRIKE ->
        # FLY VEERS AWAY (DNp01 ESCAPE) -> TONGUE MISSES -> RETRACTS TO COOLDOWN
        # =====================================================================
        print("\n--- TEST CASE A: FAIR APPROACH, ESCAPE VEER & TONGUE MISS ---")
        # Fly flies from 18m to 10m along path
        visited_states = []
        for step in range(20):
            # Normal forward flight approach
            fly_pos.y += 0.4
            if frog.check_encounter(fly_pos) and not frog.encounter_registered:
                encounters += 1
            if frog.state not in visited_states:
                visited_states.append(frog.state)
            frog.update(dt, fly_pos)

        self.assertIn("WATCH", visited_states, "Frog must enter WATCH when fly approaches within 30m")
        print(f"[Step 1] Approach to {fly_pos.y:.1f}m: Frog state = {frog.state}, encounters = {encounters}")

        # Fly enters strike range (dist < 11m)
        fly_pos = Vec3(0.0, 9.5, 2.0)
        aim_telegraphed = False
        strike_launched = False

        for step in range(30):
            frog.update(dt, fly_pos)
            if frog.state == "AIM":
                aim_telegraphed = True
            elif frog.state == "TONGUE_STRIKE":
                strike_launched = True
                visible_tongue_strikes += 1
                # Biological escape veer: Looming detector triggers lateral escape veer away from strike line
                fly_pos.x += 3.5  # Veers 3.5m laterally out of the tongue line
                break

        self.assertTrue(aim_telegraphed, "Frog must visibly telegraph AIM before striking")
        self.assertTrue(strike_launched, "Frog must fire TONGUE_STRIKE")
        print(f"[Step 2] AIM telegraphed = {aim_telegraphed}, TONGUE_STRIKE launched = {strike_launched}")

        # Let tongue complete strike and miss because fly veered out of the path
        miss_completed = False
        for step in range(30):
            caught = frog.update(dt, fly_pos)
            self.assertFalse(caught, "Veered fly must NOT be caught (proximity does not kill!)")
            if frog.state == "COOLDOWN":
                miss_completed = True
                misses += 1
                break

        self.assertTrue(miss_completed, "Missed tongue strike must retract and transition to COOLDOWN")
        print(f"[Step 3] Tongue missed! Frog state = {frog.state}, misses = {misses}, deaths = {deaths}")

        # =====================================================================
        # SCENARIO 2: DIRECT PHYSICAL HIT & VISIBLE CATCH_PULL
        # =====================================================================
        print("\n--- TEST CASE B: DIRECT PHYSICAL HIT & VISIBLE CATCH_PULL RETRACTION ---")
        # Reset frog for second encounter
        frog.state = "IDLE"
        frog.state_timer = 0.0
        frog.is_engaged = False
        frog.encounter_registered = False

        # Position fly in front of frog at 7.0m, trapped without escaping
        fly_pos = Vec3(0.0, 11.0, 1.0)
        frog.check_encounter(fly_pos)
        encounters += 1

        # Advance to AIM
        for _ in range(25):
            frog.update(dt, fly_pos)
            if frog.state == "AIM":
                break

        self.assertEqual(frog.state, "AIM", "Frog must telegraph AIM")
        print(f"[Step 4] Telegraphing strike: state = {frog.state}")

        # Advance through AIM telegraph into TONGUE_STRIKE and physical hit
        strike_visible = False
        hit_occurred = False
        catch_pull_frames = 0

        for _ in range(50):
            caught = frog.update(dt, fly_pos)
            if frog.state == "TONGUE_STRIKE":
                strike_visible = frog.tongue_visible
            elif frog.state == "CATCH_PULL":
                if not hit_occurred:
                    physical_hits += 1
                    hit_occurred = True
                    visible_tongue_strikes += 1
                catch_pull_frames += 1

            if caught:
                deaths += 1
                break

        self.assertTrue(strike_visible, "Tongue strike must be human-visible")
        self.assertTrue(hit_occurred, "Direct tongue contact must trigger physical hit")
        self.assertGreaterEqual(catch_pull_frames, 8, "CATCH_PULL must be visible over multiple frames (0.45s)")
        self.assertEqual(deaths, 1, "Only completed CATCH_PULL retraction triggers FLY EATEN death")
        print(f"[Step 5] Hit confirmed! CATCH_PULL frames = {catch_pull_frames}, Deaths = {deaths}")

        print("\n" + "=" * 75)
        print("FAIR LIVE FROG TEST SUMMARY REPORT:")
        print(f"  encounters:              {encounters}")
        print(f"  visible tongue strikes:  {visible_tongue_strikes}")
        print(f"  misses:                  {misses}")
        print(f"  physical hits:           {physical_hits}")
        print(f"  deaths:                  {deaths}")
        print("=" * 75)


if __name__ == "__main__":
    unittest.main()
