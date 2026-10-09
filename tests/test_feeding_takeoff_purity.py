"""Test Feeding Physical Contact Overlap & Pure Neural Takeoff Invariants.

Verifies:
1. Feeding physical contact:
   - Requires food surface physical contact
   - Requires neural feeding/proboscis activity (PER)
   - Requires actual proboscis tip collider (sphere r=0.25m) overlapping the food 3D box collider
   - Spatial proximity alone or retracted proboscis NEVER allows feeding
2. Takeoff purity:
   - Generic forward speed alone NEVER launches the fly
   - Only validated neural circuits (DNp01 escape jump, DLMn/DVMn flight power) initiate takeoff
"""
import unittest
from panda3d.core import loadPrcFileData, Vec3
loadPrcFileData("", "window-type none")
loadPrcFileData("", "audio-library-name null")

from direct.showbase.ShowBase import ShowBase
from game.food_system import FoodSystem, FoodItem
from game.fly_controller import FlyController
from game.brain_worker import BrainWorker, BrainTelemetry
from game.motor_decoder import MotorState
from game.sensory_encoder import SensoryInput


class TestFeedingTakeoffPurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.base = ShowBase()
        except Exception:
            import builtins
            cls.base = getattr(builtins, "base", None)

    def test_feeding_requires_physical_proboscis_tip_overlap(self):
        food_sys = FoodSystem(self.base.render, max_active=1)
        apple = food_sys.foods[0]
        apple.name = "APPLE"
        apple.pos = Vec3(10.0, 10.0, 1.0)
        apple.size = (1.4, 1.4, 1.3)  # Half-extents: 0.7, 0.7, 0.65
        apple.active = True

        # Test Case 1: Fly is at distance 2.8m (old arbitrary radius), facing away, proboscis retracted
        fly_pos_far = Vec3(10.0, 7.2, 1.0)  # dist = 2.8m
        # Extended tip pos is at Y = 7.2 + 1.6 = 8.8 (still 1.2m away from apple at Y=10.0-0.7=9.3)
        res = food_sys.check_feeding(
            fly_pos=fly_pos_far,
            fly_is_landed=True,
            current_time=0.0,
            proboscis_tip_pos=Vec3(10.0, 8.2, 0.2), # 1.1m away from surface
            proboscis_extended=False,
            proboscis_extension=0.0
        )
        self.assertIsNone(res, "Retracted proboscis at 2.8m must NOT feed")

        # Test Case 2: Fly is adjacent to apple (pos = 10.0, 8.5, 0.5), landed, proboscis RETRACTED (tip at Y=8.8)
        # Apple box starts at Y = 10.0 - 0.7 = 9.3. Tip at 8.8 is 0.5m away (> 0.25m tip radius)
        res = food_sys.check_feeding(
            fly_pos=Vec3(10.0, 8.5, 0.5),
            fly_is_landed=True,
            current_time=0.0,
            proboscis_tip_pos=Vec3(10.0, 8.8, 0.3),
            proboscis_extended=False,
            proboscis_extension=0.0
        )
        self.assertIsNone(res, "Retracted proboscis must NOT feed even when adjacent")

        # Test Case 3: Fly is adjacent to apple, landed, proboscis EXTENDED touching apple surface (tip at Y=9.35, inside apple box)
        tip_touching = Vec3(10.0, 9.35, 0.6)  # Apple box is [9.3, 10.7], so tip touches surface
        food_sys.check_feeding(
            fly_pos=Vec3(10.0, 8.5, 0.5),
            fly_is_landed=True,
            current_time=0.0,
            proboscis_tip_pos=tip_touching,
            proboscis_extended=True,
            proboscis_extension=1.0
        )
        # Advance time by 1.3s while maintaining contact
        res_eaten = food_sys.check_feeding(
            fly_pos=Vec3(10.0, 8.5, 0.5),
            fly_is_landed=True,
            current_time=1.3,
            proboscis_tip_pos=tip_touching,
            proboscis_extended=True,
            proboscis_extension=1.0
        )
        self.assertEqual(res_eaten, "APPLE", "Extended proboscis tip touching food surface must complete feeding")

    def test_takeoff_purity_walking_never_launches(self):
        """Verifies that normal walking speed never automatically launches the fly."""
        class MockEnv:
            world_height = 30.0
            half_size = 50.0
            def raycast(self, pos, dir_vec, max_dist): return 20.0
            def get_surface_below(self, pos): return 0.0, "GROUND"

        class MockBrain:
            def __init__(self):
                self.telem = BrainTelemetry()
                self.telem.motor = MotorState()
            def get_telemetry(self): return self.telem
            def update_sensory(self, s): pass

        mock_brain = MockBrain()
        env = MockEnv()
        fly = FlyController(self.base.render, env, mock_brain)

        # Place fly on ground in GROUNDED mode
        fly.locomotion_mode = "GROUNDED"
        fly.pos = Vec3(0, 0, 0.3)

        # Set forward flight drive moderate (walking speed) with NO flight power and NO escape jump
        mock_brain.telem.motor.fwd_pop_hz = 2.0
        mock_brain.telem.motor.forward_speed = 4.8  # Even at former 4.8 threshold!
        mock_brain.telem.motor.flight_power_hz = 0.0
        mock_brain.telem.motor.esc_pop_hz = 0.0
        mock_brain.telem.motor.escape_impulse = 0.0

        sensory = SensoryInput(dist_center=20.0)

        # Update fly for multiple steps
        for _ in range(25):
            fly.update(0.04, custom_sensory=sensory)

        self.assertEqual(fly.locomotion_mode, "GROUNDED",
                         "Normal walking speed with zero flight power must NEVER trigger takeoff!")

        # Now activate DLMn/DVMn flight power motor neurons
        mock_brain.telem.motor.flight_power_hz = 4.5
        fly.update(0.04, custom_sensory=sensory)
        self.assertEqual(fly.locomotion_mode, "AIRBORNE",
                         "Flight power motor neuron activation (DLMn/DVMn) MUST initiate takeoff!")


if __name__ == "__main__":
    unittest.main()
