import unittest
import numpy as np
from pathlib import Path
from game.memory_system import MushroomBodyMemorySystem

class TestMemoryPlasticity(unittest.TestCase):
    def test_3factor_synaptic_potentiation(self):
        mem = MushroomBodyMemorySystem(
            kc_indices=np.arange(30, dtype=np.int32),
            mbon_indices=np.arange(6, dtype=np.int32),
            pam_indices=np.array([50], dtype=np.int32),
            ppl1_indices=np.array([60], dtype=np.int32),
            memory_path='memory/test_plast.npz'
        )
        active_kc = np.array([1, 2, 3], dtype=np.int32)
        mem.update_activity_trace(set(active_kc), dt=0.02)
        base_app, _ = mem.compute_learned_mbon_drive(active_kc)

        mem.apply_reinforcement(pam_reward=1.0)
        new_app, _ = mem.compute_learned_mbon_drive(active_kc)
        self.assertGreater(new_app, base_app)

        p = Path('memory/test_plast.npz')
        if p.exists(): p.unlink()

if __name__ == '__main__':
    unittest.main()