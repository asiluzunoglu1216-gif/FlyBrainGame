"""Unit test verifying visible frog tongue lifecycle, physical collider capture,
miss handling, and encounter invariants.
"""
from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from panda3d.core import NodePath, Vec3
from game.frog_entity import FrogEntity


class TestFrogTongueVisibleStrike(unittest.TestCase):
    def setUp(self):
        self.root = NodePath("TestWorld")
        self.frog = FrogEntity(self.root, "Kermit", Vec3(0, 0, 0))

    def test_01_proximity_alone_does_not_kill(self):
        """Proximity alone MUST NOT kill the fly. Only physical tongue tip collision."""
        fly_pos = Vec3(0, 3.0, 0.5)  # Very close to frog, but frog is IDLE
        caught = self.frog.update(dt=0.02, fly_pos=fly_pos)
        self.assertFalse(caught, "Proximity alone must not kill the fly")
        self.assertEqual(self.frog.state, "WATCH", "Frog should be watching, not instantly killing")

    def test_02_aim_telegraph_before_strike(self):
        """Frog must enter AIM to telegraph attack before tongue strikes."""
        fly_pos = Vec3(0, 6.0, 0.5)
        # Advance through WATCH
        self.frog.state = "WATCH"
        self.frog.state_timer = 0.7
        self.frog.update(dt=0.05, fly_pos=fly_pos)
        self.assertEqual(self.frog.state, "AIM", "Frog must telegraph attack via AIM state")
        self.assertFalse(self.frog.tongue_visible, "Tongue should not be visible during AIM telegraph")

    def test_03_tongue_miss_does_not_kill(self):
        """When fly moves away and tongue misses, frog retracts and cooldown begins without killing fly."""
        # Setup strike towards initial position (0, 8.0, 0.5)
        fly_pos = Vec3(0, 8.0, 0.5)
        self.frog.state = "AIM"
        self.frog.state_timer = 0.4
        self.frog.update(dt=0.02, fly_pos=fly_pos)
        self.assertEqual(self.frog.state, "TONGUE_STRIKE")
        self.assertTrue(self.frog.tongue_visible)

        # Fly dodges away to (15.0, 8.0, 10.0)
        dodged_pos = Vec3(15.0, 8.0, 10.0)
        caught = False
        # Advance through entire strike duration + retraction
        for _ in range(40):
            c = self.frog.update(dt=0.02, fly_pos=dodged_pos)
            if c:
                caught = True

        self.assertFalse(caught, "Missed tongue strike must not kill the fly")
        self.assertFalse(self.frog.physical_hit, "Physical hit must be False on miss")
        self.assertIn(self.frog.state, ("COOLDOWN", "IDLE"), "Frog must enter COOLDOWN after miss")

    def test_04_physical_tongue_tip_hit_pulls_and_catches(self):
        """When physical tongue tip collides with fly, CATCH_PULL visibly pulls fly to mouth."""
        fly_pos = Vec3(0, 5.0, 0.8)
        self.frog.state = "AIM"
        self.frog.state_timer = 0.4
        self.frog.update(dt=0.02, fly_pos=fly_pos)
        self.assertEqual(self.frog.state, "TONGUE_STRIKE")

        # Advance tongue until tip hits fly
        hit_occurred = False
        for _ in range(15):
            self.frog.update(dt=0.02, fly_pos=fly_pos)
            if self.frog.state == "CATCH_PULL":
                hit_occurred = True
                break

        self.assertTrue(hit_occurred, "Tongue tip must physically collide with stationary fly")
        self.assertTrue(self.frog.physical_hit)

        # Advance pull animation until fly is consumed at mouth
        consumed = False
        for _ in range(35):
            c = self.frog.update(dt=0.02, fly_pos=fly_pos)
            if c:
                consumed = True
                break

        self.assertTrue(consumed, "Fly must be consumed once pulled into frog mouth")

    def test_05_encounter_invariant(self):
        """Invariant: frog_deaths > 0 must imply frog_encounters >= frog_deaths."""
        fly_pos = Vec3(0, 5.0, 0.8)
        enc = self.frog.check_encounter(fly_pos)
        self.assertTrue(enc, "Approaching fly must register encounter")
        self.frog.state = "AIM"
        self.frog.state_timer = 0.4
        self.frog.update(dt=0.02, fly_pos=fly_pos)
        caught = False
        for _ in range(50):
            if self.frog.update(dt=0.02, fly_pos=fly_pos):
                caught = True
                break
        self.assertTrue(caught)
        encounters = 1 if self.frog.encounter_registered else 0
        deaths = 1 if caught else 0
        self.assertGreaterEqual(encounters, deaths)


if __name__ == "__main__":
    unittest.main()
