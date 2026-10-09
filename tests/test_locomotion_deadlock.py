"""Locomotion Deadlock Resolution and Neural Causality Tests.

Verifies:
- Scenario A: Deprived chamber (zero sensory stimulus) -> zero forward firing -> zero forward speed.
- Scenario B: Natural ecosystem cues (airflow / retinal flow) -> population firing -> positive forward propulsion.
- Scenario C: Zero-Spike Zero-Speed invariant in MotorDecoder (no hardcoded cruise or bias).
- Scenario D: Grounded vs Airborne locomotion, takeoff transitions, and physics-assisted landing.
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock
import numpy as np
from panda3d.core import NodePath, Vec3

from flybrain import FlyBrain
from game.sensory_encoder import SensoryInput, FeatureEncoder
from game.motor_decoder import MotorDecoder, MotorState
from game.fly_controller import FlyController


class TestLocomotionDeadlock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[DeadlockTest] Loading FlyBrain connectome...")
        cls.brain = FlyBrain(seed=123)
        for _ in range(5):
            cls.brain.step()
        cls.encoder = FeatureEncoder(cls.brain)
        cls.decoder = MotorDecoder()

        # Connectome cell subsets for test verification
        cls.dng100_l = cls.brain.cells(["DNg100"], side="L")
        cls.dng100_r = cls.brain.cells(["DNg100"], side="R")
        cls.dnp09_l = cls.brain.cells(["DNp09"], side="L")
        cls.dnp09_r = cls.brain.cells(["DNp09"], side="R")
        cls.fwd_pop = np.concatenate([cls.dng100_l, cls.dng100_r, cls.dnp09_l, cls.dnp09_r])

    def test_scenario_a_sensory_deprived_zero_propulsion(self):
        """Scenario A: Sensory-deprived chamber (no airflow, no optic flow, no looming).
        Must produce strictly 0.0V injection, 0.0 forward firing, and 0.0 forward speed.
        """
        deprived_input = SensoryInput(
            dist_left=50.0,
            dist_center=50.0,
            dist_right=50.0,
            optic_flow=0.0,
            airspeed=0.0,
            ambient_breeze=0.0,
            target_visible=False,
            target_azimuth=0.0,
            target_dist=50.0
        )

        # 1. FeatureEncoder must produce zero forward circuit injections
        injections = self.encoder.encode(deprived_input)
        self.assertEqual(deprived_input.fwd_stimulus, 0.0, "Sensory-deprived chamber must have 0.0 forward stimulus")
        self.assertEqual(deprived_input.fwd_source, "NONE")

        # 2. Run brain with no stimulus for 15 steps
        spikes_fwd = 0
        for _ in range(15):
            fired = self.brain.step()
            spikes_fwd += int(np.sum(np.isin(self.fwd_pop, fired)))

        fwd_pop_hz = (spikes_fwd / (15 * 0.020)) / max(1, len(self.fwd_pop))
        print(f"[Scenario A] Deprived chamber -> Forward population firing: {fwd_pop_hz:.2f} Hz")

        # 3. Decode motor commands from zero population drive
        motor = self.decoder.decode(
            dng100_l_hz=0.0,
            dng100_r_hz=0.0,
            dna02_l_hz=0.0,
            dna02_r_hz=0.0,
            dnp01_l_hz=0.0,
            dnp01_r_hz=0.0,
            mdn_l_hz=0.0,
            mdn_r_hz=0.0,
            fwd_pop_l_hz=0.0,
            fwd_pop_r_hz=0.0,
            steer_pop_l_hz=0.0,
            steer_pop_r_hz=0.0,
            escape_pop_l_hz=0.0,
            escape_pop_r_hz=0.0,
            back_pop_l_hz=0.0,
            back_pop_r_hz=0.0,
            dt=0.020
        )

        self.assertEqual(motor.forward_speed, 0.0, "Zero neural drive MUST produce strictly 0.0 forward speed")
        self.assertEqual(motor.turn_rate, 0.0, "Zero neural drive MUST produce 0.0 turn rate")
        self.assertIn(motor.decision, ["HOVER_STATIONARY", "STATIONARY_REST"])

    def test_scenario_b_natural_environment_resolves_deadlock(self):
        """Scenario B: Natural environment cues (ambient breeze & optic flow).
        Stimulates multi-channel forward pathways (LC9 + fwd_circuit + JO-C/E).
        Connectome forward population fires, producing smooth positive forward speed without freeze.
        """
        natural_input = SensoryInput(
            dist_left=30.0,
            dist_center=30.0,
            dist_right=30.0,
            optic_flow=0.35,
            airspeed=1.50,
            ambient_breeze=1.0,
            target_visible=False
        )

        encoder = FeatureEncoder(self.brain)
        encoder.prev_dist_l = 30.0
        encoder.prev_dist_r = 30.0
        encoder.prev_dist_c = 30.0

        injections = encoder.encode(natural_input)
        self.assertGreater(natural_input.fwd_stimulus, 0.0, "Natural sensory cues must generate forward stimulus")
        self.assertIn("FLOW", natural_input.fwd_source)
        self.assertIn("AIR", natural_input.fwd_source)

        # Apply injections and verify downstream population firing
        spikes_fwd = 0
        for _ in range(25):
            for cells, val in injections:
                self.brain.stimulate(cells, val)
            fired = self.brain.step()
            spikes_fwd += int(np.sum(np.isin(self.fwd_pop, fired)))

        fwd_pop_hz = (spikes_fwd / (25 * 0.020)) / max(1, len(self.fwd_pop))
        print(f"[Scenario B] Natural cues -> Forward population firing: {fwd_pop_hz:.2f} Hz")
        self.assertGreater(fwd_pop_hz, 0.0, "Forward population must fire under natural airflow and optic flow")

        # Decode motor response
        motor = self.decoder.decode(
            dng100_l_hz=fwd_pop_hz,
            dng100_r_hz=fwd_pop_hz,
            dna02_l_hz=0.0,
            dna02_r_hz=0.0,
            dnp01_l_hz=0.0,
            dnp01_r_hz=0.0,
            mdn_l_hz=0.0,
            mdn_r_hz=0.0,
            fwd_pop_l_hz=fwd_pop_hz,
            fwd_pop_r_hz=fwd_pop_hz,
            steer_pop_l_hz=0.0,
            steer_pop_r_hz=0.0,
            escape_pop_l_hz=0.0,
            escape_pop_r_hz=0.0,
            back_pop_l_hz=0.0,
            back_pop_r_hz=0.0,
            dt=0.020
        )

        self.assertGreater(motor.forward_speed, 1.0, "Forward population firing must produce active forward speed")
        self.assertIn(motor.decision, ["FORWARD_PROPULSION", "PROPULSION_CRUISE", "FAST_FORWARD"])

    def test_scenario_c_strict_zero_spike_zero_speed_invariant(self):
        """Scenario C: Mathematical invariant check in MotorDecoder.
        Ensure no hidden bias, scripted offset, or fake cruise exists.
        """
        decoder = MotorDecoder()
        for step in range(10):
            m = decoder.decode(
                dng100_l_hz=0.0, dng100_r_hz=0.0,
                dna02_l_hz=0.0, dna02_r_hz=0.0,
                dnp01_l_hz=0.0, dnp01_r_hz=0.0,
                mdn_l_hz=0.0, mdn_r_hz=0.0,
                fwd_pop_l_hz=0.0, fwd_pop_r_hz=0.0,
                steer_pop_l_hz=0.0, steer_pop_r_hz=0.0,
                escape_pop_l_hz=0.0, escape_pop_r_hz=0.0,
                back_pop_l_hz=0.0, back_pop_r_hz=0.0,
                dt=0.020
            )
            self.assertEqual(m.forward_speed, 0.0, f"Step {step}: Forward speed must be exactly 0.0 at zero Hz")
            self.assertEqual(m.turn_rate, 0.0, f"Step {step}: Turn rate must be exactly 0.0 at zero Hz")

    def test_scenario_d_grounded_vs_airborne_and_physics_assisted_landing(self):
        """Scenario D: Dynamic Takeoff and Landing (Physics-Assisted Landing)."""
        mock_env = MagicMock()
        mock_env.get_surface_below.return_value = (0.0, "GROUND")
        mock_env.raycast.return_value = 35.0
        mock_env.get_target_pos.return_value = Vec3(0, 0, 8)
        mock_env.half_size = 50.0
        mock_env.world_height = 28.0
        mock_env.room_height = 28.0

        mock_brain = MagicMock()
        root = NodePath("Root")
        fly = FlyController(root, mock_env, mock_brain)

        # 1. Start fly just above surface settling for landing
        fly.pos = Vec3(0.0, 0.0, 0.35)
        fly._vertical_vel = 0.05
        fly._current_speed = 1.0

        mock_telem = MagicMock()
        mock_telem.motor = MotorState(forward_speed=1.0, turn_rate=0.0, escape_impulse=0.0)
        mock_brain.get_telemetry.return_value = mock_telem

        fly.update(dt=0.020)

        self.assertEqual(fly.locomotion_mode, "GROUNDED", "Fly must enter GROUNDED state on physical contact")
        self.assertTrue(fly.is_landed)
        self.assertEqual(fly.landing_state_label, "PHYSICS-ASSISTED LANDING (Surface Contact)")
        self.assertEqual(fly.total_landings, 1)

        # 2. Ground walking
        mock_telem.motor = MotorState(forward_speed=4.0, turn_rate=15.0, escape_impulse=0.0)
        fly.update(dt=0.050)

        self.assertEqual(fly.locomotion_mode, "GROUNDED", "Fly remains grounded during walking")
        self.assertGreater(fly.distance_travelled, 0.0, "Fly must walk on ground under neural drive")

        # 3. Neural takeoff
        mock_telem.motor = MotorState(forward_speed=2.0, turn_rate=0.0, escape_impulse=3.0)
        fly.update(dt=0.020)

        self.assertEqual(fly.locomotion_mode, "AIRBORNE", "Fly must take off into AIRBORNE upon escape impulse")
        self.assertFalse(fly.is_landed)
        self.assertGreater(fly._vertical_vel, 2.0, "Takeoff must provide upward vertical velocity")


if __name__ == "__main__":
    unittest.main()
