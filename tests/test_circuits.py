"""Empirical Neural Circuit Verification Test.

Tests that sensory inputs into projection neurons (LC4, LPLC2, LC10a)
evoke biologically consistent downstream motor responses in descending neurons
(DNp01 giant fiber, DNa02 steering) using the real MaleCNS connectome.
"""
from __future__ import annotations

import sys
import unittest
import numpy as np

from flybrain import FlyBrain


class TestConnectomeCircuits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[CircuitTest] Initializing FlyBrain connectome...")
        cls.brain = FlyBrain(seed=42)
        # JIT warmup
        for _ in range(10):
            cls.brain.step()

        # Identify sensory projection neurons
        cls.lc_l = cls.brain.cells(["LC4", "LPLC2"], side="L")
        cls.lc_r = cls.brain.cells(["LC4", "LPLC2"], side="R")
        cls.lc10a_l = cls.brain.cells(["LC10a"], side="L")
        cls.lc10a_r = cls.brain.cells(["LC10a"], side="R")

        # Identify descending command neurons
        cls.dnp01_l = cls.brain.cells(["DNp01"], side="L")
        cls.dnp01_r = cls.brain.cells(["DNp01"], side="R")
        cls.dna02_l = cls.brain.cells(["DNa02"], side="L")
        cls.dna02_r = cls.brain.cells(["DNa02"], side="R")
        cls.dng100_l = cls.brain.cells(["DNg100"], side="L")
        cls.dng100_r = cls.brain.cells(["DNg100"], side="R")
        cls.mdn_l = cls.brain.cells(["MDN"], side="L")
        cls.mdn_r = cls.brain.cells(["MDN"], side="R")

        print(f"[CircuitTest] Neurons loaded: LC4/LPLC2 (L:{len(cls.lc_l)}, R:{len(cls.lc_r)}) | "
              f"DNp01 (L:{len(cls.dnp01_l)}, R:{len(cls.dnp01_r)}) | "
              f"DNa02 (L:{len(cls.dna02_l)}, R:{len(cls.dna02_r)})")

    def _measure_rate(self, steps: int = 40, stim_cells: np.ndarray | None = None,
                      stim_strength: float = 0.8) -> dict[str, float]:
        """Runs the connectome for given steps and measures firing rate (Hz) of readouts."""
        counts = {
            "dnp01_l": 0, "dnp01_r": 0,
            "dna02_l": 0, "dna02_r": 0,
            "dng100_l": 0, "dng100_r": 0,
            "mdn_l": 0, "mdn_r": 0,
        }
        for _ in range(steps):
            if stim_cells is not None and len(stim_cells) > 0:
                self.brain.stimulate(stim_cells, stim_strength)
            fired = self.brain.step()
            counts["dnp01_l"] += int(np.sum(np.isin(self.dnp01_l, fired)))
            counts["dnp01_r"] += int(np.sum(np.isin(self.dnp01_r, fired)))
            counts["dna02_l"] += int(np.sum(np.isin(self.dna02_l, fired)))
            counts["dna02_r"] += int(np.sum(np.isin(self.dna02_r, fired)))
            counts["dng100_l"] += int(np.sum(np.isin(self.dng100_l, fired)))
            counts["dng100_r"] += int(np.sum(np.isin(self.dng100_r, fired)))
            counts["mdn_l"] += int(np.sum(np.isin(self.mdn_l, fired)))
            counts["mdn_r"] += int(np.sum(np.isin(self.mdn_r, fired)))

        duration = steps * self.brain.dt
        return {k: v / duration for k, v in counts.items()}

    def test_01_resting_baseline(self):
        """Verify baseline resting rates are calm without runaway hyperactivity."""
        self.brain.reset(101)
        for _ in range(20):
            self.brain.step()
        base = self._measure_rate(steps=40)
        print(f"\n[Test 1 Baseline] DNp01_L: {base['dnp01_l']:.1f}Hz, DNp01_R: {base['dnp01_r']:.1f}Hz, "
              f"DNa02_L: {base['dna02_l']:.1f}Hz, DNa02_R: {base['dna02_r']:.1f}Hz")
        # In resting state, giant fiber and steering command neurons should be calm (< 10 Hz)
        self.assertLess(base["dnp01_l"], 10.0)
        self.assertLess(base["dnp01_r"], 10.0)
        self.assertLess(base["dna02_l"], 10.0)
        self.assertLess(base["dna02_r"], 10.0)

    def test_02_looming_left_activates_left_giant_fiber(self):
        """Left looming stimulus (LC4/LPLC2) must evoke significant ipsilateral DNp01 elevation."""
        self.brain.reset(102)
        for _ in range(20):
            self.brain.step()
        base = self._measure_rate(steps=40)

        self.brain.reset(102)
        for _ in range(20):
            self.brain.step()
        stim = self._measure_rate(steps=40, stim_cells=self.lc_l, stim_strength=0.8)

        delta_l = stim["dnp01_l"] - base["dnp01_l"]
        delta_r = stim["dnp01_r"] - base["dnp01_r"]
        print(f"\n[Test 2 Looming Left] DNp01_L delta: {delta_l:+.1f}Hz (stim: {stim['dnp01_l']:.1f}Hz), "
              f"DNp01_R delta: {delta_r:+.1f}Hz (stim: {stim['dnp01_r']:.1f}Hz)")

        self.assertGreater(delta_l, 10.0, "Left DNp01 giant fiber must elevate by > 10 Hz on left looming")
        self.assertGreater(stim["dnp01_l"], stim["dnp01_r"], "Ipsilateral response must exceed contralateral")

    def test_03_looming_right_activates_right_giant_fiber(self):
        """Right looming stimulus (LC4/LPLC2) must evoke significant ipsilateral DNp01 elevation."""
        self.brain.reset(103)
        for _ in range(20):
            self.brain.step()
        base = self._measure_rate(steps=40)

        self.brain.reset(103)
        for _ in range(20):
            self.brain.step()
        stim = self._measure_rate(steps=40, stim_cells=self.lc_r, stim_strength=0.8)

        delta_l = stim["dnp01_l"] - base["dnp01_l"]
        delta_r = stim["dnp01_r"] - base["dnp01_r"]
        print(f"\n[Test 3 Looming Right] DNp01_R delta: {delta_r:+.1f}Hz (stim: {stim['dnp01_r']:.1f}Hz), "
              f"DNp01_L delta: {delta_l:+.1f}Hz (stim: {stim['dnp01_l']:.1f}Hz)")

        self.assertGreater(delta_r, 10.0, "Right DNp01 giant fiber must elevate by > 10 Hz on right looming")
        self.assertGreater(stim["dnp01_r"], stim["dnp01_l"], "Ipsilateral response must exceed contralateral")

    def test_04_target_tracking_activates_dna02_steering(self):
        """LC10a stimulation must elevate DNa02 steering response."""
        self.brain.reset(104)
        for _ in range(20):
            self.brain.step()
        base = self._measure_rate(steps=50)

        self.brain.reset(104)
        for _ in range(20):
            self.brain.step()
        stim = self._measure_rate(steps=50, stim_cells=self.lc10a_l, stim_strength=0.8)

        delta_l = stim["dna02_l"] - base["dna02_l"]
        print(f"\n[Test 4 Target Tracking Left] DNa02_L delta: {delta_l:+.1f}Hz (stim: {stim['dna02_l']:.1f}Hz vs base: {base['dna02_l']:.1f}Hz)")
        self.assertGreater(delta_l, 0.0, "DNa02_L must elevate upon LC10a_L stimulation")


if __name__ == "__main__":
    unittest.main()
