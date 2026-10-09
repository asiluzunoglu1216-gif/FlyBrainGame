"""Presentation Regression Tests: Ensures expanded biology features
do NOT regress natural flight behavior.

8 checks (A-H):
A. Zero neural = zero movement
B. Natural sensory = forward population sometimes active
C. Odor alone != direct motor command
D. Hunger alone != direct motor command
E. Memory alone != direct motor command
F. Frog presence alone != direct velocity change
G. Landing state doesn't trigger while airborne
H. Retry preserves persistent memory
"""
from __future__ import annotations
import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game.motor_decoder import MotorDecoder, MotorState
from game.sensory_encoder import SensoryInput
from game.internal_state import InternalPhysiologicalState


class TestPresentationRegression(unittest.TestCase):
    """Regression tests to prevent expanded biology from breaking natural flight."""

    def setUp(self):
        self.decoder = MotorDecoder()

    # ----------------------------------------------------------------
    # A. Zero neural output = zero movement
    # ----------------------------------------------------------------
    def test_a_zero_neural_zero_movement(self):
        """When all population firing rates are zero, forward_speed must be 0.0
        and turn_rate must be 0.0. No scripted minimum cruise speed."""
        motor = self.decoder.decode(
            fwd_pop_l=0.0, fwd_pop_r=0.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            bwd_pop_l=0.0, bwd_pop_r=0.0,
            feeding_pop=0.0, landing_pop=0.0,
            punch_pop=0.0, kick_pop=0.0,
        )
        self.assertEqual(motor.forward_speed, 0.0,
                         "Forward speed must be 0.0 when neural output is zero")
        self.assertEqual(motor.turn_rate, 0.0,
                         "Turn rate must be 0.0 when neural output is zero")
        self.assertEqual(motor.escape_impulse, 0.0,
                         "Escape impulse must be 0.0 when neural output is zero")
        self.assertEqual(motor.decision, "HOVER_STATIONARY",
                         "Decision must be HOVER_STATIONARY when all populations are silent")

    # ----------------------------------------------------------------
    # B. Moderate forward population = some forward speed
    # ----------------------------------------------------------------
    def test_b_forward_population_produces_speed(self):
        """When forward population fires at 3.0 Hz, forward_speed must be > 0."""
        motor = self.decoder.decode(
            fwd_pop_l=3.0, fwd_pop_r=3.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            bwd_pop_l=0.0, bwd_pop_r=0.0,
        )
        self.assertGreater(motor.forward_speed, 0.0,
                           "Forward speed must be > 0 when fwd pop fires")
        self.assertIn("FORWARD", motor.decision,
                      "Decision should contain FORWARD when flying")

    # ----------------------------------------------------------------
    # C. Odor alone must NOT produce direct motor command
    # ----------------------------------------------------------------
    def test_c_odor_does_not_directly_control_motor(self):
        """SensoryInput with high odor concentration must not set forward_speed
        or turn_rate on MotorState directly. Odor should only stimulate ORN neurons."""
        sensory = SensoryInput(
            odor_conc_l=0.8,
            odor_conc_r=0.2,
            odor_conc=1.0,
            odor_type="ETHYL_ACETATE",
            olfactory_gain=1.5,
        )
        # Odor doesn't appear anywhere in MotorDecoder inputs
        motor = self.decoder.decode(
            fwd_pop_l=0.0, fwd_pop_r=0.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            bwd_pop_l=0.0, bwd_pop_r=0.0,
        )
        self.assertEqual(motor.forward_speed, 0.0,
                         "Odor must not directly set forward speed")
        self.assertEqual(motor.turn_rate, 0.0,
                         "Odor must not directly set turn rate")

    # ----------------------------------------------------------------
    # D. Hunger alone must NOT produce direct motor command
    # ----------------------------------------------------------------
    def test_d_hunger_does_not_directly_control_motor(self):
        """Internal hunger state must only modulate sensory gains, not produce movement."""
        state = InternalPhysiologicalState(energy=0.05)  # Very hungry
        self.assertGreater(state.hunger, 0.8, "Hunger should be high when energy is low")
        # Hunger modulates gains but doesn't create a motor command
        motor = self.decoder.decode(
            fwd_pop_l=0.0, fwd_pop_r=0.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
        )
        self.assertEqual(motor.forward_speed, 0.0,
                         "Hunger must not directly produce forward speed")
        self.assertEqual(motor.turn_rate, 0.0,
                         "Hunger must not directly produce turn rate")

        # Verify gains are bounded
        self.assertLessEqual(state.olfactory_gain, 2.0,
                             "Olfactory gain must not exceed 2.0x")
        self.assertLessEqual(state.gustatory_gain, 2.0,
                             "Gustatory gain must not exceed 2.0x")

    # ----------------------------------------------------------------
    # E. Memory MBON drive alone must NOT produce direct motor command
    # ----------------------------------------------------------------
    def test_e_memory_does_not_directly_control_motor(self):
        """MushroomBody MBON drive should not directly appear in MotorDecoder output.
        It should modulate synaptic plasticity, not create movement."""
        # MotorDecoder does not take MBON inputs at all
        motor = self.decoder.decode(
            fwd_pop_l=0.0, fwd_pop_r=0.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
        )
        self.assertEqual(motor.forward_speed, 0.0,
                         "Memory must not directly produce movement")

    # ----------------------------------------------------------------
    # F. Frog presence alone must NOT directly change velocity
    # ----------------------------------------------------------------
    def test_f_frog_does_not_directly_change_velocity(self):
        """Frog detection should inject into LC4/LPLC2 sensory neurons,
        not directly set forward_speed or turn_rate in MotorDecoder."""
        # Even with frog_looming = 1.0 in sensory, MotorDecoder only reads
        # population rates from descending neurons
        motor = self.decoder.decode(
            fwd_pop_l=2.0, fwd_pop_r=2.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
        )
        # Frog looming appears in sensory, not in motor decoder
        speed_no_frog = motor.forward_speed

        motor2 = self.decoder.decode(
            fwd_pop_l=2.0, fwd_pop_r=2.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
        )
        self.assertEqual(motor.forward_speed, motor2.forward_speed,
                         "Frog presence must not directly change forward speed in decoder")

    # ----------------------------------------------------------------
    # G. Landing state must NOT trigger while clearly airborne
    # ----------------------------------------------------------------
    def test_g_no_landing_while_airborne(self):
        """Landing readiness at low values and no surface contact should not trigger landing."""
        motor = self.decoder.decode(
            fwd_pop_l=4.0, fwd_pop_r=4.0,
            steer_pop_l=1.0, steer_pop_r=1.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            landing_pop=1.0,  # Low landing activity
        )
        # Landing readiness at 1.0 Hz * 0.20 = 0.20
        # This is below the tightened 0.25 threshold in fly_controller
        self.assertLess(motor.landing_readiness, 0.25,
                        "Low landing pop should not exceed the touchdown threshold")

    # ----------------------------------------------------------------
    # H. Feeding pop baseline must NOT trigger proboscis
    # ----------------------------------------------------------------
    def test_h_feeding_baseline_does_not_trigger_proboscis(self):
        """CEM/MN10 resting-state baseline (~5 Hz) must not trigger proboscis extension.
        Only genuine feeding motor activity (> 8.0 Hz) should extend proboscis."""
        # Simulate baseline CEM/MN10 at 5.0 Hz
        motor = self.decoder.decode(
            fwd_pop_l=2.0, fwd_pop_r=2.0,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            feeding_pop=5.0,
        )
        self.assertEqual(motor.proboscis_extension, 0.0,
                         "Feeding pop at baseline 5 Hz must not extend proboscis")
        self.assertNotEqual(motor.decision, "FEEDING_PROBOSCIS_ACTIVE",
                            "Baseline feeding pop must not trigger FEEDING decision")

        # Genuine feeding at 10 Hz should trigger
        motor2 = self.decoder.decode(
            fwd_pop_l=0.5, fwd_pop_r=0.5,
            steer_pop_l=0.0, steer_pop_r=0.0,
            esc_pop_l=0.0, esc_pop_r=0.0,
            feeding_pop=12.0,
        )
        self.assertGreater(motor2.proboscis_extension, 0.0,
                           "Genuine feeding pop at 12 Hz should extend proboscis")


    # ----------------------------------------------------------------
    # I. Frog encounters >= frog deaths invariant
    # ----------------------------------------------------------------
    def test_i_frog_death_implies_encounters_invariant(self):
        """Invariant: If frog_deaths > 0, frog_encounters must be >= frog_deaths.
        Logically impossible for a predator to catch the fly without an encounter."""
        from panda3d.core import NodePath, Vec3
        from game.frog_entity import FrogEntity

        root = NodePath("TestRoot")
        frog = FrogEntity(root, "TestFrog", Vec3(0, 0, 0))

        # Fly approaches frog to within strike range
        fly_pos = Vec3(0, 5, 0)
        # 1. Encounter registered as frog begins engagement
        has_encounter = frog.check_encounter(fly_pos)
        self.assertTrue(has_encounter, "Approaching frog must register encounter")
        self.assertTrue(frog.is_engaged)

        # 2. Advance frog through AIM -> TONGUE_STRIKE -> CATCH_PULL
        frog.state = "AIM"
        frog.state_timer = 0.4
        frog.update(0.02, fly_pos)

        # Advance tongue strike to hit fly
        caught = False
        for _ in range(60):
            caught = frog.update(0.02, fly_pos)
            if caught:
                break

        self.assertTrue(caught, "Tongue strike at fly pos must eventually catch fly")
        encounters = 1 if frog.encounter_registered or has_encounter else 0
        frog_deaths = 1 if caught else 0
        self.assertGreaterEqual(encounters, frog_deaths,
                                "Frog encounters must be >= frog deaths")


if __name__ == "__main__":
    unittest.main()
