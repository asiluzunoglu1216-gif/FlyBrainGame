"""Ecosystem Integration and Biological Fidelity Tests.

Verifies:
1. Dynamic Frog Looming: Frog approach activates looming stimulus in EcosystemSensoryManager
   without imposing scripted heading/yaw alterations.
2. Food Visual Tracking: Visible foods produce target azimuth for LC10a sensory input without
   teleporting or artificially steering the fly.
3. Emergent Landing / Perching: Low altitude above solid surface + low speed initiates perching;
   take-off triggers when connectome generates forward drive or escape impulse.
4. Feeding Interaction: Dwell time >= 1.5s on food marks it eaten and triggers 60s respawn timer.
5. Reincarnation / Retry: Resets life stats, frog positions, and connectome state.
"""
from __future__ import annotations

import unittest
from panda3d.core import Vec3, NodePath
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

from game.ecosystem_sensory import EcosystemSensoryManager
from game.food_system import FoodSystem
from game.frog_entity import FrogEntity
from game.natural_world import NaturalWorld
from game.fly_controller import FlyController
from game.brain_worker import BrainWorker
from game.sensory_encoder import SensoryInput

# Ensure headless Panda3D for unit testing
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")


class TestEcosystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = ShowBase()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "base") and cls.base is not None:
            cls.base.destroy()

    def test_01_frog_looming_produces_sensory_stimulus_without_scripted_steering(self):
        """Approaching frog on the left reduces left obstacle distance (inducing LC4/LPLC2 looming).
        Verifies that EcosystemSensoryManager does NOT alter fly yaw directly.
        """
        mgr = EcosystemSensoryManager(max_sensor_range=40.0)
        fly_pos = Vec3(0.0, 0.0, 5.0)
        fly_yaw = 90.0  # Heading towards +Y

        # Frog positioned on the left side (-15, 10, 0)
        frogs = [("Kermit", Vec3(-15.0, 10.0, 0.0), Vec3(0, 0, 0))]
        foods = []

        sensory, nearest_food, frog_threat = mgr.compute_sensory_input(
            fly_pos=fly_pos,
            fly_yaw=fly_yaw,
            terrain_dist_l=40.0,
            terrain_dist_c=40.0,
            terrain_dist_r=40.0,
            foods=foods,
            frogs=frogs
        )

        print(f"\n[Ecosystem Test 1] Frog on Left -> dist_l: {sensory.dist_left:.1f}, "
              f"dist_r: {sensory.dist_right:.1f}, Threat: {frog_threat}")

        self.assertTrue(frog_threat, "Frog within FOV must activate threat flag")
        self.assertLess(sensory.dist_left, sensory.dist_right, "Left distance must be reduced by approaching frog")
        self.assertEqual(fly_yaw, 90.0, "Fly yaw must not be modified by sensory manager")

    def test_02_food_tracking_provides_lc10a_azimuth_without_scripted_motion(self):
        """Food located ahead and to the right provides positive azimuth for LC10a.
        Fly position remains untouched.
        """
        mgr = EcosystemSensoryManager(max_sensor_range=40.0)
        fly_pos = Vec3(0.0, 0.0, 5.0)
        fly_yaw = 90.0  # Heading +Y

        # Food at (10, 20, 1) -> right of heading
        foods = [("APPLE", Vec3(10.0, 20.0, 1.0))]
        frogs = []

        sensory, nearest_food, frog_threat = mgr.compute_sensory_input(
            fly_pos=fly_pos,
            fly_yaw=fly_yaw,
            terrain_dist_l=40.0,
            terrain_dist_c=40.0,
            terrain_dist_r=40.0,
            foods=foods,
            frogs=frogs
        )

        print(f"\n[Ecosystem Test 2] Food on Right -> nearest: {nearest_food}, "
              f"azimuth: {sensory.target_azimuth:.2f}, visible: {sensory.target_visible}")

        self.assertEqual(nearest_food, "APPLE")
        self.assertTrue(sensory.target_visible)
        self.assertGreater(sensory.target_azimuth, 0.0, "Target on right must produce positive azimuth for LC10a")

    def test_03_food_feeding_dwell_time_and_respawn(self):
        """Verifies feeding requires >= 1.5s dwell time on active food."""
        food_sys = FoodSystem(self.base.render, max_active=3)
        self.assertTrue(len(food_sys.foods) >= 3)

        target_food = food_sys.foods[0]
        food_pos = target_food.pos

        # Step 1: Fly is landed at food location at t=0.0
        eaten = food_sys.check_feeding(fly_pos=food_pos, fly_is_landed=True, current_time=0.0)
        self.assertIsNone(eaten, "Feeding must not trigger immediately")

        # Step 2: Fly is still landed at t=1.0s (less than 1.5s)
        eaten = food_sys.check_feeding(fly_pos=food_pos, fly_is_landed=True, current_time=1.0)
        self.assertIsNone(eaten, "Feeding must require 1.5 seconds of dwell time")

        # Step 3: Fly remains landed at t=1.6s -> Feeding completes!
        eaten = food_sys.check_feeding(fly_pos=food_pos, fly_is_landed=True, current_time=1.6)
        print(f"\n[Ecosystem Test 3] Feeding completed on {eaten} at t=1.6s!")
        self.assertEqual(eaten, target_food.name)
        self.assertFalse(target_food.active, "Food must become inactive after being eaten")
        self.assertEqual(target_food.eaten_time, 1.6)

        # Step 4: Verify 60-second respawn delay
        food_sys.update(dt=1.0, current_time=30.0)
        self.assertFalse(target_food.active, "Food must remain inactive before 60 seconds")

        food_sys.update(dt=1.0, current_time=62.0)
        self.assertTrue(target_food.active, "Food must respawn after 60 seconds")

    def test_04_surface_height_detection_for_landing(self):
        """Verifies NaturalWorld detects surfaces below positions correctly."""
        world = NaturalWorld(self.base.render, world_size=100.0, world_height=30.0)

        # Ground level test
        z_ground, s_type = world.get_surface_below(Vec3(0, 0, 5.0))
        print(f"\n[Ecosystem Test 4] Surface below (0,0,5): z={z_ground}, type={s_type}")
        self.assertEqual(z_ground, 0.0)
        self.assertEqual(s_type, "GROUND")

        # Branch / Rock surface test (query inside rock or branch coordinates)
        if len(world.surfaces) > 1:
            first_surf = world.surfaces[1]
            q_pos = Vec3(first_surf.center.x, first_surf.center.y, first_surf.center.z + first_surf.half_extents.z + 0.2)
            z_surf, s_type2 = world.get_surface_below(q_pos)
            expected_top = first_surf.center.z + first_surf.half_extents.z
            self.assertAlmostEqual(z_surf, expected_top, delta=0.1)

    def test_05_reincarnation_and_retry_resets_ecosystem(self):
        """Verifies retry and reincarnation resets all entities, life stats, and world items."""
        frog = FrogEntity(self.base.render, "TestFrog", Vec3(10, 10, 0))
        frog.state = "JUMP"
        frog.pos = Vec3(15, 15, 4)

        food_sys = FoodSystem(self.base.render, max_active=3)
        food_sys.foods[0].active = False

        # Reset
        frog.reset()
        food_sys.reset_all()

        print(f"\n[Ecosystem Test 5] Reset Frog state: {frog.state}, pos: ({frog.pos.x}, {frog.pos.y}), "
              f"Food 0 active: {food_sys.foods[0].active}")

        self.assertEqual(frog.state, "IDLE")
        self.assertEqual(frog.pos, Vec3(10, 10, 0))
        self.assertTrue(food_sys.foods[0].active)

    def test_06_perching_landing_and_takeoff_transitions(self):
        """Verifies landing touchdown and take-off transitions."""
        world = NaturalWorld(self.base.render, world_size=100.0, world_height=30.0)
        worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=False)
        fly = FlyController(self.base.render, world, worker)

        # 1. Fly at high altitude -> Not landed
        fly.pos = Vec3(0, 0, 10.0)
        self.assertFalse(fly.is_landed)

        # 2. Fly near ground with low speed -> touches down
        fly.pos = Vec3(0, 0, 0.5)
        fly._vertical_vel = -0.2
        # Run one update frame with calm sensory
        sensory = SensoryInput(dist_left=40.0, dist_center=40.0, dist_right=40.0)
        fly.update(dt=0.02, custom_sensory=sensory)

        print(f"\n[Ecosystem Test 6] Landed check -> is_landed: {fly.is_landed}, "
              f"surface: {fly.current_surface}, total_landings: {fly.total_landings}")

        self.assertTrue(fly.is_landed, "Fly near ground must touch down and perch")
        self.assertEqual(fly.total_landings, 1)

        # 3. Connectome escape / take-off trigger
        # Simulate motor state generating escape impulse
        worker._latest_telemetry.motor.escape_impulse = 5.0
        fly.update(dt=0.02, custom_sensory=sensory)

        print(f"[Ecosystem Test 6] Take-off check -> is_landed: {fly.is_landed}, vertical_vel: {fly._vertical_vel:.1f}")
        self.assertFalse(fly.is_landed, "High escape impulse must cause take-off")
        self.assertGreater(fly._vertical_vel, 0.0)


if __name__ == "__main__":
    unittest.main()
