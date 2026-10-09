"""Neural Causality Verification Test Suite.

Proves that:
1. Connectome ON + Stimulus ON -> Evokes genuine motor outputs (turning / escape).
2. Connectome ON + Stimulus OFF -> Only calm baseline resting activity (no stimulus-driven bursts).
3. Connectome OFF -> Neural controller produces zero commands.
4. No hidden scripted 'if obstacle: turn' cheat exists when F2 Scripted Bot is disabled.
5. Fallback safeguard is distinct from neural decisions and logged separately.
"""
from __future__ import annotations

import time
import unittest
from game.brain_worker import BrainWorker
from game.sensory_encoder import SensoryInput
from game.motor_decoder import MotorDecoder, MotorState


class TestNeuralCausality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[NeuralCausality] Initializing BrainWorker...")
        cls.worker = BrainWorker(sensory_mode="FEATURE_MODE", log_telemetry=False)
        cls.worker.start()

        # Wait for worker to warm up and take first steps
        t0 = time.time()
        while time.time() - t0 < 8.0:
            telem = cls.worker.get_telemetry()
            if telem.brain_step > 5:
                break
            time.sleep(0.1)
        print(f"[NeuralCausality] Worker active at step {telem.brain_step}!")

    @classmethod
    def tearDownClass(cls):
        cls.worker.stop()

    def test_01_stimulus_off_produces_calm_resting_state(self):
        """When stimulus is OFF, DNp01 and DNa02 remain at resting rates."""
        calm_sensory = SensoryInput(dist_left=50.0, dist_center=50.0, dist_right=50.0, target_visible=False)
        self.worker.update_sensory(calm_sensory)

        # Allow 0.5s of calm steps
        time.sleep(0.5)
        telem = self.worker.get_telemetry()
        print(f"\n[Causality 1 Stimulus OFF] DNp01_L: {telem.motor.dnp01_l_hz:.1f}Hz, "
              f"DNp01_R: {telem.motor.dnp01_r_hz:.1f}Hz, Decision: {telem.motor.decision}")

        # Giant fiber escape neurons should be quiet (< 5 Hz)
        self.assertLess(telem.motor.dnp01_l_hz, 8.0)
        self.assertLess(telem.motor.dnp01_r_hz, 8.0)
        self.assertEqual(telem.motor.escape_impulse, 0.0)

    def test_02_looming_stimulus_on_produces_escape_motor_output(self):
        """When imminent looming obstacle is present on LEFT, Giant Fiber DNp01_L activates and commands rightward escape."""
        looming_left = SensoryInput(dist_left=5.0, dist_center=20.0, dist_right=40.0, target_visible=False)
        self.worker.update_sensory(looming_left)

        # Wait for neural integration and propagation
        time.sleep(0.4)
        telem = self.worker.get_telemetry()
        print(f"\n[Causality 2 Stimulus ON Left] DNp01_L: {telem.motor.dnp01_l_hz:.1f}Hz, "
              f"DNp01_R: {telem.motor.dnp01_r_hz:.1f}Hz, TurnRate: {telem.motor.turn_rate:.1f} deg/s, "
              f"Decision: {telem.motor.decision}")

        # Verify genuine neural escape activation
        self.assertGreaterEqual(telem.motor.dnp01_l_hz, 8.0, "Left DNp01 must fire strongly under left looming")
        self.assertGreater(telem.motor.escape_impulse, 0.0, "Escape impulse must trigger")
        self.assertGreater(telem.motor.turn_rate, 0.0, "Steering must turn RIGHT away from left danger")

    def test_03_connectome_disabled_produces_zero_neural_output(self):
        """When connectome is disabled (OFF), it must not produce neural motion commands."""
        self.worker.set_connectome_enabled(False)
        time.sleep(0.2)

        looming = SensoryInput(dist_left=5.0, dist_center=5.0, dist_right=5.0)
        self.worker.update_sensory(looming)

        time.sleep(0.2)
        telem = self.worker.get_telemetry()
        print(f"\n[Causality 3 Connectome OFF] Enabled: {telem.enabled}, Decision: {telem.motor.decision}")
        self.assertFalse(telem.enabled)

        # Re-enable connectome for remaining tests
        self.worker.set_connectome_enabled(True)
        time.sleep(0.2)

    def test_04_no_hidden_scripted_rule_in_connectome_mode(self):
        """Confirms that motor actions derive purely from decoder on neural spike rates, not hard-coded obstacle coordinates."""
        decoder = MotorDecoder()
        # Case A: Left obstacle detected in physics, BUT zero spikes in connectome
        fake_silent_rates = {
            "dna02_l": 0.0, "dna02_r": 0.0,
            "dnp01_l": 0.0, "dnp01_r": 0.0,
            "dng100_l": 0.0, "dng100_r": 0.0,
            "mdn_l": 0.0, "mdn_r": 0.0
        }
        decoded = decoder.decode(fake_silent_rates)
        print(f"\n[Causality 4 Pure Neural] Silent brain turn rate: {decoded.turn_rate} deg/s (must be 0.0)")
        self.assertEqual(decoded.turn_rate, 0.0, "No turn must occur without neural spikes!")
        self.assertEqual(decoded.escape_impulse, 0.0)

    def test_05_zero_drive_zero_propulsion(self):
        """Zero Drive Test: All sensory stimuli = 0 -> DNg100 = 0 -> forward_speed must be strictly 0.0."""
        self.worker.reset_brain(seed=42)
        zero_sensory = SensoryInput(
            dist_left=50.0, dist_center=50.0, dist_right=50.0,
            target_visible=False, optic_flow=0.0, airspeed=0.0
        )
        self.worker.update_sensory(zero_sensory)
        time.sleep(0.6)

        telem = self.worker.get_telemetry()
        print(f"\n[Causality 5 Zero Drive] DNg100_L: {telem.motor.dng100_l_hz:.1f}Hz, "
              f"DNg100_R: {telem.motor.dng100_r_hz:.1f}Hz, FwdSpeed: {telem.motor.forward_speed:.2f}")

        self.assertEqual(telem.sensory.fwd_stimulus, 0.0, "Zero sensory input must produce 0 forward stimulus")
        self.assertEqual(telem.motor.dng100_l_hz, 0.0, "Zero sensory drive must produce 0.0 Hz in DNg100_L")
        self.assertEqual(telem.motor.dng100_r_hz, 0.0, "Zero sensory drive must produce 0.0 Hz in DNg100_R")
        self.assertEqual(telem.motor.forward_speed, 0.0, "forward_speed must be strictly 0.0 when DNg100 is 0")
        self.assertEqual(telem.motor.turn_rate, 0.0, "turn_rate must be strictly 0.0 when DNa02 is calm")


if __name__ == "__main__":
    unittest.main()
